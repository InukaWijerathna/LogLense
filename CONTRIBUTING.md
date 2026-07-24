# Contributing to LogLense

Thanks for your interest in improving LogLense.

## Setup

```bash
git clone https://github.com/your-username/LogLense.git
cd LogLense
pip install -e .[dev]
```

## Workflow

1. Fork the repo and create a feature branch.
2. Make your change, keeping functions small and focused.
3. Add or update tests in `tests/` for any behavior change.
4. Run the test suite and linter before opening a PR:

```bash
pytest -q
ruff check .
```

5. Open a pull request describing the change and why it's needed.


6. For user-facing changes, update `CHANGELOG.md` under `[Unreleased]` (or the appropriate version section) before opening the PR.

## Code style

- Follow the existing type-hint style (`from __future__ import annotations`, builtin generics).
- Keep parsing/filtering logic in `loglense/parser.py` and `loglense/filters.py`; keep `loglense/main.py` focused on CLI wiring and presentation.
- Avoid duplicating logic that already exists elsewhere in the package (e.g. level normalization lives in `parser.py`, regex-with-fallback compilation lives in `filters.py`).
