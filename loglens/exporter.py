import csv
from typing import List

from .parser import LogEntry


def export_txt(entries: List[LogEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(entry.raw + "\n")


def export_csv(entries: List[LogEntry], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["timestamp", "level", "source", "message"])
        writer.writeheader()
        for e in entries:
            writer.writerow({
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
                "level": e.level or "",
                "source": e.source or "",
                "message": e.message,
            })


def export(entries: List[LogEntry], path: str) -> None:
    if path.lower().endswith(".csv"):
        export_csv(entries, path)
    else:
        export_txt(entries, path)
