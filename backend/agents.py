from typing import Dict, Any
import os
import google.generativeai as genai

from exercises import (
    build_nback_config,
    build_breathing_config,
    build_gratitude_config,
)


# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class TherapistAgent:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def generate_reply(self, message: str, emotion_state: Dict[str, Any]) -> str:
        emo_text = ""
        if emotion_state:
            emo_text = (
                f"\nDetected emotional state (from webcam):\n"
                f"- Valence: {emotion_state.get('valence')}\n"
                f"- Arousal: {emotion_state.get('arousal')}\n"
                f"- Top emotions: {emotion_state.get('top_emotions')}\n"
            )

        prompt = f"""
You are an empathetic mental wellbeing coach called NeuroGuide.
You are NOT a doctor or therapist and you NEVER diagnose or give medical advice.
You:
- listen kindly,
- validate the user's feelings,
- offer simple CBT-style coping ideas,
- suggest small actionable steps,
- keep answers under 6–8 sentences.

If the user seems anxious or sad, slow down, be gentle, and reassure them.

{emo_text}

User: {message}
Coach:
"""

        response = self.model.generate_content(prompt)
        return (response.text or "").strip()


class ExerciseCoachAgent:
    def recommend_exercise(self, emotion_state: Dict[str, Any]) -> Dict[str, Any]:
        valence = emotion_state.get("valence", 0.0)
        arousal = emotion_state.get("arousal", 0.0)

        # Negative & high arousal -> calm down
        if valence < -0.3 and arousal > 0.3:
            return build_breathing_config()

        # Negative & low arousal -> gratitude / activation
        if valence < -0.3 and arousal <= 0.3:
            return build_gratitude_config()

        # Otherwise -> cognitive training
        return build_nback_config(level=1)


class SafetyAgent:
    RISK_KEYWORDS = [
        "suicide", "kill myself", "end my life", "want to die",
        "kill someone", "hurt someone", "self harm", "self-harm",
        "cut myself", "overdose"
    ]

    def check(self, message: str) -> bool:
        msg = message.lower()
        return any(k in msg for k in self.RISK_KEYWORDS)

    def crisis_message(self) -> str:
        return (
            "I'm really glad you reached out. "
            "I’m an AI wellbeing coach and **not** a crisis service or a doctor.\n\n"
            "If you're in immediate danger or thinking about harming yourself, "
            "please contact your local emergency number right now, "
            "or reach out to a trusted person or crisis helpline in your country.\n\n"
            "You don’t have to go through this alone."
        )
