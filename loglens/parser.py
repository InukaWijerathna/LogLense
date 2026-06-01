from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, Optional
import re

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
]

_LEVEL_NORMALIZE = {"WARNING": "WARN", "CRITICAL": "FATAL"}


def _parse_timestamp(raw: str) -> Optional[datetime]:
    raw = raw.strip()
    for fmt in _TIMESTAMP_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=None)  # normalize to naive
        except ValueError:
            continue
    return None


def parse_line(line: str) -> LogEntry:
    line = line.rstrip()

    for fmt_name, pattern in _PATTERNS:
        m = pattern.match(line)
        if not m:
            continue

        g = m.groupdict()
        ts = _parse_timestamp(g.get("timestamp") or "")
        raw_level = (g.get("level") or "").upper()
        level = _LEVEL_NORMALIZE.get(raw_level, raw_level) or None
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
