import streamlit as st
from openai import OpenAI
from pydantic import BaseModel

class ResearchSummary(BaseModel):
    main_answer: str
    key_facts: list[str]
    source_hint: str

st.title("Lab 6: AI Research Agent")

# Set up OpenAI client
if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)

structured_mode = st.sidebar.checkbox("Return structured summary")

# Get user question
user_question = st.text_input("Ask a question:")

if user_question:
    if structured_mode:
        response = st.session_state.openai_client.responses.parse(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=user_question,
            tools=[{"type": "web_search_preview"}],
            text_format=ResearchSummary
        )
        result = response.output_parsed
        st.markdown(result.main_answer)
        st.subheader("Key Facts:")
        for fact in result.key_facts:
            st.write(f"- {fact}")
        st.caption(result.source_hint)
    else:
        response = st.session_state.openai_client.responses.create(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=user_question,
            tools=[{"type": "web_search_preview"}]
        )
        st.markdown(response.output_text)
        
    st.session_state.last_response_id = response.id

# Follow-up question
follow_up = st.text_input("Ask a follow-up question:")

st.caption("🔍 This agent has web search enabled for up-to-date answers.")

if follow_up and 'last_response_id' in st.session_state:
    follow_up_response = st.session_state.openai_client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful research assistant. Cite your sources.",
        input=follow_up,
        tools=[{"type": "web_search_preview"}],
        previous_response_id=st.session_state.last_response_id
    )

    st.markdown(follow_up_response.output_text)

