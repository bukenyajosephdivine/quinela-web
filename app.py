import asyncio
from speaker import speak
import streamlit as st
from main import get_response, learn, identity, load_user_memory, save_user_memory
from datetime import datetime

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="Quinela", page_icon="🤖")
st.title(f"{identity['name']} 🤖")
st.write("Your learning AI assistant")

# ---------- SESSION STATE ----------
if "teach_mode" not in st.session_state:
    st.session_state.teach_mode = False
    st.session_state.last_question = ""
    st.session_state.last_reply = ""
    st.session_state.qa_item = None

# ---------- USER LOGIN ----------
user_name = st.text_input("Enter your name:", "")
if not user_name:
    st.warning("Please enter your name to continue")
    st.stop()

# Load per-user memory
knowledge, path = load_user_memory(user_name)

# ---------- USER INPUT ----------
user_input = st.text_input("You:", placeholder="Type something...")

# ---------- SEND BUTTON ----------
if st.button("Send") and user_input.strip():
    reply, qa_item, needs_teaching = get_response(user_input, knowledge, path)
    st.session_state.last_reply = reply
    st.session_state.qa_item = qa_item

    st.markdown(f"**Quinela:** {reply}")
    asyncio.run(speak(reply))

    # If Quinela does not know, enter teach mode
    if needs_teaching:
        st.session_state.teach_mode = True
        st.session_state.last_question = user_input
    else:
        st.session_state.teach_mode = False

# ---------- MANUAL CORRECTION ----------
# Only correct manually if you know the answer is wrong
wrong_answer = st.text_input("If my answer was wrong, type the correct answer here:", key="correction_input")
if wrong_answer.strip() and st.session_state.qa_item:
    st.session_state.qa_item["answer"] = wrong_answer
    st.session_state.qa_item["last_used"] = datetime.now().isoformat()
    st.session_state.qa_item["confidence"] = max(1, st.session_state.qa_item.get("confidence", 1) - 1)
    save_user_memory(path, knowledge)
    st.success("✅ I have corrected myself!")
    st.session_state.qa_item = None  # Reset so you don't correct same answer twice

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