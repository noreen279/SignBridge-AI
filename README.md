# SignBridge — Hand Sign Recognition

Recognizes a small set of static hand signs (Hello, A, B, D, V, W, L, Y, I, I love you, Good)
from a camera or photo and translates them into letters/words.

**AI pipeline:** Computer Vision → Hand Landmark Detection (MediaPipe, 21 points) → Classification
(finger-state rules, or a Random Forest you train on your own data).

```
signbridge/
├── backend/        Python FastAPI API (predict, signs, progress in SQLite)
├── ml/             Python: data collection, training, desktop demo
└── frontend/       Website (React + TanStack Start + Tailwind)
                    Pages: Live Recognition, Learn Signs, Practice Quiz, Progress
```

## 1. Backend (Python 3.10–3.12)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/signs | List supported signs |
| POST | /api/predict | Upload image (`file`) → `{hand_found, sign_id, symbol, confidence, method, landmarks}` |
| POST | /api/progress/detection | `{user_id, sign_id}` |
| POST | /api/progress/quiz | `{user_id, sign_id, correct}` |
| POST | /api/progress/learned | `{user_id, sign_id}` toggles learned |
| GET | /api/progress/{user_id} | Progress summary |

Tests: `pytest` (inside `backend/`).

## 2. ML (optional — improves accuracy)

```bash
pip install -r ml/requirements.txt
python ml/realtime_demo.py                    # webcam demo with the rule-based classifier
python ml/collect_data.py --sign V --samples 200   # repeat for each sign
python ml/train.py                            # writes ml/model.joblib
```
Restart the backend — it automatically switches from rules to the trained model.

## 3. Frontend

```bash
cd frontend
npm install        # or bun install
echo "VITE_API_URL=http://localhost:8000" > .env   # optional: photo mode uses the Python backend
npm run dev
```
Live camera recognition runs in the browser (MediaPipe JS) for low latency; photo mode calls
the Python `/api/predict` when `VITE_API_URL` is set.

## Suggested team split (4 people)

1. **ML engineer** — `ml/`: collect data for every sign, train and evaluate the model, add new signs.
2. **Backend developer** — `backend/`: API, database, tests, deployment.
3. **Frontend developer** — `frontend/src/routes`: pages, camera, connecting to the API.
4. **UX / QA / docs** — Learn Signs content, testing with real users, presentation & report.

## Adding a new sign
Add it to `backend/app/signs.py` **and** `frontend/src/lib/signs.ts` (same id), collect data, retrain.
