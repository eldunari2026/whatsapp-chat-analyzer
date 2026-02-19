"""Tests for the core analyzer (with mocked LLM)."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from whatsapp_analyzer.analyzer.core import ChatAnalyzer
from whatsapp_analyzer.llm.base import BaseLLMClient
from whatsapp_analyzer.models.analysis import AnalysisResult


class FakeLLM(BaseLLMClient):
    """A fake LLM that returns predictable responses in the combined format."""

    def generate(self, prompt: str) -> str:
        # Handle the combined ANALYZE_ALL prompt
        if "SUMMARY:" in prompt and "TOPICS:" in prompt:
            return (
                "SUMMARY:\n"
                "This is a test summary of the conversation.\n\n"
                "TOPICS:\n"
                "- Project planning\n"
                "- Technical decisions\n\n"
                "ACTION ITEMS:\n"
                "- Bob: Set up the repo\n"
                "- Charlie: Draft wireframes\n\n"
                "PARTICIPANTS:\n"
                "- Alice: Led the project discussion and planning.\n"
                "- Bob: Focused on technical tasks and setup.\n"
            )
        if "summary" in prompt.lower() or "summarize" in prompt.lower():
            return "This is a test summary of the conversation."
        if "topic" in prompt.lower():
            return "- Project planning\n- Technical decisions"
        if "action" in prompt.lower():
            return "- Bob: Set up the repo\n- Charlie: Draft wireframes"
        if "participant" in prompt.lower():
            return "This participant was active in the discussion."
        return "Generic LLM response."

    def is_available(self) -> bool:
        return True


@pytest.fixture
def analyzer() -> ChatAnalyzer:
    fake_llm = FakeLLM()
    return ChatAnalyzer(llm_client=fake_llm)


@pytest.fixture
def sample_file(tmp_path) -> str:
    chat = tmp_path / "chat.txt"
    chat.write_text(
        "12/01/2024, 09:00 - Alice: Hello!\n"
        "12/01/2024, 09:01 - Bob: Hi there!\n"
        "12/01/2024, 09:02 - Alice: Let's plan the project.\n"
        "12/01/2024, 09:03 - Bob: Sounds good.\n"
    )
    return str(chat)


class TestChatAnalyzer:
    def test_parse_text_file(self, analyzer, sample_file):
        conv = analyzer.parse(sample_file)
        assert len(conv) == 4
        assert "Alice" in conv.participants

    def test_analyze_returns_result(self, analyzer, sample_file):
        result = analyzer.analyze(sample_file)
        assert isinstance(result, AnalysisResult)
        assert result.message_count == 4
        assert result.participant_count == 2

    def test_analyze_has_summary(self, analyzer, sample_file):
        result = analyzer.analyze(sample_file)
        assert "summary" in result.summary.lower()

    def test_analyze_has_topics(self, analyzer, sample_file):
        result = analyzer.analyze(sample_file)
        assert len(result.topics) > 0

    def test_analyze_has_action_items(self, analyzer, sample_file):
        result = analyzer.analyze(sample_file)
        assert len(result.action_items) > 0

    def test_analyze_has_participant_summaries(self, analyzer, sample_file):
        result = analyzer.analyze(sample_file)
        assert len(result.participant_summaries) > 0

    def test_analyze_with_participant_filter(self, analyzer, sample_file):
        result = analyzer.analyze(sample_file, participant="Alice")
        # Should still work, just with filtered messages
        assert isinstance(result, AnalysisResult)

    def test_analyze_with_date_filter(self, analyzer, sample_file):
        result = analyzer.analyze(
            sample_file,
            start_date=datetime(2024, 1, 12, 9, 1),
            end_date=datetime(2024, 1, 12, 9, 2),
        )
        assert isinstance(result, AnalysisResult)

    def test_format_report(self, analyzer, sample_file):
        result = analyzer.analyze(sample_file)
        report = result.format_report()
        assert "WHATSAPP CHAT ANALYSIS REPORT" in report
        assert "SUMMARY" in report

    def test_parse_invalid_source(self, analyzer):
        with pytest.raises(ValueError, match="No parser"):
            analyzer.parse("this is not a valid whatsapp chat at all xyz123")
