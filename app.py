import streamlit as st
from main import get_response, learn, identity

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="Quinela", page_icon="🤖")
st.title(f"{identity['name']} 🤖")
st.write("Your learning AI assistant")

# ---------- SESSION STATE ----------
if "teach_mode" not in st.session_state:
    st.session_state.teach_mode = False
    st.session_state.last_question = ""
    st.session_state.last_reply = ""

# ---------- USER INPUT ----------
user_input = st.text_input("You:", placeholder="Type something...")

# ---------- SEND BUTTON ----------
if st.button("Send") and user_input.strip():
    reply, needs_teaching = get_response(user_input)
    st.session_state.last_reply = reply

    st.markdown(f"**Quinela:** {reply}")

    if needs_teaching:
        st.session_state.teach_mode = True
        st.session_state.last_question = user_input
    else:
        st.session_state.teach_mode = False

# ---------- TEACHING MODE ----------
if st.session_state.teach_mode:
    st.info("Teach Quinela the correct answer 👇")
    answer = st.text_input("Correct answer:")

    if st.button("Teach"):
        if answer.strip():
            learn(st.session_state.last_question, answer)
            st.success("✅ I have learned this!")
            st.session_state.teach_mode = False
        else:
            st.warning("Please enter an answer.")