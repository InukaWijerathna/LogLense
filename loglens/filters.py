from datetime import datetime
from typing import List, Optional
import re

from .parser import LogEntry

_LEVEL_ORDER = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3, "FATAL": 4}
_NORMALIZE = {"WARNING": "WARN", "CRITICAL": "FATAL"}


def _normalize_level(level: str) -> str:
    return _NORMALIZE.get(level.upper(), level.upper())


def filter_level(entries: List[LogEntry], level: Optional[str]) -> List[LogEntry]:
    if not level:
        return entries
    target = _normalize_level(level)
    return [e for e in entries if e.level == target]


def filter_min_level(entries: List[LogEntry], min_level: Optional[str]) -> List[LogEntry]:
    if not min_level:
        return entries
    threshold = _LEVEL_ORDER.get(_normalize_level(min_level), 0)
    return [e for e in entries if _LEVEL_ORDER.get(e.level or "", -1) >= threshold]


def filter_pattern(entries: List[LogEntry], pattern: Optional[str]) -> List[LogEntry]:
    if not pattern:
        return entries
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        regex = re.compile(re.escape(pattern), re.IGNORECASE)
    return [e for e in entries if regex.search(e.raw)]


def filter_since(entries: List[LogEntry], since: Optional[datetime]) -> List[LogEntry]:
    if not since:
        return entries
    return [e for e in entries if e.timestamp and e.timestamp >= since]


def filter_until(entries: List[LogEntry], until: Optional[datetime]) -> List[LogEntry]:
    if not until:
        return entries
    return [e for e in entries if e.timestamp and e.timestamp <= until]


def apply_filters(
    entries: List[LogEntry],
    level: Optional[str] = None,
    pattern: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> List[LogEntry]:
    entries = filter_level(entries, level)
    entries = filter_pattern(entries, pattern)
    entries = filter_since(entries, since)
    entries = filter_until(entries, until)
    return entries
