import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Chat — MomentumLens", layout="wide")
st.title("Chat with MomentumLens AI")

match_id = st.session_state.get("match_id")
if match_id:
    st.info(f"Chatting in context of match: **{match_id}**")
else:
    st.warning("No match loaded. Go to the Dashboard first to load a match, or ask general questions below.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about the match, tactics, or momentum shifts...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = {
                "match_id": match_id,
                "message": user_input,
                "history": st.session_state.chat_history[:-1],
            }
            r = requests.post(f"{API_BASE}/chat", json=payload)
            if r.status_code == 200:
                reply = r.json()["reply"]
            elif r.status_code == 503:
                reply = "⚠️ IBM Granite is not configured. Please set WatsonX credentials in .env to enable AI chat."
            else:
                reply = f"Error: {r.text}"
        st.markdown(reply)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
