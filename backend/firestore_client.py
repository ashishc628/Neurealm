import os
from typing import Dict, Any
from google.cloud import firestore

# Make sure GOOGLE_CLOUD_PROJECT or GOOGLE_APPLICATION_CREDENTIALS is set
_db = None

def get_db():
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db


def log_chat_event(user_id: str, message: str, reply: str, emotion: Dict[str, Any], safety_flag: bool):
    db = get_db()
    doc = {
        "user_id": user_id,
        "user_message": message,
        "assistant_reply": reply,
        "emotion": emotion,
        "safety_flag": safety_flag,
        "type": "chat",
        "timestamp": firestore.SERVER_TIMESTAMP,
    }
    db.collection("neuroguide_events").add(doc)


def log_exercise_result(user_id: str, exercise_type: str, score: Dict[str, Any]):
    db = get_db()
    doc = {
        "user_id": user_id,
        "exercise_type": exercise_type,
        "score": score,
        "type": "exercise",
        "timestamp": firestore.SERVER_TIMESTAMP,
    }
    db.collection("neuroguide_events").add(doc)
