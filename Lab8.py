import streamlit as st
from openai import OpenAI
import requests

st.title("Image Captioning Bot")
st.write("Provide the bot with an image URL or file upload and it will write captions for you!")

# Create OpenAI client
client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)

# Initialize session state for URL response
if "url_response" not in st.session_state:
    st.session_state.url_response = None

# --- Part A: Image URL Input ---
st.subheader("Image URL Input")
st.write("Enter your image URL here:")

url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")

if st.button("Generate Captions for Image URL"):
    if url:
        with st.spinner("Generating captions..."):
            url_response = client.chat.completions.create(
                model="gpt-4.1-mini",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": url, "detail": "auto"}},
                        {"type": "text", "text": "Describe the image in at least 3 sentences. Write five different captions for this image."
                         " Captions must vary in length, minimum one word but be no longer than 2 sentences."
                         " Captions should vary in tone, such as, but not limited to funny, intellectual, and aesthetic."}
                    ]
                }]
            )
            st.session_state.url_response = url_response.choices[0].message.content

if st.session_state.url_response:
    st.image(url)
    st.write(st.session_state.url_response)