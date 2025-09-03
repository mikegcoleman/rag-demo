import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

API_PORT = os.getenv("API_PORT", "8000")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "8501")
API_HOST = os.getenv("API_HOST", "api")   

API_URL = f"http://api:{API_PORT}/chat"  # Calls local API server w/ Apple Silicon

st.set_page_config(page_title="Support Chatbot")
st.title("🛠️ Support Chatbot")

print(f"[INFO] Frontend is running. Port: {FRONTEND_PORT}")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = "demo-user"
if "debug_info" not in st.session_state:
    st.session_state.debug_info = []

# Sidebar settings
st.sidebar.header("Settings")
use_rag = st.sidebar.checkbox("🧠 Use RAG for context", value=True)
show_context = st.sidebar.checkbox("🪄 Show prompt details", value=True)

# Clear memory button
if st.sidebar.button("🧹 Clear memory"):
    try:
        res = requests.post(API_URL, json={
            "session_id": st.session_state.session_id,
            "user_message": "clear",
            "use_rag": use_rag,
            "debug": show_context
        })
        res.raise_for_status()
        st.session_state.messages = []
        st.session_state.debug_info = []
        st.sidebar.success("Memory cleared.")
    except Exception as e:
        st.sidebar.error(f"Failed to clear memory: {e}")

# Show chat history
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and show_context and i < len(st.session_state.debug_info):
            debug = st.session_state.debug_info[i]
            with st.expander("🔎 Show reasoning trace"):
                st.markdown("**Prompt:**")
                st.code(debug.get("prompt", ""), language="text")
                st.markdown("**History:**")
                st.code(debug.get("history", ""), language="text")
                st.markdown("**Context:**")
                st.code(debug.get("context", ""), language="text")

# Chat input
if prompt := st.chat_input("Ask a question about support issues..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        print(f"[INFO] Sending request to API: {API_URL}")
        res = requests.post(API_URL, json={
            "session_id": st.session_state.session_id,
            "user_message": prompt,
            "use_rag": use_rag,
            "debug": show_context
        })
        res.raise_for_status()
        result = res.json()
        answer = result["response"]
        debug_info = {
            "prompt": result.get("prompt"),
            "history": result.get("history"),
            "context": result.get("context")
        }
    except Exception as e:
        answer = f"❌ Error: {e}"
        debug_info = {}

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.debug_info.append(debug_info)
    with st.chat_message("assistant"):
        st.markdown(answer)
        if show_context and debug_info:
            with st.expander("🔎 Show reasoning trace"):
                st.markdown("**Prompt:**")
                st.code(debug_info.get("prompt", ""), language="text")
                # st.markdown("**History:**")
                # st.code(debug_info.get("history", ""), language="text")
                # st.markdown("**Context:**")
                # st.code(debug_info.get("context", ""), language="text")
