# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Markdown (`.md`) export support for log entries.
- Added `--min-level` (`-m`) severity threshold filtering for `parse` and `watch` commands.

### Changed
- Clarified CLI help text to distinguish `--level` (exact match) from `--min-level` (severity threshold).

## [0.5.0] - 2026-07-24

### Changed
- Renamed the installable package and CLI entry point from `loglens` to `loglense` to match project branding.
- Aligned the `pyproject.toml` license classifier with the Apache-2.0 `LICENSE` and README.
- Corrected README CLI documentation to reflect Typer (not Click/argparse).

### Added
- `CONTRIBUTING.md` with setup, workflow, and code-style guidance.
- Tests covering `main.py`, `exporter.py`, and `watcher.py`.
- GitHub Actions CI running `pytest` and `ruff` on push and pull requests.
- Ruff lint configuration for Python 3.8+.

### Fixed
- Deduplicated level-normalization and regex-compile helpers across parser/filters.
- Made `watch` reuse `apply_filters` instead of a separate filtering path.
- Surfaced watcher `OSError` failures as stderr warnings.
- Fixed a crash in `watch_file` when the target file does not exist yet.
- Fixed Python 3.8 test collection typing issues and ruff lint failures (E741, I001, F401).

## [0.1.0] - 2026-06-01

### Added
- Initial LogLense CLI for parsing, filtering, and watching log files.
