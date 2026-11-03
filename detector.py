"""Hand landmark detection (MediaPipe) + classification (trained model if present, else rules)."""
from __future__ import annotations

import os
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

from .signs import SIGNS, classify, normalize

MODEL_PATH = Path(os.getenv("MODEL_PATH", Path(__file__).resolve().parents[2] / "ml" / "model.joblib"))

_hands = mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)
_model = None
if MODEL_PATH.exists():
    import joblib

    _model = joblib.load(MODEL_PATH)


def predict_image(data: bytes) -> dict:
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image")
    res = _hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if not res.multi_hand_landmarks:
        return {"hand_found": False, "sign_id": None, "confidence": 0.0, "method": None, "landmarks": []}
    lm = [(p.x, p.y, p.z) for p in res.multi_hand_landmarks[0].landmark]

    if _model is not None:
        probs = _model.predict_proba([normalize(lm)])[0]
        i = int(np.argmax(probs))
        sign_id = str(_model.classes_[i]) if probs[i] >= 0.6 else None
        conf, method = float(probs[i]), "ml"
    else:
        s = classify(lm)
        sign_id, conf, method = (s["id"] if s else None), (1.0 if s else 0.0), "rules"

    sign = next((s for s in SIGNS if s["id"] == sign_id), None)
    return {
        "hand_found": True,
        "sign_id": sign_id,
        "symbol": sign["symbol"] if sign else None,
        "confidence": conf,
        "method": method,
        "landmarks": [list(p) for p in lm],
    }
