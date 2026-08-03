"""Filtering helpers for log level, pattern, and time-range queries."""

import re
from datetime import datetime
from typing import List, Optional, Union

from .parser import LEVEL_NORMALIZE, LogEntry

_LEVEL_ORDER = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3, "FATAL": 4}


def _normalize_level(level: str) -> str:
    return LEVEL_NORMALIZE.get(level.upper(), level.upper())


def compile_pattern(pattern: str) -> "re.Pattern[str]":
    """Compile *pattern* as a case-insensitive regex, falling back to a literal
    escaped match if it isn't valid regex syntax."""
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error:
        return re.compile(re.escape(pattern), re.IGNORECASE)


def filter_level(entries: List[LogEntry], level: Optional[Union[str, List[str]]]) -> List[LogEntry]:
    if not level:
        return entries
    if isinstance(level, str):
        targets = {_normalize_level(level)}
    else:
        targets = {_normalize_level(item) for item in level}
    return [e for e in entries if e.level in targets]


def filter_min_level(entries: List[LogEntry], min_level: Optional[str]) -> List[LogEntry]:
    if not min_level:
        return entries
    threshold = _LEVEL_ORDER.get(_normalize_level(min_level), 0)
    return [e for e in entries if _LEVEL_ORDER.get(e.level or "", -1) >= threshold]


def filter_pattern(entries: List[LogEntry], pattern: Optional[str]) -> List[LogEntry]:
    if not pattern:
        return entries
    regex = compile_pattern(pattern)
    return [e for e in entries if regex.search(e.raw)]


def filter_exclude(entries: List[LogEntry], pattern: Optional[str]) -> List[LogEntry]:
    if not pattern:
        return entries
    regex = compile_pattern(pattern)
    return [e for e in entries if not regex.search(e.raw)]


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
    level: Optional[Union[str, List[str]]] = None,
    min_level: Optional[str] = None,
    pattern: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    exclude: Optional[str] = None,
) -> List[LogEntry]:
    entries = filter_level(entries, level)
    if not level:
        entries = filter_min_level(entries, min_level)
    entries = filter_pattern(entries, pattern)
    entries = filter_exclude(entries, exclude)
    entries = filter_since(entries, since)
    entries = filter_until(entries, until)
    return entries
