import csv
import json
from typing import List

from .parser import LogEntry


def export_txt(entries: List[LogEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(entry.raw + "\n")


def export_csv(entries: List[LogEntry], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["timestamp", "level", "source", "message", "file"])
        writer.writeheader()
        for e in entries:
            writer.writerow({
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
                "level": e.level or "",
                "source": e.source or "",
                "message": e.message,
                "file": e.filepath or "",
            })


def export_json(entries: List[LogEntry], path: str) -> None:
    data = [
        {
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "level": e.level,
            "source": e.source,
            "message": e.message,
            "file": e.filepath,
        }
        for e in entries
    ]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def export(entries: List[LogEntry], path: str) -> None:
    if path.lower().endswith(".csv"):
        export_csv(entries, path)
    elif path.lower().endswith(".json"):
        export_json(entries, path)
    else:
        export_txt(entries, path)
