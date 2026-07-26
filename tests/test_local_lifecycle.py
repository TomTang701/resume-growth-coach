import base64
import json
import subprocess
import sys
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


def test_lifecycle_starts_the_recorded_python_process_directly():
    lifecycle_script = (Path(__file__).resolve().parents[1] / "scripts" / "local-server.ps1").read_text(encoding="utf-8")

    assert "Start-Process -FilePath $python" in lifecycle_script
    assert '$rootProcess.Name -ine "python.exe"' in lifecycle_script


def test_lifecycle_cli_accepts_an_encoded_observed_command(tmp_path: Path):
    record_path = tmp_path / "local-server.json"
    record_path.write_text(
        json.dumps({"pid": 1234, "checkout": str(tmp_path), "command_marker": "uvicorn app.main:app"}),
        encoding="utf-8",
    )
    command = "python.exe -m uvicorn app.main:app --app-dir 'C:\\workspace with spaces' --reload"
    encoded_command = base64.b64encode(command.encode("utf-8")).decode("ascii")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.lifecycle",
            "--record-path",
            str(record_path),
            "--checkout",
            str(tmp_path),
            "--observed-command-base64",
            encoded_command,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
