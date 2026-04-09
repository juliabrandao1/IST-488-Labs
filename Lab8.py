import streamlit as st
from openai import OpenAI
import requests

st.title("Image Captioning Bot")
st.write("Provide the bot with an image URL or file upload and it will write captions for you!")

# Create OpenAI client
client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)
