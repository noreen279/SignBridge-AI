"""SignBridge API — run with: uvicorn app.main:app --reload"""
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import db
from .signs import SIGN_IDS, SIGNS

app = FastAPI(title="SignBridge API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
db.init()


class SignEvent(BaseModel):
    user_id: str
    sign_id: str


class QuizEvent(SignEvent):
    correct: bool


def _check(sign_id: str) -> None:
    if sign_id not in SIGN_IDS:
        raise HTTPException(400, f"Unknown sign '{sign_id}'")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/signs")
def signs():
    return SIGNS


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    from .detector import predict_image  # loaded lazily (heavy imports)

    data = await file.read()
    if not data or len(data) > 10 * 1024 * 1024:
        raise HTTPException(400, "Image must be between 1 byte and 10 MB")
    try:
        return predict_image(data)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/progress/detection")
def detection(e: SignEvent):
    _check(e.sign_id)
    db.add_detection(e.user_id, e.sign_id)
    return {"ok": True}


@app.post("/api/progress/quiz")
def quiz(e: QuizEvent):
    _check(e.sign_id)
    db.add_quiz(e.user_id, e.sign_id, e.correct)
    return {"ok": True}


@app.post("/api/progress/learned")
def learned(e: SignEvent):
    _check(e.sign_id)
    return {"learned": db.toggle_learned(e.user_id, e.sign_id)}


@app.get("/api/progress/{user_id}")
def get_progress(user_id: str):
    return db.progress(user_id)
