import csv
import json
from datetime import datetime

from loglense.exporter import export, export_csv, export_json, export_txt
from loglense.parser import LogEntry


def _entry(**overrides) -> LogEntry:
    defaults = dict(
        timestamp=datetime(2024, 1, 15, 8, 23, 45),
        level="ERROR",
        source="app",
        message="boom",
        raw="raw line",
        filepath="app.log",
    )
    defaults.update(overrides)
    return LogEntry(**defaults)


def test_export_txt_writes_raw_lines(tmp_path):
    path = tmp_path / "out.txt"
    export_txt([_entry(raw="line one"), _entry(raw="line two")], str(path))
    assert path.read_text(encoding="utf-8").splitlines() == ["line one", "line two"]


def test_export_csv_writes_expected_columns(tmp_path):
    path = tmp_path / "out.csv"
    export_csv([_entry()], str(path))
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows == [
        {
            "timestamp": "2024-01-15T08:23:45",
            "level": "ERROR",
            "source": "app",
            "message": "boom",
            "file": "app.log",
        }
    ]


def test_export_csv_handles_missing_timestamp(tmp_path):
    path = tmp_path / "out.csv"
    export_csv([_entry(timestamp=None)], str(path))
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["timestamp"] == ""


def test_export_json_round_trips(tmp_path):
    path = tmp_path / "out.json"
    export_json([_entry()], str(path))
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == [
        {
            "timestamp": "2024-01-15T08:23:45",
            "level": "ERROR",
            "source": "app",
            "message": "boom",
            "file": "app.log",
        }
    ]


def test_export_dispatches_by_extension(tmp_path):
    entries = [_entry()]
    export(entries, str(tmp_path / "a.csv"))
    export(entries, str(tmp_path / "b.json"))
    export(entries, str(tmp_path / "c.txt"))
    export(entries, str(tmp_path / "d.unknown"))

    assert (tmp_path / "a.csv").exists()
    assert (tmp_path / "b.json").exists()
    assert (tmp_path / "c.txt").exists()
    # unrecognized extensions fall back to plain text
    assert (tmp_path / "d.unknown").read_text(encoding="utf-8") == "raw line\n"
