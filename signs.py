"""Sign vocabulary and rule-based classifier (mirrors the frontend's src/lib/signs.ts)."""
from __future__ import annotations

import math
from typing import Sequence

# fingers = (thumb, index, middle, ring, pinky) -> True if extended
SIGNS = [
    {"id": "hello", "symbol": "Hello", "meaning": "Greeting", "fingers": (1, 1, 1, 1, 1)},
    {"id": "B", "symbol": "B", "meaning": "Letter B", "fingers": (0, 1, 1, 1, 1)},
    {"id": "A", "symbol": "A", "meaning": "Letter A", "fingers": (0, 0, 0, 0, 0)},
    {"id": "D", "symbol": "D", "meaning": "Letter D / number 1", "fingers": (0, 1, 0, 0, 0)},
    {"id": "V", "symbol": "V", "meaning": "Letter V / number 2", "fingers": (0, 1, 1, 0, 0)},
    {"id": "W", "symbol": "W", "meaning": "Letter W / number 3", "fingers": (0, 1, 1, 1, 0)},
    {"id": "L", "symbol": "L", "meaning": "Letter L", "fingers": (1, 1, 0, 0, 0)},
    {"id": "Y", "symbol": "Y", "meaning": "Letter Y", "fingers": (1, 0, 0, 0, 1)},
    {"id": "I", "symbol": "I", "meaning": "Letter I", "fingers": (0, 0, 0, 0, 1)},
    {"id": "love", "symbol": "I love you", "meaning": "ILY sign", "fingers": (1, 1, 0, 0, 1)},
    {"id": "good", "symbol": "Good", "meaning": "Thumbs up / OK", "fingers": (1, 0, 0, 0, 0)},
]
SIGN_IDS = [s["id"] for s in SIGNS]

Point = Sequence[float]  # (x, y[, z]) normalized


def _d(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def finger_states(lm: Sequence[Point]) -> tuple[int, ...]:
    """Which fingers are extended, from 21 MediaPipe hand landmarks."""
    wrist = lm[0]

    def ext(tip: int, pip: int) -> int:
        return int(_d(lm[tip], wrist) > _d(lm[pip], wrist) * 1.1)

    palm = _d(lm[0], lm[9])
    thumb = int(_d(lm[4], lm[17]) > _d(lm[3], lm[17]) * 1.05 and _d(lm[4], lm[5]) > palm * 0.55)
    return (thumb, ext(8, 6), ext(12, 10), ext(16, 14), ext(20, 18))


def classify_fingers(f: Sequence[int]) -> dict | None:
    return next((s for s in SIGNS if tuple(s["fingers"]) == tuple(f)), None)


def classify(lm: Sequence[Point]) -> dict | None:
    if len(lm) < 21:
        return None
    return classify_fingers(finger_states(lm))


def normalize(lm: Sequence[Point]) -> list[float]:
    """Wrist-relative, scale-invariant feature vector (42 values) for ML models."""
    wx, wy = lm[0][0], lm[0][1]
    scale = _d(lm[0], lm[9]) or 1.0
    out: list[float] = []
    for p in lm:
        out += [(p[0] - wx) / scale, (p[1] - wy) / scale]
    return out
