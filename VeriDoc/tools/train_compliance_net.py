#!/usr/bin/env python3
"""
Train a lightweight rule-aware compliance model (ComplianceNet) on your labeled dataset
and export it to ONNX for fast CPU inference inside VeriDoc.

Dataset CSV schema (one row per image):
  path, format, face_small, face_large, eye_low, eye_high, tilt, yaw,
  mouth_open, eyes_closed, glare, red_eye, bg_off, bg_non_uniform, headwear, multi_face,
  face_height_ratio, eye_height_ratio, centering_offset, roll_deg, yaw_deg

Usage:
  python tools/train_compliance_net.py --data /path/to/dataset.csv --epochs 10 --out models/compliance_net.onnx
"""

import os
import sys
import argparse
from pathlib import Path
import random
from typing import List, Tuple

import numpy as np
import cv2

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
except Exception as e:
    print("ERROR: PyTorch is required for training. Install with pip install torch torchvision.")
    raise

# ---------------------
# Dataset
# ---------------------

LABEL_COLUMNS = [
    'face_small','face_large','eye_low','eye_high','tilt','yaw','mouth_open','eyes_closed',
    'glare','red_eye','bg_off','bg_non_uniform','headwear','multi_face'
]
REG_COLUMNS = ['face_height_ratio','eye_height_ratio','centering_offset','roll_deg','yaw_deg']

class ComplianceDataset(Dataset):
    def __init__(self, csv_path: str, image_size: int = 256):
        import pandas as pd
        self.df = pd.read_csv(csv_path)
        self.size = image_size

    def __len__(self):
        return len(self.df)

    def _augment(self, img: np.ndarray) -> np.ndarray:
        # Random flips
        if random.random() < 0.5:
            img = cv2.flip(img, 1)
        # Random brightness/gamma
        if random.random() < 0.5:
            g = random.uniform(0.8, 1.2)
            table = ((np.linspace(0, 1, 256) ** (1.0/g)) * 255).astype(np.uint8)
            img = cv2.LUT(img, table)
        # JPEG noise
        if random.random() < 0.3:
            _, buf = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), random.randint(60, 95)])
            img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return img

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        path = str(row['path'])
        img = cv2.imread(path)
        if img is None:
            img = np.zeros((self.size, self.size, 3), dtype=np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.size, self.size), interpolation=cv2.INTER_AREA)
        img = self._augment(img)
        x = (img.astype(np.float32) / 255.0).transpose(2, 0, 1)

        y_cls = np.array([row.get(c, 0) for c in LABEL_COLUMNS], dtype=np.float32)
        y_reg = np.array([row.get(c, 0.0) for c in REG_COLUMNS], dtype=np.float32)
        return torch.from_numpy(x), torch.from_numpy(y_cls), torch.from_numpy(y_reg)

# ---------------------
# Model
# ---------------------

class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, s: int = 1):
        super().__init__()
        self.dw = nn.Conv2d(in_ch, in_ch, 3, stride=s, padding=1, groups=in_ch, bias=False)
        self.pw = nn.Conv2d(in_ch, out_ch, 1, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)
        self.act = nn.SiLU(inplace=True)
    def forward(self, x):
        x = self.dw(x)
        x = self.pw(x)
        x = self.bn(x)
        return self.act(x)

