import streamlit as st
from sermon_chatbot.utils import sermon_selection
from sermon_chatbot.chat import chat_interface

def main():
    st.set_page_config(page_title="Petra Sermon Bot", page_icon="📖", layout="centered")

    # Navigation between sermon selection and chat interface
    if "selected_sermon" not in st.session_state:
        sermon_selection()
    else:
        chat_interface()
        if st.button("🔙 Back to Sermon Selection"):
            del st.session_state["selected_sermon"]
            st.session_state.messages = []
            st.rerun()
