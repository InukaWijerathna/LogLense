<div align="center">

  # LogLense

  ![Banner](https://img.shields.io/badge/LogLense-CLI_Log_Parser-0ea5e9?style=for-the-badge&logo=gnubash&logoColor=white)

  ![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![License](https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge)
  ![Version](https://img.shields.io/badge/version-0.5.0-8b5cf6?style=for-the-badge)

</div>

**LogLense** is a smart CLI log parser, filter, and watcher for developers. Like `grep` + `tail -f` — but with structured output, color-coded levels, time filters, and a clean rich UI. Zero config, ships with sample logs.

---

## ✨ Features

- **Level Filtering** — Filter by `DEBUG`, `INFO`, `WARN`, `ERROR`, or `FATAL` with color-coded output
- **Pattern Search** — Regex or keyword search across the full raw log line, with optional inline highlighting
- **Time Range** — Slice any log file by `--since` and `--until` timestamps
- **Multi-file** — Parse and aggregate multiple log files at once; a File column appears automatically
- **Live Tail** — Stream new entries in real time as they're written, with level and pattern filters applied
- **Stats Summary** — Level breakdown bar chart, time range, and top message patterns at a glance
- **Export** — Save filtered results to `.csv`, `.json`, or `.txt`
- **Auto Format Detection** — Supports Python logging, Apache CLF, Nginx error logs, and generic formats — no config needed

---

## ⚡ Quick Start

Install from PyPI:

```bash
pip install loglens
```

Or clone and run immediately with the bundled sample log:

```bash
git clone https://github.com/InukaWijerathna/LogLensee.git
cd LogLensee
pip install -e .

loglens parse sample_logs/app.log
```

---

## 📋 Commands

### `parse` — filter and display

Accepts one or more files. When entries come from different files, a **File** column is added automatically.

```
loglens parse LOGFILE [LOGFILE ...] [OPTIONS]

  -l, --level TEXT      Filter by level: DEBUG | INFO | WARN | ERROR | FATAL
  -p, --pattern TEXT    Regex or keyword search (matches full raw line)
      --since TEXT      Start time  e.g. "2024-01-15 08:00"
      --until TEXT      End time    e.g. "2024-01-15 12:00"
  -e, --export FILE     Save results to .txt, .csv, or .json
  -H, --highlight       Highlight pattern matches inline
```

**Examples**

```bash
# Filter to errors
loglens parse sample_logs/app.log --level ERROR

# Regex search with highlights
loglens parse sample_logs/app.log --pattern "timeout" --highlight

# Time window
loglens parse sample_logs/app.log --since "2024-01-15 08:10" --until "2024-01-15 09:00"

# Aggregate multiple files
loglens parse app.log worker.log nginx.log --level ERROR

# Export to JSON
loglens parse sample_logs/app.log --level ERROR --export errors.json
```

---

### `watch` — live tail

Streams new lines as they are written. Shows the last N lines of existing content on startup.

```
loglens watch LOGFILE [OPTIONS]

  -l, --level TEXT      Filter by level
  -p, --pattern TEXT    Filter by pattern
  -n, --lines INTEGER   Lines of history to show on start  [default: 10]
```

```bash
loglens watch app.log --level ERROR
loglens watch app.log --pattern "timeout" --highlight
```

---

### `stats` — summary

```
loglens stats LOGFILE [LOGFILE ...] [OPTIONS]

  -p, --pattern TEXT    Scope stats to matching entries only
```

```
LogLense Stats — app.log
────────────────────────────────────────────────────
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
```

---

## 🗂️ Supported Log Formats

Auto-detected — no flags or config files needed.

| Format | Example |
|--------|---------|
| **Python logging** | `2024-01-15 08:00:01,234 - app.db - ERROR - Connection timeout` |
| **Nginx error** | `2024/01/15 08:10:00 [error] 1234#0: connect() failed` |
| **Apache CLF** | `127.0.0.1 - frank [15/Jan/2024:08:00:01 +0000] "GET / HTTP/1.1" 200 1234` |
| **Generic** | `ERROR: disk full` or `[2024-01-15 08:00] WARN: high memory` |

Level aliases are normalized automatically — `WARNING` → `WARN`, `CRITICAL` → `FATAL`.

---

## 📤 Export

```bash
# Structured columns: timestamp, level, source, message, file
loglens parse app.log --level ERROR --export errors.csv

# JSON array, one object per entry
loglens parse app.log --level ERROR --export errors.json

# Original raw lines
loglens parse app.log --pattern "timeout" --export timeouts.txt
```

---

## 🛠️ Tech Stack

| Library | Purpose |
|---------|---------|
| [typer](https://typer.tiangolo.com) | CLI interface |
| [rich](https://rich.readthedocs.io) | Colored terminal output, tables, panels |
| [watchdog](https://python-watchdog.readthedocs.io) | Live file watching for `--watch` mode |
| `re` | Regex pattern matching |
| `csv` / `json` | Export functionality |

---

## 🚀 Dev Setup

```bash
git clone https://github.com/InukaWijerathna/LogLensee.git
cd LogLensee
pip install -e ".[dev]"
pytest
```

---

## 🗺️ Roadmap

- [x] v0.1 — `parse` with `--level` and `--pattern`
- [x] v0.2 — `--since` / `--until` time filters + `stats` command
- [x] v0.3 — `watch` live tail mode
- [x] v0.4 — `--export` CSV / TXT + pip installable
- [x] v0.5 — Multi-file parsing + JSON export
- [ ] v0.6 — Saved filter presets

---

## 📄 License

MIT
