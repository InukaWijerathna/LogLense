from datetime import datetime

import pytest

from loglens.parser import LogEntry, parse_line
from loglens.filters import (
    apply_filters,
    filter_level,
    filter_min_level,
    filter_pattern,
    filter_since,
    filter_until,
)


# ---------------------------------------------------------------------------
# parse_line
# ---------------------------------------------------------------------------

class TestParseLine:
    def test_python_format(self):
        line = "2024-01-15 08:10:15,448 - app.db - ERROR - Connection timeout"
        e = parse_line(line)
        assert e.level == "ERROR"
        assert e.source == "app.db"
        assert e.message == "Connection timeout"
        assert e.timestamp == datetime(2024, 1, 15, 8, 10, 15, 448000)

    def test_python_format_warn_normalised(self):
        line = "2024-01-15 09:00:00,000 - app - WARNING - something weird"
        e = parse_line(line)
        assert e.level == "WARN"

    def test_nginx_error_format(self):
        line = "2024/01/15 08:10:00 [error] 1234#0: connection refused"
        e = parse_line(line)
        assert e.level == "ERROR"
        assert e.message == "connection refused"

    def test_apache_clf_200(self):
        line = '127.0.0.1 - frank [15/Jan/2024:08:00:01 +0000] "GET /index.html HTTP/1.1" 200 1234'
        e = parse_line(line)
        assert e.level == "INFO"
        assert e.source == "127.0.0.1"

    def test_apache_clf_500(self):
        line = '10.0.0.1 - - [15/Jan/2024:09:00:00 +0000] "POST /api HTTP/1.1" 500 0'
        e = parse_line(line)
        assert e.level == "ERROR"

    def test_bare_level(self):
        line = "ERROR: disk full"
        e = parse_line(line)
        assert e.level == "ERROR"
        assert e.message == "disk full"

    def test_unparsed_line(self):
        line = "some random text without structure"
        e = parse_line(line)
        assert e.level is None
        assert e.message == line
        assert e.raw == line

    def test_fatal_normalised_from_critical(self):
        line = "2024-01-15 08:00:00,000 - app - CRITICAL - crash"
        e = parse_line(line)
        assert e.level == "FATAL"


# ---------------------------------------------------------------------------
# filters
# ---------------------------------------------------------------------------

def _entries(*levels: str) -> list[LogEntry]:
    return [
        LogEntry(
            timestamp=datetime(2024, 1, 15, 8, i, 0),
            level=lv,
            source="test",
            message=f"msg {lv}",
            raw=f"raw {lv}",
        )
        for i, lv in enumerate(levels)
    ]


class TestFilterLevel:
    def test_keeps_matching(self):
        entries = _entries("INFO", "ERROR", "WARN", "ERROR")
        assert len(filter_level(entries, "ERROR")) == 2

    def test_none_passthrough(self):
        entries = _entries("INFO", "ERROR")
        assert filter_level(entries, None) == entries

    def test_warning_alias(self):
        entries = _entries("WARN", "INFO")
        assert len(filter_level(entries, "WARNING")) == 1


class TestFilterMinLevel:
    def test_min_warn(self):
        entries = _entries("DEBUG", "INFO", "WARN", "ERROR", "FATAL")
        result = filter_min_level(entries, "WARN")
        assert {e.level for e in result} == {"WARN", "ERROR", "FATAL"}


class TestFilterPattern:
    def test_keyword_match(self):
        entries = _entries("INFO", "ERROR")
        entries[0].message = "timeout occurred"
        entries[0].raw = "2024-01-15 08:00:00 - app - INFO - timeout occurred"
        entries[1].message = "all good"
        entries[1].raw = "2024-01-15 08:01:00 - app - ERROR - all good"
        result = filter_pattern(entries, "timeout")
        assert len(result) == 1
        assert result[0].message == "timeout occurred"

    def test_regex_match(self):
        entries = _entries("ERROR", "ERROR")
        entries[0].raw = "connection refused to 10.0.0.1"
        entries[1].raw = "connection refused to 10.0.0.2"
        result = filter_pattern(entries, r"10\.0\.0\.\d+")
        assert len(result) == 2

    def test_case_insensitive(self):
        entries = _entries("INFO")
        entries[0].raw = "TimeOut"
        result = filter_pattern(entries, "timeout")
        assert len(result) == 1

    def test_no_pattern_passthrough(self):
        entries = _entries("INFO", "WARN")
        assert filter_pattern(entries, None) == entries


class TestTimeFilters:
    def _timed_entries(self) -> list[LogEntry]:
        return [
            LogEntry(datetime(2024, 1, 15, 8, 0), "INFO", "s", "early", "raw"),
            LogEntry(datetime(2024, 1, 15, 10, 0), "INFO", "s", "mid", "raw"),
            LogEntry(datetime(2024, 1, 15, 12, 0), "INFO", "s", "late", "raw"),
            LogEntry(None, "INFO", "s", "no-ts", "raw"),
        ]

    def test_since_excludes_early(self):
        result = filter_since(self._timed_entries(), datetime(2024, 1, 15, 9, 0))
        messages = [e.message for e in result]
        assert "early" not in messages
        assert "mid" in messages
        assert "late" in messages
        assert "no-ts" not in messages  # no timestamp entries dropped

    def test_until_excludes_late(self):
        result = filter_until(self._timed_entries(), datetime(2024, 1, 15, 11, 0))
        messages = [e.message for e in result]
        assert "late" not in messages
        assert "early" in messages


class TestApplyFilters:
    def test_combined_level_and_pattern(self):
        line1 = "2024-01-15 08:00:00,000 - app - ERROR - Connection timeout"
        line2 = "2024-01-15 08:01:00,000 - app - ERROR - Disk full"
        line3 = "2024-01-15 08:02:00,000 - app - INFO - Connection opened"
        entries = [parse_line(l) for l in [line1, line2, line3]]
        result = apply_filters(entries, level="ERROR", pattern="timeout")
        assert len(result) == 1
        assert "timeout" in result[0].message.lower()
