import streamlit as st
from openai import OpenAI
import chromadb
import fitz  # PyMuPDF

# Show title
st.title("Lab 4 - RAG Chatbot")

# Create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

# --- Function to read a PDF file and return its text ---
def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

# --- Function to create the ChromaDB collection ---
def create_vector_db():
    # Create a ChromaDB client (in-memory)
    chroma_client = chromadb.Client()

    # Create the collection with OpenAI embeddings
    from chromadb.utils import embedding_functions
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=st.secrets["OPENAI_API_KEY"],
        model_name="text-embedding-3-small"
    )

    collection = chroma_client.get_or_create_collection(
        name="Lab4Collection",
        embedding_function=openai_ef
    )

    # List of PDF files
    pdf_files = [
        "docs/IST 195 Syllabus - Information Technologies.pdf",
        "docs/IST 256 Syllabus - Intro to Python for the Information Profession.pdf",
        "docs/IST 314 Syllabus - Interacting with AI.pdf",
        "docs/IST 343 Syllabus - Data in Society.pdf",
        "docs/IST 387 Syllabus - Introduction to Applied Data Science.pdf",
        "docs/IST 418 Syllabus - Big Data Analytics.pdf",
        "docs/IST 488 Syllabus - Building Human-Centered AI Applications.pdf",
    ]

    # Read each PDF and add to the collection
    documents = []
    ids = []
    metadatas = []

    for pdf_file in pdf_files:
        text = read_pdf(pdf_file)
        documents.append(text)
        # Use the filename (without path) as the ID
        filename = pdf_file.split("/")[-1]
        ids.append(filename)
        metadatas.append({"source": filename})

    # Add all documents to the collection
    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )

    return collection

# --- Only create the vector DB once ---
if "Lab4_VectorDB" not in st.session_state:
    with st.spinner("Creating vector database..."):
        st.session_state.Lab4_VectorDB = create_vector_db()
    st.success("Vector database created!")
else:
    st.success("Vector database already loaded!")

# --- Initialize chat history ---
if "lab4_messages" not in st.session_state:
    st.session_state.lab4_messages = []

# --- Display chat history ---
for message in st.session_state.lab4_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat input ---
if prompt := st.chat_input("Ask a question about IST courses..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to history
    st.session_state.lab4_messages.append({"role": "user", "content": prompt})

    # Search the vector database for relevant documents
    results = st.session_state.Lab4_VectorDB.query(
        query_texts=[prompt],
        n_results=3
    )

    # Get the matching document texts and names
    context = ""
    sources = []
    for i in range(len(results['ids'][0])):
        doc_name = results['ids'][0][i]
        doc_text = results['documents'][0][i]
        sources.append(doc_name)
        context += f"\n--- From {doc_name} ---\n{doc_text}\n"

    # Build the prompt with RAG context
    system_message = f"""You are a helpful assistant that answers questions about IST courses at Syracuse University. 
Use the following course syllabus information to answer the user's question. 
If you are using information from the provided syllabi, clearly state which course(s) you are referencing.
If the question cannot be answered from the provided information, say so clearly.

COURSE INFORMATION:
{context}"""

    # Send to OpenAI
    client = st.session_state.client
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    # Display assistant response
    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    # Add assistant response to history
    st.session_state.lab4_messages.append({"role": "assistant", "content": response})