import time
import streamlit as st

from petrabot.reasoning.agents import ReactAgent
from petrabot.utils.agent_utils import update_chat_history
from sermon_chatbot.backend import process_streamlit_messages_to_petrasermonbot_chat_history

def chat_interface():
    st.title("🗣️ Chat with the Sermon")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(f"{message['icon']} {message['content']}")

    # User input
    if prompt := st.chat_input("Ask a question about the sermon..."):
        # Store user message
        st.session_state.messages.append({"role": "user", "content": prompt, "icon": "👤"})
        st.session_state.runtime_data["chat_history"] = process_streamlit_messages_to_petrasermonbot_chat_history(
            messages=st.session_state.messages,
            chat_history=st.session_state.runtime_data["chat_history"]
        )
        
        with st.chat_message("user"):
            st.write(f"👤 {prompt}")

        # Get the full response first
        response = AI(prompt, st.session_state.runtime_data)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for char in response:
                full_response += char
                message_placeholder.write(full_response + "▌")  # Cursor effect
                time.sleep(0.02)  # Simulate typing delay

            message_placeholder.write(full_response)

        # Store assistant message
        st.session_state.messages.append({"role": "assistant", "content": full_response, "icon": "🤖"})


def AI(prompt, runtime_data):
    agent: ReactAgent = runtime_data["agent"]
    response = agent.run(
        user_msg=prompt,
        chat_history=runtime_data["chat_history"]
    )
    
    if response == "":
        response = "I'm sorry, I don't understand. Please ask another question."
        
    update_chat_history(
        history=runtime_data["chat_history"],
        role="model",
        msg=prompt
    )
    
    return response

