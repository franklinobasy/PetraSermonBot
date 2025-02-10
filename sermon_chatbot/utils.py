import streamlit as st

def sermon_selection():
    st.title("📜 Select a Sermon to Chat With")
    
    # Dummy sermons list (can be replaced with real data)
    sermons = ["Faith and Patience", "The Power of Prayer", "Walking in Love"]
    
    selected_sermon = st.selectbox("Choose a sermon:", sermons)

    if st.button("🚀 Start Chat"):
        st.session_state.selected_sermon = selected_sermon
        st.session_state.messages = [
            {"role": "assistant", "content": f"You are now chatting with '{selected_sermon}'. Ask your questions!", "icon": "🤖"}
        ]
        st.rerun()
