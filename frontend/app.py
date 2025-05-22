import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

API_PORT = os.getenv("API_PORT", "8000")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "5000")
API_URL = f"http://api:{API_PORT}/chat"

st.set_page_config(page_title="Support Chatbot", server_port=int(FRONTEND_PORT))
st.title("🛠️ Support Chatbot")

print(f"[INFO] Frontend is running. Port: {FRONTEND_PORT}")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = "demo-user"

# Clear memory button
if st.button("🧹 Clear memory"):
    res = requests.post(API_URL, json={
        "session_id": st.session_state.session_id,
        "user_message": "clear"
    })
    st.session_state.messages = []
    st.success("Memory cleared.")

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a question about support issues..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        res = requests.post(API_URL, json={
            "session_id": st.session_state.session_id,
            "user_message": prompt
        })
        res.raise_for_status()
        answer = res.json()["response"]
    except Exception as e:
        answer = f"❌ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
