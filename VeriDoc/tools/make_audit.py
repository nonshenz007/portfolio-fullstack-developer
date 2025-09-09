#!/usr/bin/env python3
"""
Run stress batches in three modes (baseline, no-AI, core) and aggregate into a single audit.json.

Usage:
  python tools/make_audit.py --input tests --format ICS-UAE --out export/audit_run
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from statistics import mean


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def load_summary(path: Path) -> list[dict]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def summarize(items: list[dict]) -> dict:
    total = len(items)
    success = sum(1 for i in items if i.get("success"))
    passes = sum(1 for i in items if i.get("overall_pass"))
    times = [i.get("processing_time", 0.0) for i in items]
    avg_time = round(mean(times), 3) if times else 0.0
    # reasons
    from collections import Counter
    c = Counter()
    for i in items:
        for r in (i.get("reasons") or []):
            c[r] += 1
    return {
        "total": total,
        "success": success,
        "overall_pass": passes,
        "avg_time_s": avg_time,
        "top_reasons": c.most_common(10),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--format", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rules", default="config/icao_rules.json")
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    runs = {
        "baseline": out_root / "stress_baseline",
        "no_ai": out_root / "stress_noai",
        "core": out_root / "stress_core",
    }

    # Run three modes
    run(["python", "tools/validate_cli.py", "--input", args.input, "--format", args.format, "--out", str(runs["baseline"])])
    run(["python", "tools/validate_cli.py", "--input", args.input, "--format", args.format, "--out", str(runs["no_ai"]), "--no-ai"])
    run(["python", "tools/validate_cli.py", "--input", args.input, "--format", args.format, "--out", str(runs["core"]), "--core", "--rules", args.rules])

    # Aggregate
    audit = {}
    for key, path in runs.items():
        items = load_summary(path / "summary.json")
        audit[key] = summarize(items)

    (out_root / "audit.json").write_text(json.dumps(audit, indent=2))
    print("Wrote:", out_root / "audit.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


