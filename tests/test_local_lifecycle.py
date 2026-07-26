from pathlib import Path

from app.lifecycle import lifecycle_record_is_valid


def test_pid_record_rejects_wrong_checkout(tmp_path: Path):
    payload = {
        "pid": 1234,
        "checkout": "C:\\wrong",
        "command_marker": "uvicorn app.main:app",
    }

    assert lifecycle_record_is_valid(
        payload,
        checkout=tmp_path,
        observed_command="cmd /k uvicorn app.main:app",
    ) is False


def test_pid_record_requires_expected_command(tmp_path: Path):
    payload = {
        "pid": 1234,
        "checkout": str(tmp_path),
        "command_marker": "uvicorn app.main:app",
    }

    assert lifecycle_record_is_valid(
        payload,
        checkout=tmp_path,
        observed_command="cmd /k uvicorn app.main:app",
    ) is True
    assert lifecycle_record_is_valid(
        payload,
        checkout=tmp_path,
        observed_command="cmd /k python -m http.server",
    ) is False
