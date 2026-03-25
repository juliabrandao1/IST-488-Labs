import streamlit as st
from openai import OpenAI

st.title("Lab 6: AI Research Agent")

# Set up OpenAI client
if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)

    