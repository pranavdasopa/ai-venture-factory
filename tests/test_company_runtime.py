def test_runtime_boots(monkeypatch, tmp_path):
    import app.core.database as database
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "company.db")

    from app.core.company_runtime import CompanyRuntime
    runtime = CompanyRuntime()
    status = runtime.status()

    assert status["status"] == "ONLINE"
    assert status["runtime"] == "READY"
    assert status["pending_tasks"] == 0
    assert status["pending_events"] == 0
    assert len(status["agents"]) >= 5
