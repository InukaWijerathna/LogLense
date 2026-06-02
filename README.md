
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
- 📤 Export to CSV, JSON, or plain text
- ⚙️ Auto-detection for Python logging, Nginx, Apache CLF, and generic formats

---

## 🚀 Installation

### Option 1: Install from PyPI (recommended)

```bash
pip install loglens
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
loglens parse sample_logs/app.log
```

2. Watch a file live (shows history then streams new lines):

```bash
loglens watch sample_logs/app.log --level ERROR
```

3. Aggregate and export errors to JSON:

```bash
loglens parse app.log worker.log --level ERROR --export errors.json
```

### Commands quick reference

- `parse` — filter and render log entries
- `watch` — live tail a file
- `stats` — show aggregate metrics

Use `--help` on any subcommand for full options, e.g. `loglens parse --help`.

---

## 🏗️ Project Structure

```
LogLense/
├── loglens/                 # Python package
│   ├── __init__.py
│   ├── main.py              # CLI entrypoints
│   ├── parser.py            # Parsing & detection logic
│   ├── filters.py           # Filter helpers
│   ├── exporter.py          # Export to CSV/JSON
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
| CLI framework| Click / argparse |
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
python -m loglens parse sample_logs/app.log
```

---

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the repo
2. Create a feature branch
3. Add tests for new behavior
4. Open a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) if present for coding guidelines.

---

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

---

*Designed for fast, human-friendly log exploration.*

