import os

os.environ["DB_PATH"] = "test_signbridge.db"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.signs import SIGNS, classify_fingers  # noqa: E402

client = TestClient(app)


def test_patterns_unique():
    assert len({tuple(s["fingers"]) for s in SIGNS}) == len(SIGNS)


def test_classify_v():
    assert classify_fingers((0, 1, 1, 0, 0))["id"] == "V"


def test_unknown_pattern():
    assert classify_fingers((0, 0, 1, 0, 0)) is None


def test_progress_flow():
    u = "tester"
    client.post("/api/progress/quiz", json={"user_id": u, "sign_id": "A", "correct": True})
    client.post("/api/progress/quiz", json={"user_id": u, "sign_id": "A", "correct": False})
    p = client.get(f"/api/progress/{u}").json()
    assert p["quiz"]["total"] >= 2
    assert client.post("/api/progress/quiz", json={"user_id": u, "sign_id": "ZZ", "correct": True}).status_code == 400
