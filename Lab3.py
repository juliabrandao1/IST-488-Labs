import streamlit as st
from openai import OpenAI

# Show title
st.title("Lab 3 - Chatbot")

# Create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

# Initialize chat history
# Initialize chat history with system prompt
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant. Answer questions in a way that a 10-year-old can understand. After answering each question, ask 'Do you want more info?' If the user says yes, provide more information and ask again. If the user says no, ask what else you can help with."}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Get response from OpenAI
    client = st.session_state.client
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages[:1] + st.session_state.messages[-4:],
        stream=True
    )
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})