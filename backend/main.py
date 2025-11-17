import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest, ChatResponse, ExerciseRequest, ExerciseResponse
from agents import TherapistAgent, ExerciseCoachAgent, SafetyAgent
from firestore_client import log_chat_event, log_exercise_result
from exercises import (
    build_nback_config,
    build_breathing_config,
    build_gratitude_config,
)

app = FastAPI(title="NeuroGuide Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

therapist_agent = TherapistAgent()
exercise_agent = ExerciseCoachAgent()
safety_agent = SafetyAgent()


@app.get("/")
def root():
    return {"status": "ok", "service": "neuroguide-backend"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    # 1) Safety
    if safety_agent.check(req.message):
        crisis_text = safety_agent.crisis_message()
        log_chat_event(
            req.user_id,
            req.message,
            crisis_text,
            req.emotion.dict() if req.emotion else {},
            safety_flag=True,
        )
        return ChatResponse(
            reply=crisis_text,
            suggested_exercise=None,
            safety_flag=True,
        )

    # 2) Normal therapist reply
    emotion_state = req.emotion.dict() if req.emotion else {}
    reply = therapist_agent.generate_reply(req.message, emotion_state)

    # 3) Exercise recommendation
    suggested_ex = exercise_agent.recommend_exercise(emotion_state)

    # Log to Firestore
    log_chat_event(
        req.user_id,
        req.message,
        reply,
        emotion_state,
        safety_flag=False,
    )

    return ChatResponse(
        reply=reply,
        suggested_exercise=suggested_ex,
        safety_flag=False,
    )


@app.post("/exercise", response_model=ExerciseResponse)
def exercise_endpoint(req: ExerciseRequest):
    if req.exercise_type == "nback":
        config = build_nback_config(level=req.level)
    elif req.exercise_type == "breathing":
        config = build_breathing_config()
    elif req.exercise_type == "gratitude":
        config = build_gratitude_config()
    else:
        config = {"type": req.exercise_type}

    # Example: log a dummy score of 0 now (front-end can later POST scores)
    log_exercise_result(
        user_id=req.user_id,
        exercise_type=req.exercise_type,
        score={"status": "started"},
    )

    return ExerciseResponse(config=config)
