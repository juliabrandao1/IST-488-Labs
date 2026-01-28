import streamlit as st
from openai import OpenAI
import fitz

def read_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text()
    return text

# Show title and description.
st.title("📄 Document Summarizer")
st.write( 
    "Upload a document below and get a summary powered by GPT!"
)
# Sidebar options
with st.sidebar:
    summary_type = st.selectbox(
        "Choose summary type:",
        ("Summarize in 100 words", "Summarize in 2 connecting paragraphs", "Summarize in 5 bullet points")
    )
    
    use_advanced_model = st.checkbox("Use advanced model")

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management

openai_api_key = st.secrets["OPENAI_API_KEY"]

    # Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)
try:
    client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role":"user","content":"What is 2+2?"}],
    max_tokens=10
)
    st.success("API Key is valid!")
except:
    st.error("Invalid API key. Please try again")
    st.stop()

# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .pdf)", type=("txt", "pdf")
)

if uploaded_file:

    # Process the uploaded file and question.
    file_extension = uploaded_file.name.split('.')[-1]
    if file_extension == 'txt':
        document = uploaded_file.read().decode()
    elif file_extension == 'pdf':
        document = read_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")
    
    messages = [
        {
            "role": "user",
            "content": f"Here's a document: {document} \n\n---\n\n {summary_type}",
        }
    ]

    if use_advanced_model:
        model_to_use = "gpt-4o"
    else:
        model_to_use = "gpt-4o-mini"

    stream = client.chat.completions.create(
        model=model_to_use,
        messages=messages,
        stream=True,
    )

    # Stream the response to the app using `st.write_stream`.
    st.write_stream(stream)