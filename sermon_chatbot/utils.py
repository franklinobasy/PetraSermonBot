import streamlit as st

from petrabot.reasoning.agents import ReactAgent
from sermon_chatbot.backend import get_all_sermon_titles, initialize_chat_requirements, process_streamlit_messages_to_petrasermonbot_chat_history, update_system_prompt

def sermon_selection():
    st.title("📜 Select a Sermon to Chat With")
    
    # Dummy sermons list (can be replaced with real data)
    sermons = get_all_sermon_titles()
    
    selected_sermon = st.selectbox("Choose a sermon:", sermons)

    if st.button("🚀 Start Chat"):
        st.session_state.selected_sermon = selected_sermon
        st.session_state.messages = [
            {"role": "assistant", "content": f"You are now chatting with '{selected_sermon}'. Ask your questions!", "icon": "🤖"}
        ]
        st.session_state.runtime_data = initialize_chat_requirements()
        st.session_state.runtime_data["chat_history"] = process_streamlit_messages_to_petrasermonbot_chat_history(
            messages=st.session_state.messages,
            chat_history=st.session_state.runtime_data["chat_history"]
        )
        agent = ReactAgent(
            llm_metadata = st.session_state.runtime_data["llm_metadata"],
            tools=st.session_state.runtime_data["tools"]
        )
        agent = update_system_prompt(agent, title=selected_sermon)
        st.session_state.runtime_data["agent"] = agent
        st.rerun()
