"""Collect hand-landmark samples from your webcam.

Usage: python ml/collect_data.py --sign V --samples 200
Hold the sign in front of the camera; press SPACE to start/pause recording, Q to quit.
Rows are appended to ml/data.csv as: label, 42 normalized coordinates.
"""
import argparse
import csv
import sys
from pathlib import Path

import cv2
import mediapipe as mp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.signs import SIGN_IDS, normalize  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--sign", required=True, choices=SIGN_IDS)
ap.add_argument("--samples", type=int, default=200)
args = ap.parse_args()

out = Path(__file__).parent / "data.csv"
hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.6)
draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
count, recording = 0, False

with out.open("a", newline="") as f:
    w = csv.writer(f)
    while count < args.samples:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if res.multi_hand_landmarks:
            hl = res.multi_hand_landmarks[0]
            draw.draw_landmarks(frame, hl, mp.solutions.hands.HAND_CONNECTIONS)
            if recording:
                w.writerow([args.sign] + normalize([(p.x, p.y) for p in hl.landmark]))
                count += 1
        cv2.putText(frame, f"{args.sign} {count}/{args.samples} {'REC' if recording else 'paused (SPACE)'}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
        cv2.imshow("SignBridge collector", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord(" "):
            recording = not recording
        elif k == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
print(f"Saved {count} samples for '{args.sign}' to {out}")
