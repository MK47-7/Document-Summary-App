# Used AI code generation: Gemini 2.0 Flash


import fitz  # PyMuPDF
import requests
import streamlit as st
import google.generativeai as genai
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(filename="app_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Gemini API configuration
genai.configure(api_key="AIzaSyD1aD2SJt0X37T-Di6-sDUgFHHEfQE0IPY")

model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    generation_config={
        'temperature': 0.7,
        'max_output_tokens': 2048
    }
)

# Text extraction from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        text = ""
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        logging.info("PDF text extracted successfully.")
        return text
    except Exception as e:
        logging.error(f"PDF extraction error: {e}")
        return ""

# Text extraction from URL
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        logging.info("URL text extracted successfully.")
        return soup.get_text()
    except Exception as e:
        logging.error(f"URL fetch error: {e}")
        return ""

# Text trimming
def trim_text(text, max_chars=15000):
    return text[:max_chars] if len(text) > max_chars else text

# Summarize text
def summarize_text(text, style):
    if not text.strip():
        return "No document content to summarize."
    prompt = f"Summarize the following document in a {style} style:\n\n{trim_text(text)}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Summarization error: {e}")
        return "Error generating summary."

# Answer user questions
def answer_questions(text, question):
    if not text.strip() or not question.strip():
        return "Missing document or question."
    prompt = f"""Answer the following question based only on this document:

Document:
{trim_text(text)}

Question:
{question}

Answer only from the document."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Q&A error: {e}")
        return "Error generating answer."

# Simplify section
def simplify_text_section(text, section_prompt):
    if not text.strip() or not section_prompt.strip():
        return "Missing document or section to simplify."
    prompt = f"""Simplify this section for a younger audience:

Topic:
{section_prompt}

Document:
{trim_text(text)}"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Simplification error: {e}")
        return "Error generating simplified content."

# Streamlit UI
st.title("📚 Interactive Tutor - Document QA and Summarizer")
input_type = st.radio("Choose input method:", ("Upload File", "Enter URL"))
summary_style = st.selectbox("Choose summary style:", ("short", "detailed", "bullet points"))
text_content = ""

if input_type == "Upload File":
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            text_content = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "text/plain":
            text_content = uploaded_file.read().decode("utf-8")
        else:
            st.error("Unsupported file type.")

elif input_type == "Enter URL":
    url = st.text_input("Enter a URL")
    if url:
        text_content = extract_text_from_url(url)

if text_content:
    st.subheader("Summary")
    if st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            summary = summarize_text(text_content, summary_style)
            st.write(summary)

    st.subheader("Ask a Question")
    question = st.text_input("Enter your question:", help="Type your question here, then click the 'Answer Question' button.")
    if st.button("Answer Question") and question:
        with st.spinner("Getting answer..."):
            answer = answer_questions(text_content, question)
            st.write(answer)

    st.subheader("Simplify Content")
    section_prompt = st.text_area("Enter the section or topic to simplify:", help="Type the section to simplify, then click the 'Simplify' button.")
    if st.button("Simplify") and section_prompt:
        with st.spinner("Simplifying..."):
            simplified = simplify_text_section(text_content, section_prompt)
            st.write(simplified)
