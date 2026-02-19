"""Tests for WhatsApp text parser."""

from __future__ import annotations

from datetime import datetime

from whatsapp_analyzer.parsers.text_parser import WhatsAppTextParser


class TestWhatsAppTextParser:
    def setup_method(self):
        self.parser = WhatsAppTextParser()

    def test_parse_24h_format(self, sample_24h_text):
        conv = self.parser.parse_text(sample_24h_text)
        # System message + 5 user messages
        assert len(conv) == 6

    def test_system_message_detected(self, sample_24h_text):
        conv = self.parser.parse_text(sample_24h_text)
        assert conv.messages[0].is_system is True
        assert "encrypted" in conv.messages[0].content

    def test_sender_parsed(self, sample_24h_text):
        conv = self.parser.parse_text(sample_24h_text)
        assert conv.messages[1].sender == "Alice"
        assert conv.messages[2].sender == "Bob"

    def test_multiline_message(self, sample_24h_text):
        conv = self.parser.parse_text(sample_24h_text)
        alice_plan = conv.messages[3]
        assert alice_plan.sender == "Alice"
        assert "1. Design phase" in alice_plan.content
        assert "2. Development" in alice_plan.content

    def test_media_omitted(self, sample_24h_text):
        conv = self.parser.parse_text(sample_24h_text)
        media_msg = conv.messages[4]
        assert media_msg.is_media is True
        assert media_msg.sender == "Charlie"

    def test_participants(self, sample_24h_text):
        conv = self.parser.parse_text(sample_24h_text)
        participants = conv.participants
        assert "Alice" in participants
        assert "Bob" in participants
        assert "Charlie" in participants

    def test_parse_12h_format(self, sample_12h_text):
        conv = self.parser.parse_text(sample_12h_text)
        assert len(conv) == 2
        assert conv.messages[0].sender == "Alice"
        assert conv.messages[0].content == "Good morning!"

    def test_parse_bracketed_format(self, sample_bracketed_text):
        conv = self.parser.parse_text(sample_bracketed_text)
        assert len(conv) == 2
        assert conv.messages[0].sender == "Alice"
        assert conv.messages[1].sender == "Bob"

    def test_timestamps_parsed(self, sample_24h_text):
        conv = self.parser.parse_text(sample_24h_text)
        assert conv.messages[1].timestamp == datetime(2024, 1, 12, 9, 1)

    def test_can_handle_text_file(self, tmp_path):
        txt_file = tmp_path / "chat.txt"
        txt_file.write_text("12/01/2024, 09:00 - Alice: Hello")
        assert self.parser.can_handle(str(txt_file)) is True

    def test_can_handle_raw_text(self):
        raw = "12/01/2024, 09:00 - Alice: Hello"
        assert self.parser.can_handle(raw) is True

    def test_cannot_handle_random_text(self):
        assert self.parser.can_handle("just some random text") is False

    def test_empty_input(self):
        conv = self.parser.parse_text("")
        assert len(conv) == 0

    def test_filter_by_participant(self, sample_24h_text):
        conv = self.parser.parse_text(sample_24h_text)
        filtered = conv.filter_by_participant("Alice")
        non_system = [m for m in filtered.messages if not m.is_system]
        assert all(m.sender == "Alice" for m in non_system)

    def test_filter_by_date_range(self, sample_24h_text):
        conv = self.parser.parse_text(sample_24h_text)
        start = datetime(2024, 1, 12, 9, 3)
        end = datetime(2024, 1, 12, 9, 5)
        filtered = conv.filter_by_date_range(start=start, end=end)
        for msg in filtered.messages:
            assert start <= msg.timestamp <= end
