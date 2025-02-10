import streamlit as st

def set_styles():
    st.markdown("""
        <style>
            body {
                font-family: 'Arial', sans-serif;
            }
            .stChatMessage {
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
                max-width: 80%;
            }
            .stChatMessage.user {
                background-color: #0084ff;
                color: white;
                align-self: flex-end;
                text-align: right;
            }
            .stChatMessage.assistant {
                background-color: #f1f0f0;
                color: black;
                align-self: flex-start;
                text-align: left;
            }
            [data-testid="stChatInput"] > div {
                border-radius: 10px;
                background-color: #2b2b2b;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)
