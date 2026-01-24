# tests/test_schedule_api.py

import pytest
from src.backend.main import create_app
from src.backend.database import get_db_connection, init_db


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------
@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Each test gets a completely clean database."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_FILE", str(db_file))
    init_db()


@pytest.fixture
def client():
    app = create_app()
    app.config.update({"TESTING": True})
    return app.test_client()


# ------------------------------------------------------------------
# QUEST Schedule Import
# ------------------------------------------------------------------
def test_import_schedule_quest_empty_text(client):
    """Empty schedule text → 400 Bad Request (currently passing)"""
    resp = client.post("/api/schedules", json={"scheduleText": "   "})
    assert resp.status_code == 400


# ------------------------------------------------------------------
# iCalendar Import
# ------------------------------------------------------------------
def test_import_icalendar_empty(client):
    """Empty iCalendar content → 400 Bad Request (currently passing)"""
    resp = client.post("/api/schedules/icalendar", json={"icalContent": ""})
    assert resp.status_code == 400


# ------------------------------------------------------------------
# Schedule Retrieval
# ------------------------------------------------------------------
def test_get_schedule_by_id(client):
    """Insert a schedule and retrieve it by ID → 200 + correct data"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO schedules (user_id, term) VALUES (?, ?)", (1, "Fall 2025"))
    schedule_id = cur.lastrowid
    conn.commit()

    resp = client.get(f"/api/schedules/{schedule_id}")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["success"] is True
    assert data["schedule"]["schedule_id"] == schedule_id
    assert data["schedule"]["term"] == "Fall 2025"


def test_get_schedule_not_found(client):
    """Non-existent schedule ID → 404"""
    resp = client.get("/api/schedules/999999")
    assert resp.status_code == 404