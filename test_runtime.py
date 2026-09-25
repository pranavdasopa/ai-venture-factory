from app.core.runtime import get_runtime_status


def test_runtime_status_is_evidence_backed():
    status = get_runtime_status()

    assert status["company"] == "AI Venture Factory"
    assert status["database"]["ok"] is True
    assert status["truth_policy"]["synthetic_metrics"] is False
    assert status["truth_policy"]["unverified_claims"] is False
