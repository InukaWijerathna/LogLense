# LogLens

> **A smart CLI log parser, filter, and watcher for developers.**  
> Like `grep` + `tail -f` + `awk` — but with a clean UI and zero config.

---

## Features

| Flag | What it does |
|---|---|
| `--level` | Filter by log level: `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL` |
| `--pattern` | Regex or keyword search across the full log line |
| `--since` / `--until` | Filter by time range |
| `--highlight` | Color-code pattern matches inline |
| `--export` | Save results to `.csv` or `.txt` |
| `watch` | Live tail mode — streams new lines in real time |
| `stats` | Summary: level breakdown, time range, top message patterns |

Supports **Python logging**, **Apache CLF**, **Nginx error**, and generic formats automatically.

---

## Install

```bash
pip install loglens
```

Or from source:

```bash
git clone https://github.com/yourname/loglens
cd loglens
pip install -e .
```

---

## Quick Start

```bash
# Ships with a sample log — try it immediately
loglens parse sample_logs/app.log

# Filter to errors only
loglens parse sample_logs/app.log --level ERROR

# Search with a regex
loglens parse sample_logs/app.log --pattern "timeout" --highlight

# Filter a time window
loglens parse sample_logs/app.log --since "2024-01-15 08:10" --until "2024-01-15 09:00"

# Export errors to CSV
loglens parse sample_logs/app.log --level ERROR --export errors.csv

# Watch a live log file (like tail -f, but filtered)
loglens watch app.log --level ERROR

# Show stats summary
loglens stats sample_logs/app.log
```

---

## Usage

### `parse` — filter and display

```
loglens parse LOGFILE [OPTIONS]

Options:
  -l, --level TEXT      Filter by level: DEBUG, INFO, WARN, ERROR, FATAL
  -p, --pattern TEXT    Regex or keyword search
  --since TEXT          Start time, e.g. "2024-01-01 08:00"
  --until TEXT          End time,   e.g. "2024-01-01 12:00"
  -e, --export FILE     Save results to .txt or .csv
  -H, --highlight       Highlight pattern matches in output
```

### `watch` — live tail

```
loglens watch LOGFILE [OPTIONS]

Options:
  -l, --level TEXT      Filter by level
  -p, --pattern TEXT    Filter by pattern
  -n, --lines INTEGER   Lines of history to show on start  [default: 10]
```

### `stats` — summary

```
loglens stats LOGFILE [OPTIONS]

Options:
  -p, --pattern TEXT    Scope stats to matching entries only
```

---

## Supported Log Formats

LogLens auto-detects the format — no config needed.

| Format | Example |
|---|---|
| Python logging | `2024-01-15 08:00:01,234 - app.db - ERROR - Connection timeout` |
| Nginx error | `2024/01/15 08:10:00 [error] 1234#0: connect() failed` |
| Apache CLF | `127.0.0.1 - frank [15/Jan/2024:08:00:01 +0000] "GET / HTTP/1.1" 200 1234` |
| Generic | `ERROR: disk full` |

---

## Dev Setup

```bash
pip install -e ".[dev]"
pytest
```

---

## Milestones

- [x] v0.1 — `parse` with `--level` and `--pattern`
- [x] v0.2 — `--since`/`--until` time filters + `stats` command
- [x] v0.3 — `watch` live tail mode
- [x] v0.4 — `--export` CSV/TXT + pip installable

---

## License

MIT
