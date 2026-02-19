"""Tests for conversation chunker."""

from __future__ import annotations

from datetime import datetime

from whatsapp_analyzer.analyzer.chunker import ConversationChunker
from whatsapp_analyzer.models.message import ChatMessage, Conversation


class TestConversationChunker:
    def setup_method(self):
        self.chunker = ConversationChunker(max_chars=200)

    def _make_messages(self, count: int) -> list[ChatMessage]:
        return [
            ChatMessage(
                timestamp=datetime(2024, 1, 12, 9, i),
                sender="User",
                content=f"Message number {i} with some extra text to fill space.",
            )
            for i in range(count)
        ]

    def test_single_chunk_small_conversation(self):
        conv = Conversation(messages=self._make_messages(2))
        chunks = self.chunker.chunk(conv)
        assert len(chunks) == 1
        assert len(chunks[0]) == 2

    def test_multiple_chunks_large_conversation(self):
        conv = Conversation(messages=self._make_messages(20))
        chunks = self.chunker.chunk(conv)
        assert len(chunks) > 1
        # All messages accounted for
        total = sum(len(c) for c in chunks)
        assert total == 20

    def test_no_messages(self):
        conv = Conversation(messages=[])
        chunks = self.chunker.chunk(conv)
        assert chunks == []

    def test_each_chunk_under_limit(self):
        conv = Conversation(messages=self._make_messages(20))
        chunks = self.chunker.chunk(conv)
        for chunk in chunks:
            text = chunk.to_text()
            # Allow some tolerance for the last message added
            assert len(text) < self.chunker.max_chars * 2

    def test_needs_chunking(self):
        small = Conversation(messages=self._make_messages(1))
        large = Conversation(messages=self._make_messages(20))
        assert self.chunker.needs_chunking(small) is False
        assert self.chunker.needs_chunking(large) is True
