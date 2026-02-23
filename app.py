import streamlit as st
from main import get_response, learn, identity, load_user_memory, save_user_memory
from datetime import datetime
import re
import tempfile
import asyncio
import edge_tts

VOICE = "en-US-JennyNeural"

# ---------- TTS FUNCTIONS ---------- #
async def generate_audio(text):
    """Generate TTS audio file and return path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        path = f.name
    communicate = edge_tts.Communicate(text=text, voice=VOICE)
    await communicate.save(path)
    return path

def speak_streamlit(text):
    """Generate TTS and play automatically using st.audio"""
    path = asyncio.run(generate_audio(text))
    st.audio(path, format="audio/mp3", start_time=0)

# ---------- PAGE SETUP ---------- #
st.set_page_config(page_title="Quinela", page_icon="🤖")
st.markdown(
    f"<h1 style='text-align:center; font-size:70px; color:black'>{identity['name']} 🤖</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align:center; color:gray'>Your private learning AI assistant</h3>", 
    unsafe_allow_html=True
)

# ---------- SESSION STATE ---------- #
if "teach_mode" not in st.session_state:
    st.session_state.teach_mode = False
    st.session_state.last_question = ""
    st.session_state.last_reply = ""
    st.session_state.qa_item = None
    st.session_state.user_email = None

# ---------- USER LOGIN ---------- #
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

# ---------- LOAD PRIVATE MEMORY ---------- #
knowledge, path = load_user_memory(email)

# ---------- USER INPUT ---------- #
user_input = st.text_input("You:", placeholder="Type something...")

# ---------- SEND BUTTON ---------- #
if st.button("Send") and user_input.strip():
    reply, qa_item, needs_teaching = get_response(user_input, knowledge, path)
    st.session_state.last_reply = reply
    st.session_state.qa_item = qa_item

    st.markdown(f"**Quinela:** {reply}")

    # Automatic speech (works on web & mobile)
    speak_streamlit(reply)

    # Teach mode if unknown
    if needs_teaching:
        st.session_state.teach_mode = True
        st.session_state.last_question = user_input
    else:
        st.session_state.teach_mode = False

# ---------- MANUAL CORRECTION ---------- #
st.markdown("### Correction (only if I was wrong)")
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

# ---------- TEACHING MODE ---------- #
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