"""Tiny SQLite store for per-user progress."""
import os
import sqlite3
import time

DB_PATH = os.getenv("DB_PATH", "signbridge.db")


def conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init() -> None:
    with conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS detections (user_id TEXT, sign_id TEXT, at REAL);
            CREATE TABLE IF NOT EXISTS quiz (user_id TEXT, sign_id TEXT, ok INTEGER, at REAL);
            CREATE TABLE IF NOT EXISTS learned (user_id TEXT, sign_id TEXT, PRIMARY KEY (user_id, sign_id));
            """
        )


def add_detection(user: str, sign: str) -> None:
    with conn() as c:
        c.execute("INSERT INTO detections VALUES (?,?,?)", (user, sign, time.time()))


def add_quiz(user: str, sign: str, ok: bool) -> None:
    with conn() as c:
        c.execute("INSERT INTO quiz VALUES (?,?,?,?)", (user, sign, int(ok), time.time()))


def toggle_learned(user: str, sign: str) -> bool:
    with conn() as c:
        if c.execute("SELECT 1 FROM learned WHERE user_id=? AND sign_id=?", (user, sign)).fetchone():
            c.execute("DELETE FROM learned WHERE user_id=? AND sign_id=?", (user, sign))
            return False
        c.execute("INSERT INTO learned VALUES (?,?)", (user, sign))
        return True


def progress(user: str) -> dict:
    with conn() as c:
        det = {r["sign_id"]: r["n"] for r in c.execute(
            "SELECT sign_id, COUNT(*) n FROM detections WHERE user_id=? GROUP BY sign_id", (user,))}
        q = c.execute("SELECT COUNT(*) total, COALESCE(SUM(ok),0) correct FROM quiz WHERE user_id=?", (user,)).fetchone()
        per = {r["sign_id"]: {"tries": r["t"], "correct": r["c"]} for r in c.execute(
            "SELECT sign_id, COUNT(*) t, SUM(ok) c FROM quiz WHERE user_id=? GROUP BY sign_id", (user,))}
        learned = [r["sign_id"] for r in c.execute("SELECT sign_id FROM learned WHERE user_id=?", (user,))]
    return {"detections": det, "learned": learned,
            "quiz": {"total": q["total"], "correct": q["correct"], "per_sign": per}}
