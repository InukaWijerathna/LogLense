import json

import pytest
from typer.testing import CliRunner

from loglense.main import _build_regex, _ensure_files_exist, _parse_dt, app

runner = CliRunner()

SAMPLE_LOG = (
    "2024-01-15 08:23:45,123 - app - INFO - server started\n"
    "2024-01-15 08:23:46,123 - app - ERROR - something broke\n"
)

FULL_LEVEL_LOG = (
    "2024-01-15 08:00:00,000 - app - DEBUG - debug msg\n"
    "2024-01-15 08:01:00,000 - app - INFO - info msg\n"
    "2024-01-15 08:02:00,000 - app - WARN - warn msg\n"
    "2024-01-15 08:03:00,000 - app - ERROR - error msg\n"
    "2024-01-15 08:04:00,000 - app - FATAL - fatal msg\n"
)

LOW_ERROR_LOG = (
    "2024-01-15 08:00:00,000 - app - INFO - msg1\n"
    "2024-01-15 08:01:00,000 - app - INFO - msg2\n"
    "2024-01-15 08:02:00,000 - app - INFO - msg3\n"
    "2024-01-15 08:03:00,000 - app - INFO - msg4\n"
    "2024-01-15 08:04:00,000 - app - INFO - msg5\n"
    "2024-01-15 08:05:00,000 - app - INFO - msg6\n"
    "2024-01-15 08:06:00,000 - app - INFO - msg7\n"
    "2024-01-15 08:07:00,000 - app - INFO - msg8\n"
    "2024-01-15 08:08:00,000 - app - INFO - msg9\n"
    "2024-01-15 08:09:00,000 - app - INFO - msg10\n"
)

@pytest.fixture
def full_level_log(tmp_path):
    path = tmp_path / "levels.log"
    path.write_text(FULL_LEVEL_LOG, encoding="utf-8")
    return path


@pytest.fixture
def log_file(tmp_path):
    path = tmp_path / "app.log"
    path.write_text(SAMPLE_LOG, encoding="utf-8")
    return path


@pytest.fixture
def low_error_log(tmp_path):
    path = tmp_path / "low_error.log"
    path.write_text(LOW_ERROR_LOG, encoding="utf-8")
    return path


def test_parse_dt_accepts_known_formats():
    assert _parse_dt(None) is None
    assert _parse_dt("2024-01-15").isoformat() == "2024-01-15T00:00:00"
    assert _parse_dt("2024-01-15 08:23:45").isoformat() == "2024-01-15T08:23:45"


def test_parse_dt_rejects_unknown_format():
    with pytest.raises(Exception):
        _parse_dt("not-a-date")


def test_build_regex_falls_back_to_literal_on_bad_pattern():
    regex = _build_regex("[unclosed")
    assert regex.search("literal [unclosed match")


def test_ensure_files_exist_raises_on_missing(tmp_path):
    with pytest.raises(Exception):
        _ensure_files_exist([tmp_path / "nope.log"])


def test_parse_command_outputs_matching_entries(log_file):
    result = runner.invoke(app, ["parse", str(log_file), "--level", "ERROR"])
    assert result.exit_code == 0
    assert "something broke" in result.stdout
    assert "server started" not in result.stdout


def test_parse_command_outputs_multiple_matching_levels(full_level_log):
    result = runner.invoke(
        app,
        ["parse", str(full_level_log), "--level", "ERROR", "--level", "FATAL"],
    )

    assert result.exit_code == 0
    assert "error msg" in result.stdout
    assert "fatal msg" in result.stdout
    assert "debug msg" not in result.stdout
    assert "info msg" not in result.stdout
    assert "warn msg" not in result.stdout


def test_parse_command_missing_file_exits_nonzero(tmp_path):
    result = runner.invoke(app, ["parse", str(tmp_path / "missing.log")])
    assert result.exit_code != 0


def test_parse_command_exports_json(tmp_path, log_file):
    export_path = tmp_path / "out.json"
    result = runner.invoke(app, ["parse", str(log_file), "--export", str(export_path)])
    assert result.exit_code == 0
    data = json.loads(export_path.read_text(encoding="utf-8"))
    assert len(data) == 2


def test_stats_command_reports_totals(log_file):
    result = runner.invoke(app, ["stats", str(log_file)])
    assert result.exit_code == 0
    assert "Total entries" in result.stdout


def test_stats_command_warns_on_high_error_rate(log_file):
    result = runner.invoke(app, ["stats", str(log_file)])

    assert result.exit_code == 0
    assert "High error rate" in result.stdout
    assert "50.0% of entries are ERROR/FATAL" in result.stdout


