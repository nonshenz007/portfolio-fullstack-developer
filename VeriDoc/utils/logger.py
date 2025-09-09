"""
Very small CSV/activity logger used by various components. No external deps.
"""

from __future__ import annotations

import csv
import os
from typing import Any, List


class LogLevel:
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


_GLOBAL_LOGGER: "Logger" | None = None


def get_logger(csv_path: str | None = None) -> "Logger":
    global _GLOBAL_LOGGER
    if _GLOBAL_LOGGER is None:
        _GLOBAL_LOGGER = Logger(csv_path)
    return _GLOBAL_LOGGER


class Logger:
    def __init__(self, csv_path: str | None = None, max_size_mb: float = 10.0, max_backup_files: int = 5) -> None:
        self.csv_path = csv_path or os.path.join("logs", "veridoc_export_log.csv")
        self.max_size_mb = float(max_size_mb)
        self.max_backup_files = int(max_backup_files)
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        # Ensure file has headers
        if not os.path.exists(self.csv_path):
            self._write_header()

    def log_activity(self, level: str, operation: str, *args: Any, **details: Any) -> None:
        # Support optional positional file_name as 3rd argument for legacy calls
        if len(args) > 0 and 'file_name' not in details:
            details['file_name'] = args[0]
        row = {
            "timestamp": self._timestamp(),
            "level": level,
            "operation": operation,
            "file_name": details.pop("file_name", ""),
            "format": details.pop("format_type", details.pop("format", "")),
            "validation_results": details.pop("validation_results", ""),
            "export_status": details.pop("export_status", ""),
            "processing_time": details.pop("processing_time", ""),
            "error_message": details.pop("error_message", ""),
            "details": str(details) if details else "",
        }
        self._append_csv(row)

    def log_error(self, operation: str, file_name: str = "", error_message: str = "", details: Any | None = None) -> None:
        payload = {"file_name": file_name, "error_message": error_message}
        if details is not None:
            payload["details"] = details
        self.log_activity(LogLevel.ERROR, operation, **payload)

    def log_processing_start(self, file_name: str, format_type: str) -> None:
        self.log_activity(LogLevel.INFO, "PROCESSING_START", file_name=file_name, format_type=format_type)

    def log_processing_complete(self, file_name: str, format_type: str, validation_results: str | None = None,
                                export_status: str = "SUCCESS", processing_time: float = 0.0) -> None:
        self.log_activity(
            LogLevel.INFO,
            "PROCESSING_COMPLETE",
            file_name=file_name,
            format_type=format_type,
            validation_results=validation_results or "",
            export_status=export_status,
            processing_time=processing_time,
        )

    def log_export(self, file_name: str, format_type: str, export_path: str, success: bool) -> None:
        self.log_activity(LogLevel.INFO, "EXPORT", file_name=file_name, format_type=format_type,
                          export_path=export_path, success=success)

    # CSV handling
    def _append_csv(self, row: dict) -> None:
        try:
            write_header = not os.path.exists(self.csv_path) or os.path.getsize(self.csv_path) == 0
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=self._headers())
                if write_header:
                    w.writeheader()
                w.writerow(row)
            self._maybe_rotate()
        except Exception:
            pass

    def _headers(self) -> List[str]:
        return [
            "timestamp",
            "level",
            "operation",
            "file_name",
            "format",
            "validation_results",
            "export_status",
            "processing_time",
            "error_message",
            "details",
        ]

    def _write_header(self) -> None:
        try:
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=self._headers())
                w.writeheader()
        except Exception:
            pass

    def _timestamp(self) -> str:
        import datetime as _dt
        return _dt.datetime.now().isoformat()

    def _maybe_rotate(self) -> None:
        """Rotate the CSV when it exceeds max_size_mb, keeping numbered backups."""
        try:
            size_mb = os.path.getsize(self.csv_path) / (1024.0 * 1024.0)
            if size_mb <= self.max_size_mb:
                return
            from pathlib import Path
            p = Path(self.csv_path)
            base = p.with_suffix('')  # strip .csv
            # Rotate: shift backups
            for i in range(self.max_backup_files, 0, -1):
                src = base.with_suffix(f'.{i}.csv')
                dst = base.with_suffix(f'.{i+1}.csv')
                if os.path.exists(src):
                    if i == self.max_backup_files:
                        os.remove(str(src))
                    else:
                        os.replace(str(src), str(dst))
            # Move current to .1 and create new with header
            os.replace(self.csv_path, str(base.with_suffix('.1.csv')))
            self._write_header()
        except Exception:
            pass

    # Convenience helpers used by tests
    def log_validation_result(self, file_name: str, format_type: str, results: str, passed: bool) -> None:
        self.log_activity(LogLevel.INFO, "VALIDATION", file_name=file_name, format_type=format_type,
                          validation_results=results, export_status="PASS" if passed else "FAIL")

    def get_recent_logs(self, count: int = 10) -> list[dict]:
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                return reader[-count:]
        except Exception:
            return []

    def clear_logs(self) -> bool:
        try:
            self._write_header()
            # Remove backups
            for i in range(1, self.max_backup_files + 1):
                p = f"{self.csv_path}.{i}.csv"
                if os.path.exists(p):
                    os.remove(p)
            return True
        except Exception:
            return False


