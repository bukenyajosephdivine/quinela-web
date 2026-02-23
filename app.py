import streamlit as st
import re
from datetime import datetime
import asyncio
import tempfile
import os

from main import get_response, learn, identity, load_user_memory, save_user_memory
import edge_tts

# ---------- VOICE CONFIG ----------
VOICE = "en-US-JennyNeural"

async def generate_speech_bytes(text):
    """Generate speech bytes from text using edge-tts"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        path = f.name
    communicate = edge_tts.Communicate(text=text, voice=VOICE)
    await communicate.save(path)
    with open(path, "rb") as f:
        data = f.read()
    os.remove(path)
    return data

def speak_st(text):
    """Speak automatically in Streamlit"""
    mp3_bytes = asyncio.run(generate_speech_bytes(text))
    st.audio(mp3_bytes, format="audio/mp3", start_time=0)

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="Quinela", page_icon="🤖", layout="centered")

# ---------- BACKGROUND & STYLING ----------
background_url = "https://images.unsplash.com/photo-1607746882042-944635dfe10e?auto=format&fit=crop&w=1950&q=80"  # Example background
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-position: center;
    }}
    .chat-box {{
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }}
    .user-box {{
        background-color: rgba(0, 0, 0, 0.3);
        color: white;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title(f"<span style='color:white'>{identity['name']} 🤖</span>", unsafe_allow_html=True)
st.write("<span style='color:white'>Your private learning AI assistant</span>", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "teach_mode" not in st.session_state:
    st.session_state.teach_mode = False
    st.session_state.last_question = ""
    st.session_state.last_reply = ""
    st.session_state.qa_item = None
    st.session_state.user_email = None
    st.session_state.chat_history = []

# ---------- USER LOGIN (GMAIL) ----------
email = st.text_input("Login with your Gmail:", placeholder="example@gmail.com")

def is_valid_gmail(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email)

if not email:
    st.warning("Please enter your Gmail to continue")
    st.stop()

if not is_valid_gmail(email):
    st.error("Please enter a valid Gmail address")
    st.stop()

st.session_state.user_email = email

# ---------- LOAD PRIVATE MEMORY ----------
knowledge, path = load_user_memory(email)

# ---------- USER INPUT ----------
user_input = st.text_input("You:", placeholder="Type something...")

# ---------- SEND BUTTON ----------
if st.button("Send") and user_input.strip():
    reply, qa_item, needs_teaching = get_response(user_input, knowledge, path)

    st.session_state.last_reply = reply
    st.session_state.qa_item = qa_item

    st.session_state.chat_history.append({"user": user_input, "bot": reply})

    # Display chat
    for chat in st.session_state.chat_history[::-1]:
        st.markdown(f"<div class='user-box'>{chat['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-box'>{chat['bot']}</div>", unsafe_allow_html=True)

    speak_st(reply)  # Auto-speaking

    if needs_teaching:
        st.session_state.teach_mode = True
        st.session_state.last_question = user_input
    else:
        st.session_state.teach_mode = False

# ---------- MANUAL CORRECTION ----------
st.markdown("<span style='color:white'>### Correction (only if I was wrong)</span>", unsafe_allow_html=True)
wrong_answer = st.text_input(
    "Type the correct answer here (optional):",
    key="correction_input"
)

if wrong_answer.strip() and st.session_state.qa_item:
    st.session_state.qa_item["answer"] = wrong_answer
    st.session_state.qa_item["last_used"] = datetime.now().isoformat()
    st.session_state.qa_item["confidence"] = max(
        1, st.session_state.qa_item.get("confidence", 1) - 1
    )
    save_user_memory(path, knowledge)
    st.success("✅ I have corrected myself!")
    st.session_state.qa_item = None

# ---------- TEACHING MODE ----------
if st.session_state.teach_mode:
    st.info("Teach Quinela the correct answer 👇")
    answer = st.text_input("Correct answer:", key="teach_input")

    if st.button("Teach"):
        if answer.strip():
            learn(st.session_state.last_question, answer, knowledge, path)
            st.success("✅ I have learned this!")
            st.session_state.teach_mode = False
        else:
            st.warning("Please enter an answer.")