class ComplianceNet(nn.Module):
    def __init__(self, num_labels: int, num_regs: int):
        super().__init__()
        ch = [16, 24, 40, 64, 96]
        self.stem = nn.Sequential(
            nn.Conv2d(3, ch[0], 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(ch[0]), nn.SiLU(inplace=True)
        )
        self.b1 = DepthwiseSeparableConv(ch[0], ch[1], s=2)
        self.b2 = DepthwiseSeparableConv(ch[1], ch[2], s=2)
        self.b3 = DepthwiseSeparableConv(ch[2], ch[3], s=2)
        self.b4 = DepthwiseSeparableConv(ch[3], ch[4], s=2)
        self.pool = nn.AdaptiveAvgPool2d(1)
        feat = ch[4]
        self.head_cls = nn.Sequential(nn.Linear(feat, feat), nn.SiLU(), nn.Linear(feat, num_labels))
        self.head_reg = nn.Sequential(nn.Linear(feat, feat), nn.SiLU(), nn.Linear(feat, num_regs))

    def forward(self, x):
        x = self.stem(x)
        x = self.b1(x); x = self.b2(x); x = self.b3(x); x = self.b4(x)
        x = self.pool(x).flatten(1)
        logits = self.head_cls(x)
        regs = self.head_reg(x)
        return logits, regs

# ---------------------
# Train
# ---------------------

def train(args):
    ds = ComplianceDataset(args.data, image_size=args.img)
    n = len(ds)
    idx = list(range(n))
    random.shuffle(idx)
    split = int(n * 0.9)
    tr_idx, va_idx = idx[:split], idx[split:]
    from torch.utils.data import Subset
    tr = Subset(ds, tr_idx); va = Subset(ds, va_idx)

    dl_tr = DataLoader(tr, batch_size=args.bs, shuffle=True, num_workers=2)
    dl_va = DataLoader(va, batch_size=args.bs, shuffle=False, num_workers=2)

    model = ComplianceNet(num_labels=len(LABEL_COLUMNS), num_regs=len(REG_COLUMNS))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    bce = nn.BCEWithLogitsLoss()
    l1 = nn.SmoothL1Loss()

    best_f1 = 0.0
    for epoch in range(args.epochs):
        model.train(); t_loss = 0.0
        for xb, yb_cls, yb_reg in dl_tr:
            xb, yb_cls, yb_reg = xb.to(device), yb_cls.to(device), yb_reg.to(device)
            opt.zero_grad()
            logits, regs = model(xb)
            loss = bce(logits, yb_cls) + 0.5 * l1(regs, yb_reg)
            loss.backward(); opt.step()
            t_loss += float(loss)
        # simple val
        model.eval(); tp=fp=fn=0; 
        with torch.no_grad():
            for xb, yb_cls, yb_reg in dl_va:
                xb, yb_cls = xb.to(device), yb_cls.to(device)
                logits, _ = model(xb)
                preds = (torch.sigmoid(logits) > 0.5).float()
                tp += (preds*yb_cls).sum().item()
                fp += ((preds==1)&(yb_cls==0)).sum().item()
                fn += ((preds==0)&(yb_cls==1)).sum().item()
        precision = tp/(tp+fp+1e-6); recall = tp/(tp+fn+1e-6)
        f1 = 2*precision*recall/(precision+recall+1e-6)
        print(f"Epoch {epoch+1}/{args.epochs} loss={t_loss/len(dl_tr):.4f} F1={f1:.3f}")
        if f1 > best_f1:
            best_f1 = f1
            # Export to ONNX
            dummy = torch.randn(1,3,args.img,args.img, device=device)
            onnx_path = Path(args.out)
            onnx_path.parent.mkdir(parents=True, exist_ok=True)
            torch.onnx.export(model, dummy, str(onnx_path), input_names=['image'], output_names=['logits','regs'],
                              opset_version=13, dynamic_axes={'image':{0:'batch'}, 'logits':{0:'batch'}, 'regs':{0:'batch'}})
            print(f"Saved best ONNX: {onnx_path}")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True, help='CSV with labeled data')
    ap.add_argument('--out', default='models/compliance_net.onnx', help='Output ONNX path')
    ap.add_argument('--epochs', type=int, default=10)
    ap.add_argument('--bs', type=int, default=32)
    ap.add_argument('--img', type=int, default=256)
    ap.add_argument('--lr', type=float, default=3e-4)
    args = ap.parse_args()
    sys.exit(train(args) or 0)


