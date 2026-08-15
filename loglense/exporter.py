"""Exports parsed log entries to plain text, CSV, or JSON files."""

import csv
import json
from typing import List

from .parser import LogEntry


def entry_to_dict(entry: LogEntry) -> dict:
    return {
        "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
        "level": entry.level,
        "source": entry.source,
        "message": entry.message,
        "file": entry.filepath,
    }


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
    data = [entry_to_dict(e) for e in entries]

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def export_markdown(entries: List[LogEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("| Timestamp | Level | Source | Message | File |\n")
        fh.write("|-----------|-------|--------|---------|------|\n")

        for e in entries:
            message = e.message.replace("|", "\\|")

            fh.write(
                f"| "
                f"{e.timestamp.isoformat() if e.timestamp else ''} | "
                f"{e.level or ''} | "
                f"{e.source or ''} | "
                f"{message} | "
                f"{e.filepath or ''} |\n"
            )


def export(entries: List[LogEntry], path: str) -> None:
    if path.lower().endswith(".csv"):
        export_csv(entries, path)
    elif path.lower().endswith(".json"):
        export_json(entries, path)
    elif path.lower().endswith(".md"):
        export_markdown(entries, path)
    else:
        export_txt(entries, path)
