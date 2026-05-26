import re
from typing import List

import streamlit as st
from pypdf import PdfReader


def extract_text(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    text_parts: List[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)
    return "\n".join(text_parts)


def generate_summary(text: str, max_sentences: int = 3) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return "(No text to summarize)"
    summary = " ".join(sentences[:max_sentences])
    return summary


def answer_question(context: str, question: str) -> str:
    if not question or not context:
        return "Please provide both a PDF and a question."

    question_tokens = [t.lower() for t in re.findall(r"\w+", question) if len(t) > 2]
    sentences = re.split(r'(?<=[.!?])\s+', context)

    matches: List[str] = []
    for s in sentences:
        sl = s.lower()
        if all(tok in sl for tok in question_tokens):
            matches.append(s.strip())

    if matches:
        return "\n\n".join(matches[:3])

    # Fallback: return the most relevant sentence by keyword overlap
    best = None
    best_score = 0
    for s in sentences:
        sl = s.lower()
        score = sum(1 for tok in question_tokens if tok in sl)
        if score > best_score:
            best_score = score
            best = s

    if best_score > 0 and best:
        return best.strip()

    # Last resort: return an excerpt
    return context[:1000] + ("..." if len(context) > 1000 else "")


def main():
    st.title("PDF QA & Summary (local)")

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if not uploaded_file:
        st.info("Upload a PDF to get started.")
        return

    st.success("PDF uploaded successfully")

    with st.spinner("Reading PDF..."):
        try:
            pdf_text = extract_text(uploaded_file)
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")
            return

    st.subheader("PDF Preview")
    st.write(pdf_text[:2000])

    # Summary
    if st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            summary = generate_summary(pdf_text)
        st.subheader("Summary")
        st.write(summary)

    # QA
    st.subheader("Ask Questions")
    user_question = st.text_input("Enter your question")
    if st.button("Get Answer"):
        with st.spinner("Finding answer..."):
            answer = answer_question(pdf_text, user_question)
        st.subheader("Answer")
        st.write(answer)


if __name__ == "__main__":
    main()
