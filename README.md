# LogLens

**A smart CLI log parser, filter, and watcher for developers.**  
Like `grep` + `tail -f` — but with structured output, time filters, and a clean UI.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-0.5.0-informational)

---

## Why LogLens?

Plain `grep` gives you raw lines. LogLens gives you **structured results** — parsed timestamps, color-coded levels, exportable tables, and live streaming — across any log format with zero config.

```
 Timestamp            Level    Source        Message
 2024-01-15 08:10:15  ERROR    app.db        Connection timeout after 30s: host=db-replica-1.internal
 2024-01-15 08:12:31  ERROR    app.auth      Brute-force detected: 5 failed logins — blocking IP 203.0.113.42
 2024-01-15 08:19:45  ERROR    app.api       POST /api/payments 503 — payment gateway timeout (15s)
 2024-01-15 08:24:11  ERROR    app.db        Deadlock detected on table=cart_items — rolling back

 13 entries matched
```

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

> Ships with `sample_logs/app.log` so you can try every command immediately — no log file needed.

---

## Quick Start

```bash
# Parse and display all entries
loglens parse sample_logs/app.log

# Parse multiple files at once
loglens parse app.log worker.log nginx.log --level ERROR

# Search with a regex or keyword
loglens parse sample_logs/app.log --pattern "timeout" --highlight

# Filter by time window
loglens parse sample_logs/app.log --since "2024-01-15 08:10" --until "2024-01-15 09:00"

# Export to CSV or JSON
loglens parse sample_logs/app.log --level ERROR --export errors.csv
loglens parse sample_logs/app.log --level ERROR --export errors.json

# Live tail — stream new lines as they arrive
loglens watch app.log --level ERROR

# Summary stats (one or more files)
loglens stats sample_logs/app.log
loglens stats app.log worker.log
```

---

## Commands

### `parse` — filter and display

Accepts one or more files. When multiple files are given, a **File** column is added to the output so you always know which file each entry came from.

```
loglens parse LOGFILE [LOGFILE ...] [OPTIONS]

  -l, --level TEXT      Filter by level: DEBUG | INFO | WARN | ERROR | FATAL
  -p, --pattern TEXT    Regex or keyword search (matches full raw line)
      --since TEXT      Include entries from this time  e.g. "2024-01-15 08:00"
      --until TEXT      Include entries up to this time e.g. "2024-01-15 12:00"
  -e, --export FILE     Save results to .txt, .csv, or .json
  -H, --highlight       Highlight pattern matches inline
```

### `watch` — live tail

Streams new entries as they're written, with optional level/pattern filtering.
Shows the last N lines of existing content on startup (like `tail -f`).

```
loglens watch LOGFILE [OPTIONS]

  -l, --level TEXT      Filter by level
  -p, --pattern TEXT    Filter by pattern
  -n, --lines INTEGER   Lines of history to show on start  [default: 10]
```

### `stats` — summary

```
loglens stats sample_logs/app.log
loglens stats app.log worker.log nginx.log   # aggregate across files

LogLens Stats — app.log
────────────────────────────────────────────────────────────
  Total entries    82
  First entry      2024-01-15 08:00:01
  Last entry       2024-01-15 09:30:00

  Level Breakdown
  Level    Count    Bar
  DEBUG       16    ######------------------------ 19.5%
  INFO        39    ##############---------------- 47.6%
  WARN        12    ####-------------------------- 14.6%
  ERROR       13    #####------------------------- 15.9%
  FATAL        2    #----------------------------- 2.4%

  Top Message Patterns
  Count    Message
      3    Connection timeout after 30s ...
      2    Slow query detected ...
      2    POST /api/payments ...
```

---

## Supported Log Formats

Auto-detected — no config, no flags.

| Format | Example |
|---|---|
| **Python logging** | `2024-01-15 08:00:01,234 - app.db - ERROR - Connection timeout` |
| **Nginx error** | `2024/01/15 08:10:00 [error] 1234#0: connect() failed` |
| **Apache CLF** | `127.0.0.1 - frank [15/Jan/2024:08:00:01 +0000] "GET / HTTP/1.1" 200 1234` |
| **Generic** | `ERROR: disk full` or `[2024-01-15 08:00] WARN: high memory usage` |

Level aliases are normalized automatically: `WARNING` → `WARN`, `CRITICAL` → `FATAL`.

---

## Export

```bash
# CSV — timestamp, level, source, message, file columns
loglens parse app.log --level ERROR --export errors.csv

# JSON — structured array, one object per entry
loglens parse app.log --level ERROR --export errors.json

# Plain text — original raw lines
loglens parse app.log --pattern "timeout" --export timeouts.txt
```

---

## Dev Setup

```bash
git clone https://github.com/yourname/loglens
cd loglens
pip install -e ".[dev]"
pytest
```

---

## Roadmap

- [x] v0.1 — `parse` with `--level` and `--pattern`
- [x] v0.2 — `--since`/`--until` time filters + `stats` command
- [x] v0.3 — `watch` live tail mode
- [x] v0.4 — `--export` CSV/TXT + pip installable
- [x] v0.5 — Multi-file parsing + JSON export
- [ ] v0.6 — Saved filter presets

---

## License

MIT
