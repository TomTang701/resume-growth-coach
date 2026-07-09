import json
from pathlib import Path

import pytest

from app.services.matching import analyze_resume_against_job


BASELINE_PATH = Path(__file__).parent / "fixtures" / "score_baseline.json"
CASES = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_score_baseline_is_stable(case):
    result = analyze_resume_against_job(case["resume"], case["job"])

    assert result.fit_score == case["expected_score"]
