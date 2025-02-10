import streamlit as st

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
        
        with st.chat_message("user"):
            st.write(f"👤 {prompt}")

        # Simulated bot response
        response = f"🤖 This is a response to: {prompt}"
        st.session_state.messages.append({"role": "assistant", "content": response, "icon": "🤖"})

        with st.chat_message("assistant"):
            st.write(response)
