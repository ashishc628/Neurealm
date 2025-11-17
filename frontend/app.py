import streamlit as st
import requests
import uuid
import time

BACKEND_URL = "https://YOUR-CLOUD-RUN-URL/chat"
EXERCISE_URL = "https://YOUR-CLOUD-RUN-URL/exercise"

st.set_page_config(page_title="NeuroGuide", layout="wide")

# Session state
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "current_exercise" not in st.session_state:
    st.session_state["current_exercise"] = None

st.title("🧠 NeuroGuide – Emotion-Aware AI Wellbeing & Brain Trainer")

col_chat, col_side = st.columns([3, 2])

with col_chat:
    st.subheader("Therapist Chat")

    chat_container = st.container()
    with chat_container:
        for role, text in st.session_state["messages"]:
            if role == "user":
                st.markdown(f"**You:** {text}")
            else:
                st.markdown(f"**Coach:** {text}")

    user_input = st.text_input("Share what's on your mind:", key="chat_input")

    if st.button("Send") and user_input.strip():
        # TODO: real Hume emotion state; for now dummy:
        emotion_payload = {
            "valence": 0.0,
            "arousal": 0.0,
            "top_emotions": [],
            "raw": {}
        }

        payload = {
            "user_id": st.session_state["user_id"],
            "message": user_input,
            "emotion": emotion_payload,
        }

        st.session_state["messages"].append(("user", user_input))

        with st.spinner("NeuroGuide is listening..."):
            resp = requests.post(BACKEND_URL, json=payload)
            data = resp.json()

        st.session_state["messages"].append(("assistant", data["reply"]))
        st.session_state["current_exercise"] = data.get("suggested_exercise")

        st.experimental_rerun()

with col_side:
    st.subheader("Emotion & Exercises")

    st.info("Webcam emotion detection via Hume will appear here in the final version.")

    if st.session_state["current_exercise"]:
        ex = st.session_state["current_exercise"]
        st.markdown("### Suggested activity")
        st.write(f"**{ex.get('description', ex.get('label', 'Exercise'))}**")
        st.json(ex)

    st.markdown("---")
    st.subheader("Quick Start")

    if st.button("Start N-back (1-back)"):
        payload = {
            "user_id": st.session_state["user_id"],
            "exercise_type": "nback",
            "level": 1,
        }
        resp = requests.post(EXERCISE_URL, json=payload)
        st.session_state["current_exercise"] = resp.json()["config"]
        st.experimental_rerun()

    if st.button("Start Breathing"):
        payload = {
            "user_id": st.session_state["user_id"],
            "exercise_type": "breathing",
            "level": 1,
        }
        resp = requests.post(EXERCISE_URL, json=payload)
        st.session_state["current_exercise"] = resp.json()["config"]
        st.experimental_rerun()

    if st.button("Start Gratitude Journaling"):
        payload = {
            "user_id": st.session_state["user_id"],
            "exercise_type": "gratitude",
            "level": 1,
        }
        resp = requests.post(EXERCISE_URL, json=payload)
        st.session_state["current_exercise"] = resp.json()["config"]
        st.experimental_rerun()

    # Show simple exercise UI
    ex = st.session_state.get("current_exercise")
    if ex:
        if ex["type"] == "breathing":
            st.markdown("#### Breathing Exercise")
            st.write("Inhale 4 seconds, hold 4 seconds, exhale 6 seconds.")
            st.write("Follow a simple 60-second timer below.")
            timer_placeholder = st.empty()
            for i in range(10, 0, -1):
                timer_placeholder.write(f"{i * 6} seconds remaining...")
                time.sleep(1)

        elif ex["type"] == "gratitude":
            st.markdown("#### Gratitude Journaling")
            for p in ex.get("prompts", []):
                st.markdown(f"- {p}")

        elif ex["type"] == "nback":
            st.markdown("#### N-back Working Memory Game (concept UI)")
            st.write(f"{ex['n']}-back sequence:")
            st.write(" ".join(ex["sequence"]))
            st.caption("For demo, imagine clicking when current letter matches the one from n steps ago.")
