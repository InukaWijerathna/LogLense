"""Detects common log formats and parses them into LogEntry objects."""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, Optional


@dataclass
class LogEntry:
    timestamp: Optional[datetime]
    level: Optional[str]
    source: Optional[str]
    message: str
    raw: str
    filepath: Optional[str] = field(default=None, compare=False)

# Ordered from most specific to most generic
_PATTERNS = [
    # Python logging: 2024-01-15 08:23:45,123 - source - LEVEL - message
    ("python", re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}(?:[,\.]\d+)?)"
        r"\s+-\s+(?P<source>\S+)\s+-\s+"
        r"(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)"
        r"\s+-\s+(?P<message>.+)$",
        re.IGNORECASE,
    )),
    # Nginx error: 2024/01/15 08:23:45 [error] 1234#0: message
    ("nginx_error", re.compile(
        r"^(?P<timestamp>\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})"
        r"\s+\[(?P<level>\w+)\]\s+\d+#\d+:\s+(?P<message>.+)$",
        re.IGNORECASE,
    )),
    # Apache CLF: 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /..." 200 2326
    ("apache", re.compile(
        r"^(?P<host>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]"
        r'\s+"(?P<request>[^"]+)"\s+(?P<status>\d+)\s+(?P<bytes>\S+)'
    )),
    # Bracket timestamp: [2024-01-15 08:23:45] LEVEL: message
    ("bracket", re.compile(
        r"^\[(?P<timestamp>[^\]]+)\]\s+"
        r"(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)"
        r"[\s:]+(?P<message>.+)$",
        re.IGNORECASE,
    )),
    # Syslog: Jan 15 08:23:45 myhost sshd[1234]: message
    ("syslog", re.compile(
        r"^(?P<timestamp>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
        r"\s+(?P<host>\S+)\s+"
        r"(?P<source>[^\s\[]+)(?:\[\d+\])?:\s+(?P<message>.+)$"
    )),
    # Bare level prefix: ERROR: message  or  ERROR message
    ("bare_level", re.compile(
        r"^(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)[\s:]+(?P<message>.+)$",
        re.IGNORECASE,
    )),
]

_TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S,%f",
    "%Y-%m-%dT%H:%M:%S,%f",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%d/%b/%Y:%H:%M:%S %z",
    "%d/%b/%Y:%H:%M:%S",
    "%b %d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%d %H:%M:%SZ"
]
_FORMATS_WITHOUT_YEAR = {"%b %d %H:%M:%S"}

LEVEL_NORMALIZE = {"WARNING": "WARN", "CRITICAL": "FATAL"}


def _parse_timestamp(raw: str) -> Optional[datetime]:
    raw = raw.strip()
    for fmt in _TIMESTAMP_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            if fmt in _FORMATS_WITHOUT_YEAR:
                dt = dt.replace(year=datetime.now().year)
            return dt.replace(tzinfo=None)  # normalize to naive
        except ValueError:
            continue
    return None


def _parse_json_log(data: dict, line: str) -> LogEntry:
    """Parse the json log and extract timestamps, level, messages and source"""
    raw_level = data.get("level") or data.get("lvl") or data.get("severity")

    if raw_level is not None:
        raw_level = str(raw_level).upper()
        normalized_level = LEVEL_NORMALIZE.get(raw_level, raw_level)
    else:
        normalized_level = None

    message = data.get("message")

    if message is None:
        message = data.get("msg")

    message = "" if message is None else str(message)

    raw_ts = data.get("timestamp") or data.get("time") or data.get("ts")
    if isinstance(raw_ts, str):
        parsed_ts = _parse_timestamp(raw_ts) if raw_ts else None
    else:
        parsed_ts = None

    source = data.get("source")

    if source is None:
        source = data.get("logger")

    if source is None:
        source = data.get("src")

    source = None if source is None else str(source)

    return LogEntry(timestamp=parsed_ts, level=normalized_level, message=message, source=source, raw=line)


def parse_line(line: str) -> LogEntry:
    line = line.rstrip()

    try:
        data = json.loads(line)
        if isinstance(data, dict):
            return _parse_json_log(data, line)
    except json.JSONDecodeError:
        pass
    for fmt_name, pattern in _PATTERNS:
        m = pattern.match(line)
        if not m:
            continue

        g = m.groupdict()
        ts = _parse_timestamp(g.get("timestamp") or "")
        raw_level = (g.get("level") or "").upper()
        level = LEVEL_NORMALIZE.get(raw_level, raw_level) or None
        source = g.get("source") or g.get("host") or None

        if fmt_name == "apache":
            status = int(g.get("status", 0))
            level = "ERROR" if status >= 500 else "WARN" if status >= 400 else "INFO"
            message = f'{g["request"]} → {status} ({g["bytes"]} bytes)'
        else:
            message = g.get("message", line)

        return LogEntry(timestamp=ts, level=level, source=source, message=message, raw=line)

    return LogEntry(timestamp=None, level=None, source=None, message=line, raw=line)


def parse_file(path: str) -> Iterator[LogEntry]:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.strip():
                entry = parse_line(line)
                entry.filepath = path
                yield entry
