"""Standalone desktop demo: webcam -> landmarks -> sign, no website needed.

Usage: python ml/realtime_demo.py
"""
import sys
from pathlib import Path

import cv2
import mediapipe as mp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.signs import classify  # noqa: E402

hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.6)
draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)
    res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    label = "-"
    if res.multi_hand_landmarks:
        hl = res.multi_hand_landmarks[0]
        draw.draw_landmarks(frame, hl, mp.solutions.hands.HAND_CONNECTIONS)
        s = classify([(p.x, p.y) for p in hl.landmark])
        label = s["symbol"] if s else "unknown"
    cv2.putText(frame, label, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 200, 255), 3)
    cv2.imshow("SignBridge", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()
