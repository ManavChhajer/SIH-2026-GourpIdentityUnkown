import pytest

import db as db_module


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Point the db module at a throwaway SQLite file for every test in the
    suite (including test_main.py's FastAPI TestClient), so tests never
    read/write the real demo database (land_records.db)."""
    test_db_path = tmp_path / "test.db"
    engine = db_module.create_engine(
        f"sqlite:///{test_db_path}", connect_args={"check_same_thread": False}
    )
    monkeypatch.setattr(db_module, "engine", engine)
    monkeypatch.setattr(
        db_module, "SessionLocal", db_module.sessionmaker(bind=engine, autoflush=False, autocommit=False)
    )
    db_module.init_db()
    yield
