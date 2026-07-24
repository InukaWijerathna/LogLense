import json

import pytest
from typer.testing import CliRunner

from loglense.main import _build_regex, _ensure_files_exist, _parse_dt, app

runner = CliRunner()

SAMPLE_LOG = (
    "2024-01-15 08:23:45,123 - app - INFO - server started\n"
    "2024-01-15 08:23:46,123 - app - ERROR - something broke\n"
)


@pytest.fixture
def log_file(tmp_path):
    path = tmp_path / "app.log"
    path.write_text(SAMPLE_LOG, encoding="utf-8")
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
