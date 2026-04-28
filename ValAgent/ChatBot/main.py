import streamlit as st
import requests

CONTEXT_API_BASE = "http://localhost:8989"  # Context Manager base URL


def init_session():
    if "session_id" not in st.session_state:
        resp = requests.get(f"{CONTEXT_API_BASE}/new_session", timeout=30)
        resp.raise_for_status()
        st.session_state.session_id = resp.json()["session_id"]

    if "messages" not in st.session_state:
        st.session_state.messages = []


def main():
    st.set_page_config(page_title="VALAGENT Chatbot", page_icon="🤖")
    st.title("🤖 VALAGENT Chatbot")

    init_session()

    with st.sidebar:
        st.subheader("Settings")
        st.checkbox("Debug mode", value=False, key="debug")
        st.markdown(f"**Session ID:** `{st.session_state.session_id}`")

    # Show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask VALAGENT something...")

    if user_input:
        # Add user message to local history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        payload = {
            "session_id": st.session_state.session_id,
            "query": user_input,
            "debug": bool(st.session_state.get("debug", False)),
            # bearer_token removed – now handled via conversation content
        }

        try:
            resp = requests.post(
                f"{CONTEXT_API_BASE}/query",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("agent_response", "")
        except Exception as e:
            answer = f"Error talking to VALAGENT Context Manager: {e}"
            data = {}

        # Show assistant reply
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

        # Optional debug trace
        if st.session_state.get("debug", False) and data.get("debug_trace") is not None:
            with st.expander("Debug trace from orchestrator"):
                st.json(data["debug_trace"])


if __name__ == "__main__":
    main()
