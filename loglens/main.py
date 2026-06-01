from __future__ import annotations

import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows (CP1252 terminals can't render Rich's box chars)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .exporter import export
from .filters import apply_filters, filter_level, filter_pattern
from .parser import LogEntry, parse_file, parse_line

app = typer.Typer(
    name="loglens",
    help="[bold cyan]LogLens[/bold cyan] — smart CLI log parser, filter, and watcher.",
    rich_markup_mode="rich",
    add_completion=False,
)
console = Console(legacy_windows=False)

LEVEL_STYLES: dict[str, str] = {
    "DEBUG": "dim cyan",
    "INFO": "green",
    "WARN": "yellow",
    "ERROR": "bold red",
    "FATAL": "bold white on red",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise typer.BadParameter(f"Cannot parse date '{value}'. Try: YYYY-MM-DD HH:MM:SS")


def _level_text(level: Optional[str]) -> Text:
    if not level:
        return Text("-", style="dim")
    return Text(f"{level:<7}", style=LEVEL_STYLES.get(level, "white"))


def _highlight(text: str, regex: Optional[re.Pattern]) -> Text:  # type: ignore[type-arg]
    if not regex:
        return Text(text)
    result = Text()
    last = 0
    for m in regex.finditer(text):
        result.append(text[last : m.start()])
        result.append(m.group(), style="bold yellow on dark_orange3")
        last = m.end()
    result.append(text[last:])
    return result


def _build_regex(pattern: Optional[str]) -> Optional[re.Pattern]:  # type: ignore[type-arg]
    if not pattern:
        return None
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error:
        return re.compile(re.escape(pattern), re.IGNORECASE)


def _display_entries(entries: list[LogEntry], regex: Optional[re.Pattern] = None) -> None:  # type: ignore[type-arg]
    if not entries:
        console.print("[dim]No matching log entries found.[/dim]")
        return

    table = Table(show_header=True, header_style="bold magenta", expand=True, box=None)
    table.add_column("Timestamp", style="dim", min_width=19, no_wrap=True)
    table.add_column("Level", min_width=7, no_wrap=True)
    table.add_column("Source", style="cyan", min_width=12, max_width=20, no_wrap=True)
    table.add_column("Message")

    for e in entries:
        ts = e.timestamp.strftime("%Y-%m-%d %H:%M:%S") if e.timestamp else "-"
        table.add_row(ts, _level_text(e.level), e.source or "-", _highlight(e.message, regex))

    console.print(table)
    console.print(f"\n[dim]{len(entries)} entr{'y' if len(entries) == 1 else 'ies'} matched[/dim]")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@app.command()
def parse(
    logfile: Path = typer.Argument(..., help="Path to log file", exists=True, readable=True),
    level: Optional[str] = typer.Option(None, "--level", "-l", help="Filter by level: DEBUG, INFO, WARN, ERROR, FATAL"),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="Regex or keyword search"),
    since: Optional[str] = typer.Option(None, "--since", help='Include entries from this time, e.g. "2024-01-01 08:00"'),
    until: Optional[str] = typer.Option(None, "--until", help='Include entries up to this time, e.g. "2024-01-01 12:00"'),
    export_path: Optional[Path] = typer.Option(None, "--export", "-e", metavar="FILE", help="Save results to .txt or .csv"),
    highlight: bool = typer.Option(False, "--highlight", "-H", help="Highlight pattern matches in output"),
) -> None:
    """Parse and filter a log file with optional level, pattern, and time filters."""
    since_dt = _parse_dt(since)
    until_dt = _parse_dt(until)
    regex = _build_regex(pattern) if highlight else None

    entries = apply_filters(
        list(parse_file(str(logfile))),
        level=level,
        pattern=pattern,
        since=since_dt,
        until=until_dt,
    )

    _display_entries(entries, regex=regex)

    if export_path:
        export(entries, str(export_path))
        console.print(f"\n[green]Exported {len(entries)} entries → {export_path}[/green]")


