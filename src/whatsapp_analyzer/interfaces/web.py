"""Streamlit web UI for WhatsApp Chat Analyzer."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from whatsapp_analyzer.analyzer.core import ChatAnalyzer
from whatsapp_analyzer.models.analysis import AnalysisResult


def main():
    st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon="💬", layout="wide")
    st.title("💬 WhatsApp Group Chat Analyzer")
    st.caption("Local LLM-powered analysis using Ollama — your data never leaves your machine.")

    # ── Sidebar settings ──
    with st.sidebar:
        st.header("Settings")
        model = st.text_input("Ollama Model", value="llama3.1:8b")
        host = st.text_input("Ollama Host", value="http://localhost:11434")

        st.header("Filters")
        participant = st.text_input("Participant (optional)", placeholder="e.g. Alice")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=None)
        with col2:
            end_date = st.date_input("End Date", value=None)

    # ── Input tabs ──
    tab_paste, tab_file, tab_screenshot = st.tabs(
        ["📋 Paste Text", "📄 Upload File", "📸 Upload Screenshots"]
    )

    source: str | None = None
    temp_path: str | None = None

    with tab_paste:
        pasted = st.text_area(
            "Paste WhatsApp chat text here",
            height=300,
            placeholder="12/01/2024, 09:00 - Alice: Hello everyone!",
        )
        if pasted.strip():
            source = pasted.strip()

    with tab_file:
        uploaded_file = st.file_uploader(
            "Upload a chat export file",
            type=["txt", "pdf", "docx"],
        )
        if uploaded_file is not None:
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name
            source = temp_path

    with tab_screenshot:
        uploaded_images = st.file_uploader(
            "Upload WhatsApp screenshot(s)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
        )
        if uploaded_images:
            # Use the first image for now; multi-image could be extended
            img = uploaded_images[0]
            suffix = Path(img.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(img.read())
                temp_path = tmp.name
            source = temp_path
            if len(uploaded_images) > 1:
                st.info(
                    f"Processing first screenshot. Multi-image merging is planned for a future release."
                )

    # ── Analysis buttons ──
    col_parse, col_analyze = st.columns(2)

    with col_parse:
        do_parse = st.button("🔍 Parse Only (no LLM)", disabled=source is None)

    with col_analyze:
        do_analyze = st.button(
            "🚀 Full Analysis", type="primary", disabled=source is None
        )

    if source is None:
        st.info("Paste text or upload a file to get started.")
        return

    analyzer = ChatAnalyzer(model=model, host=host)

    # Convert filter dates
    start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None
    participant_filter = participant.strip() if participant else None

    # ── Parse Only ──
    if do_parse:
        with st.spinner("Parsing..."):
            try:
                conversation = analyzer.parse(source)
            except ValueError as e:
                st.error(str(e))
                return

        st.success(f"Parsed **{len(conversation)}** messages from **{len(conversation.participants)}** participants")

        if conversation.participants:
            st.write("**Participants:**", ", ".join(conversation.participants))
        if conversation.start_date and conversation.end_date:
            st.write(
                f"**Date range:** {conversation.start_date:%Y-%m-%d} to {conversation.end_date:%Y-%m-%d}"
            )

        with st.expander("View parsed messages", expanded=False):
            st.text(conversation.to_text())

    # ── Full Analysis ──
    if do_analyze:
        with st.spinner("Analyzing with Ollama... This may take a minute on local hardware."):
            try:
                result = analyzer.analyze(
                    source,
                    participant=participant_filter,
                    start_date=start_dt,
                    end_date=end_dt,
                )
            except RuntimeError as e:
                st.error(
                    f"LLM Error: {e}\n\n"
                    "Make sure Ollama is running (`ollama serve`) and the model is pulled."
                )
                return
            except ValueError as e:
                st.error(str(e))
                return

        _display_results(result)


def _display_results(result: AnalysisResult) -> None:
    """Render the analysis result in Streamlit."""
    # Stats row
    c1, c2, c3 = st.columns(3)
    c1.metric("Messages", result.message_count)
    c2.metric("Participants", result.participant_count)
    c3.metric("Date Range", result.date_range or "N/A")

    # Summary
    if result.summary:
        st.subheader("Summary")
        st.write(result.summary)

    # Topics and Action Items side by side
    col_t, col_a = st.columns(2)

    with col_t:
        if result.topics:
            st.subheader("Key Topics")
            for topic in result.topics:
                st.write(f"- {topic}")

    with col_a:
        if result.action_items:
            st.subheader("Action Items")
            for item in result.action_items:
                st.write(f"- {item}")

    # Participant Analysis
    if result.participant_summaries:
        st.subheader("Participant Analysis")
        for name, summary in result.participant_summaries.items():
            with st.expander(name):
                st.write(summary)


if __name__ == "__main__":
    main()
