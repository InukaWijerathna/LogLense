
  # LogLense — The CLI Log Lens


LogLense is a small, fast command-line utility for parsing, filtering, and watching log files with structured, colorized output and minimal configuration.

Key goals:

- Fast, zero-configuration parsing of common log formats
- Human-friendly terminal output with level coloring and compact columns
- Composable commands for searching, tailing, and exporting

---

## ✨ Features

- 🔎 Level filtering (DEBUG, INFO, WARN, ERROR, FATAL)
- 🔁 Live tail/watch mode with history buffer
- 🧭 Regex or keyword search with inline highlights
- ⏱ Time-range slicing with `--since` / `--until`
- 📂 Aggregate multiple files with automatic `File` column
- 📤 Export to CSV, JSON, Markdown or plain text
- ⚙️ Auto-detection for Python logging, Nginx, Apache CLF, JSON logs, and generic formats

---

## 🚀 Installation

### Option 1: Install from PyPI (recommended)

```bash
pip install loglense
```

### Option 2: Install from source (developer)

```bash
git clone https://github.com/your-username/LogLense.git
cd LogLense
pip install -e .
```

---

## 🕹️ How to Use

1. Parse one or more files:

```bash
# show parsed entries
loglense parse sample_logs/app.log
```

2. Watch a file live (shows history then streams new lines):

```bash
loglense watch sample_logs/app.log --level ERROR
```

3. Aggregate and export errors to JSON:

```bash
loglense parse app.log worker.log --level ERROR --export errors.json
```

4. Filter for one or more exact log levels:

```bash
loglense parse sample_logs/app.log --level ERROR
loglense parse sample_logs/app.log --level ERROR --level FATAL
```

The first form returns only `ERROR` entries. The second returns entries at either `ERROR` or `FATAL`.

5. Filter by minimum severity threshold:

```bash
loglense parse sample_logs/app.log --min-level WARN
```

Returns `WARN`, `ERROR`, and `FATAL` entries.

6. Both options can be combined:

```bash
loglense parse sample_logs/app.log --level ERROR --min-level WARN
```
In this case, only `ERROR` entries are returned because `--level` takes precedence (when `--level` is set, `--min-level` is ignored).

7. Export results as a Markdown table:

```bash
loglense parse app.log --export report.md
```

8. Display summary statistics and log level distribution.

```bash
loglense stats logs/app.log
```

9. Warn when the percentage of ERROR/FATAL entries exceeds a threshold:

```bash
loglense stats logs/app.log --error-threshold 10
```

The default warning threshold is 5.0%.

10. Hide log entries matching a keyword or regex pattern.

```bash
loglense parse app.log --exclude healthcheck
```

You can combine it with `--pattern`:

```bash
loglense parse app.log --pattern ERROR --exclude healthcheck
```

This shows ERROR entries while excluding healthcheck-related messages.

### Commands quick reference

- `parse` — filter and render log entries
- `watch` — live tail a file
- `stats` — show aggregate metrics

Use `--help` on any subcommand for full options, e.g. `loglense parse --help`.

---

## 🏗️ Project Structure

```
LogLense/
├── loglense/                # Python package
│   ├── __init__.py
│   ├── main.py              # CLI entrypoints
│   ├── parser.py            # Parsing & detection logic
│   ├── filters.py           # Filter helpers
│   ├── exporter.py          # Export to CSV/JSON/Markdown, or plain text
│   └── watcher.py           # Tail/watch implementation
├── sample_logs/             # Example log files used in tests/docs
├── tests/                   # Unit tests
├── pyproject.toml           # Project metadata & dependencies
├── README.md
└── LICENSE
```

---

## ⚙️ Technical Stack

| Component    | Technology |
|--------------|------------|
| Language     | Python 3.8+ |
| CLI framework| typer |
| Output/style | rich (color + tables) |
| Testing      | pytest |
| Packaging    | pyproject.toml / pip |

---

## ⚠️ Safety & Behavior

- Hidden or system files (e.g. `.DS_Store`, `desktop.ini`) are skipped by default.
- The tool never mutates source files; `parse`/`watch` are read-only.
- Actions that could delete or overwrite files require explicit user confirmation.

---

## 🛠️ Development

Install development dependencies and run tests:

```bash
pip install -e .[dev]
pytest -q
```

Run the CLI locally:

```bash
python -m loglense parse sample_logs/app.log
```

---

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the repo
2. Create a feature branch
3. Add tests for new behavior
4. Open a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding guidelines.

---

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

---

*Designed for fast, human-friendly log exploration.*

