
<div align="center">

  # LogLense

  ![Banner](https://img.shields.io/badge/LogLense-CLI_Log_Parser-0ea5e9?style=for-the-badge&logo=gnubash&logoColor=white)

  ![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![License](https://img.shields.io/badge/license-Apache%202.0-22c55e?style=for-the-badge)
  ![Version](https://img.shields.io/badge/version-0.5.0-8b5cf6?style=for-the-badge)

</div>

LogLense is a small, fast CLI tool to parse, filter, and watch log files with structured, colorized output.

Key goals:

- Fast, zero-config parsing of common log formats
- Human-friendly terminal output with level coloring and columns
- Small, composable commands for searching, tailing, and exporting

Table of contents

- Features
- Installation
- Quick start
- Commands
- Examples
- Supported formats
- Development
- Contributing
- License

## Features

- Level filtering (DEBUG, INFO, WARN, ERROR, FATAL)
- Regex or keyword pattern search with inline highlighting
- Time-range slicing with `--since` / `--until`
- Aggregate multiple files with automatic `File` column
- Live tail/watch mode with history buffer
- Export results to CSV, JSON, or plain text
- Auto-detection for Python logging, Nginx, Apache CLF, and generic formats

## Installation

Install from PyPI:

```bash
pip install loglens
```

Or install in editable mode for development:

```bash
git clone https://github.com/InukaWijerathna/LogLensee.git
cd LogLensee
pip install -e .
```

## Quick start

Parse a single file and show entries:

```bash
loglens parse sample_logs/app.log
```

Watch a file live (shows last 10 lines then streams new ones):

```bash
loglens watch app.log --level ERROR
```

Generate a summary of a log file:

```bash
loglens stats app.log
```

## Commands

`parse` — filter and render log entries

```
loglens parse LOGFILE [LOGFILE ...] [OPTIONS]

Options:
  -l, --level TEXT      Filter by level: DEBUG | INFO | WARN | ERROR | FATAL
  -p, --pattern TEXT    Regex or keyword search (matches full raw line)
      --since TEXT      Start time  e.g. "2024-01-15 08:00"
      --until TEXT      End time    e.g. "2024-01-15 12:00"
  -e, --export FILE     Save results to .txt, .csv, or .json
  -H, --highlight       Highlight pattern matches inline
```

`watch` — live tail a file

```
loglens watch LOGFILE [OPTIONS]

Options:
  -l, --level TEXT      Filter by level
  -p, --pattern TEXT    Filter by pattern
  -n, --lines INTEGER   Lines of history to show on start  [default: 10]
```

`stats` — aggregate and show summary metrics

```
loglens stats LOGFILE [LOGFILE ...] [OPTIONS]

Options:
  -p, --pattern TEXT    Scope stats to matching entries only
```

## Examples

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

## Supported formats

Auto-detected; no config required.

| Format | Example |
|--------|---------|
| Python logging | 2024-01-15 08:00:01,234 - app.db - ERROR - Connection timeout |
| Nginx error | 2024/01/15 08:10:00 [error] 1234#0: connect() failed |
| Apache CLF | 127.0.0.1 - frank [15/Jan/2024:08:00:01 +0000] "GET / HTTP/1.1" 200 1234 |
| Generic | ERROR: disk full or [2024-01-15 08:00] WARN: high memory |

Level aliases are normalized (`WARNING` -> `WARN`, `CRITICAL` -> `FATAL`).

## Development

Install dev dependencies and run tests:

```bash
pip install -e .[dev]
pytest -q
```

Project layout: see [loglens](loglens) package for CLI entry points and implementation.

## Contributing

Contributions welcome. Please open issues for bugs or feature requests and follow standard PR workflow:

1. Fork the repository
2. Create a branch for your feature/fix
3. Add tests where appropriate
4. Open a pull request

## Roadmap

- v0.5: Multi-file parsing, JSON export (current)
- v0.6: Saved filter presets, config profiles

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
