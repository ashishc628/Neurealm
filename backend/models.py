from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class EmotionState(BaseModel):
    valence: float = 0.0
    arousal: float = 0.0
    top_emotions: List[str] = []
    raw: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    user_id: str
    message: str
    emotion: Optional[EmotionState] = None


class ChatResponse(BaseModel):
    reply: str
    suggested_exercise: Optional[Dict[str, Any]] = None
    safety_flag: bool = False


class ExerciseRequest(BaseModel):
    user_id: str
    exercise_type: str  # "nback", "breathing", "gratitude"
    level: int = 1


class ExerciseResponse(BaseModel):
    config: Dict[str, Any]
