def test_worker_does_not_guess_tools(tmp_path, monkeypatch):
    import app.core.database as db
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path/"company.db")
    from app.core.database import initialize_database
    initialize_database()
    from app.core.runtime_schema import initialize_runtime_schema, seed_default_agents
    initialize_runtime_schema(); seed_default_agents()
    from app.core.autonomous_worker import AutonomousWorker
    w=AutonomousWorker()
    assert w.run_once()["status"]=="IDLE"