def test_stats_command_does_not_warn_on_healthy_log(low_error_log):
    result = runner.invoke(app, ["stats", str(low_error_log)])

    assert result.exit_code == 0
    assert "High error rate" not in result.stdout


def test_stats_command_respects_error_threshold(log_file):
    result = runner.invoke(app, ["stats", str(log_file), "--error-threshold", "60"])

    assert result.exit_code == 0
    assert "High error rate" not in result.stdout


def test_parse_command_min_level_warn_keeps_warn_and_above(full_level_log):
    result = runner.invoke(
        app,
        ["parse", str(full_level_log), "--min-level", "WARN"],
    )

    assert result.exit_code == 0

    assert "warn msg" in result.stdout
    assert "error msg" in result.stdout
    assert "fatal msg" in result.stdout

    assert "debug msg" not in result.stdout
    assert "info msg" not in result.stdout

def test_parse_command_level_and_min_level_together(full_level_log):
    result = runner.invoke(
        app,
        [
            "parse",
            str(full_level_log),
            "--level",
            "ERROR",
            "--min-level",
            "WARN",
        ],
    )

    assert result.exit_code == 0

    assert "error msg" in result.stdout

    assert "debug msg" not in result.stdout
    assert "info msg" not in result.stdout
    assert "warn msg" not in result.stdout
    assert "fatal msg" not in result.stdout

def test_level_takes_precedence_over_min_level(full_level_log):
    result = runner.invoke(
        app,
        [
            "parse",
            str(full_level_log),
            "--level",
            "INFO",
            "--min-level",
            "WARN",
        ],
    )

    assert result.exit_code == 0

    assert "info msg" in result.stdout

    assert "warn msg" not in result.stdout
    assert "error msg" not in result.stdout
    assert "fatal msg" not in result.stdout


def test_parse_command_tail_shows_last_n_entries(full_level_log):
    result = runner.invoke(
        app,
        [
            "parse",
            str(full_level_log),
            "--tail",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert "error msg" in result.stdout
    assert "fatal msg" in result.stdout
    assert "debug msg" not in result.stdout
    assert "info msg" not in result.stdout
    assert "warn msg" not in result.stdout
    assert "Showing last 2 of 5 matched entries" in result.stdout


def test_parse_command_tail_with_level_filter(full_level_log):
    result = runner.invoke(
        app,
        [
            "parse",
            str(full_level_log),
            "--level",
            "ERROR",
            "--level",
            "FATAL",
            "--tail",
            "1"
        ],
    )

    assert result.exit_code == 0
    assert "error msg" not in result.stdout
    assert "fatal msg" in result.stdout
    assert "Showing last 1 of 2 matched entries" in result.stdout


def test_parse_command_tail_exports_only_last_entries(tmp_path, full_level_log):
    export_path = tmp_path / "out.json"
    result = runner.invoke(
        app,
        [
            "parse",
            str(full_level_log),
            "--tail",
            "2",
            "--export",
            str(export_path)
        ],
    )
    assert result.exit_code == 0
    data = json.loads(export_path.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert [e["message"] for e in data] == ["error msg", "fatal msg"]
    assert "error msg" in result.stdout
    assert "fatal msg" in result.stdout


def test_parse_command_tail_larger_than_matches(full_level_log):
    result = runner.invoke(
        app,
        [
            "parse",
            str(full_level_log),
            "--tail",
            "20"
        ],
    )
    
    assert result.exit_code == 0
    assert "error msg" in result.stdout
    assert "info msg" in result.stdout
    assert "debug msg" in result.stdout
    assert "warn msg" in result.stdout
    assert "fatal msg" in result.stdout
    assert "Showing last 5 of 5 matched entries" in result.stdout


def test_parser_no_color(full_level_log):
    result = runner.invoke(
        app,
        [
            "parse",
            str(full_level_log),
            "--no-color"
        ],
    )

    assert result.exit_code == 0
    assert "\x1b[" not in result.output


def test_stats_no_color(full_level_log):
    result = runner.invoke(
        app,
        [
            "stats",
            str(full_level_log),
            "--no-color"
        ],
    )

    assert result.exit_code == 0
    assert "\x1b[" not in result.output


def test_no_color_environment_variable(full_level_log, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    result = runner.invoke(
        app,
        [
            "parse",
            str(full_level_log)
        ]
    )

    assert result.exit_code == 0
    assert "\x1b[" not in result.output

