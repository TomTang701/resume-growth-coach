"""Run a real Chromium smoke test against a temporary local app database."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8765"


def wait_for_server(timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health", timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.25)
    raise TimeoutError("Local app did not become ready.")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="resume-growth-browser-") as temp_dir:
        env = os.environ.copy()
        env["RGC_DATABASE_URL"] = f"sqlite:///{Path(temp_dir) / 'browser.sqlite3'}"
        server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8765", "--no-access-log"],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            wait_for_server()
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(BASE_URL, wait_until="domcontentloaded")
                assert page.title() == "Resume Growth Coach"
                page.locator("#resume_text").fill("Built Python APIs with Git.")
                page.locator("#job_description_text").fill("Software Engineer requiring Python and Git.")
                page.get_by_role("button", name="Run analysis").click()
                page.locator(".score").wait_for()
                assert page.locator("text=Alternative Matching Jobs").count() == 1

                page.goto(BASE_URL, wait_until="domcontentloaded")
                page.locator("#resume_text").fill("Built a FastAPI service with Python, SQLite, SQLAlchemy, and pytest.")
                page.locator("#job_template").select_option("backend_full_stack_intern")
                page.get_by_role("button", name="Run analysis").click()
                page.locator(".score").wait_for()
                assert page.locator("text=Portfolio Planner").count() == 1
                assert page.locator("text=Implementation active; evidence gate pending.").count() == 1

                page.goto(BASE_URL, wait_until="domcontentloaded")
                page.locator("#resume_text").fill("Built Python APIs with Git.")
                page.get_by_role("button", name="Run analysis").click()
                assert page.locator("text=Job description content is required.").count() == 1

                resume_path = Path(temp_dir) / "resume.txt"
                job_path = Path(temp_dir) / "job.txt"
                resume_path.write_text("Built Python APIs with Git.", encoding="utf-8")
                job_path.write_text("Software Engineer requiring Python and Git.", encoding="utf-8")
                page.goto(BASE_URL, wait_until="domcontentloaded")
                page.locator("#resume_file").set_input_files(str(resume_path))
                page.locator("#job_description_file").set_input_files(str(job_path))
                page.get_by_role("button", name="Run analysis").click()
                page.locator(".score").wait_for()
                browser.close()
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
    print("Browser smoke test passed: page load, text and template analysis, planner display, validation recovery, and file upload.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