@app.command()
def watch(
    logfile: Path = typer.Argument(..., help="Log file to watch", exists=True, readable=True),
    level: Optional[str] = typer.Option(None, "--level", "-l", help="Filter by level"),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="Regex or keyword search"),
    lines: int = typer.Option(10, "--lines", "-n", help="Lines of existing content to show on start"),
) -> None:
    """Watch a live log file and stream new entries (like tail -f, but smarter)."""
    console.print(
        f"[bold]Watching[/bold] [cyan]{logfile}[/cyan] "
        f"[dim]— Ctrl+C to stop[/dim]\n"
    )

    regex = _build_regex(pattern)

    def on_line(raw: str) -> None:
        entry = parse_line(raw)
        filtered = [entry]
        if level:
            filtered = filter_level(filtered, level)
        if pattern:
            filtered = filter_pattern(filtered, pattern)
        if not filtered:
            return

        e = filtered[0]
        ts = e.timestamp.strftime("%H:%M:%S") if e.timestamp else "--:--:--"
        lv_style = LEVEL_STYLES.get(e.level or "", "white")
        lv = f"{e.level or '?':<7}"
        msg = _highlight(e.message, regex)

        line_text = Text()
        line_text.append(f"{ts} ", style="dim")
        line_text.append(lv, style=lv_style)
        line_text.append(" ")
        line_text.append_text(msg)
        console.print(line_text)

    from .watcher import watch_file
    watch_file(str(logfile), on_line, tail_lines=lines)


@app.command()
def stats(
    logfile: Path = typer.Argument(..., help="Path to log file", exists=True, readable=True),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="Scope stats to entries matching this pattern"),
) -> None:
    """Show a summary of log levels, time range, and top message patterns."""
    entries = list(parse_file(str(logfile)))
    if pattern:
        entries = filter_pattern(entries, pattern)

    total = len(entries)
    timestamps = [e.timestamp for e in entries if e.timestamp]
    level_counts: Counter[str] = Counter(e.level or "UNKNOWN" for e in entries)

    console.print(f"\n[bold magenta]LogLens Stats — {logfile.name}[/bold magenta]")
    console.rule()
    console.print(f"  [dim]Total entries  [/dim] [bold]{total}[/bold]")
    if timestamps:
        console.print(f"  [dim]First entry    [/dim] {min(timestamps).strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"  [dim]Last entry     [/dim] {max(timestamps).strftime('%Y-%m-%d %H:%M:%S')}")
    console.print()

    # Level breakdown
    level_table = Table(title="Level Breakdown", header_style="bold", box=None, padding=(0, 2))
    level_table.add_column("Level", min_width=8)
    level_table.add_column("Count", justify="right", min_width=6)
    level_table.add_column("Bar", min_width=30)

    for lv in ("DEBUG", "INFO", "WARN", "ERROR", "FATAL", "UNKNOWN"):
        count = level_counts.get(lv, 0)
        if count == 0:
            continue
        pct = count / total * 100
        filled = round(pct / 100 * 30)
        bar = "#" * filled + "-" * (30 - filled)
        style = LEVEL_STYLES.get(lv, "white")
        level_table.add_row(
            Text(lv, style=style),
            str(count),
            f"[{style}]{bar}[/{style}] {pct:.1f}%",
        )
    console.print(level_table)

    # Top message patterns
    msg_counter: Counter[str] = Counter(
        (e.message or "")[:70].strip() for e in entries if e.message
    )
    top = msg_counter.most_common(10)
    if top:
        console.print()
        pat_table = Table(title="Top Message Patterns", header_style="bold", box=None, padding=(0, 2))
        pat_table.add_column("Count", justify="right", min_width=5)
        pat_table.add_column("Message")
        for msg, cnt in top:
            pat_table.add_row(str(cnt), Text(msg, overflow="fold"))
        console.print(pat_table)

    console.print()


def main() -> None:
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    app()


if __name__ == "__main__":
    main()
