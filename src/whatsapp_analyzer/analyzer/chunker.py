"""Conversation chunker for splitting large chats to fit model context windows."""

from __future__ import annotations

from whatsapp_analyzer.models.message import ChatMessage, Conversation

# ~12K chars ≈ 3-4K tokens, leaving room for prompts within 8K context
DEFAULT_MAX_CHARS = 12000


class ConversationChunker:
    """Split a Conversation into chunks that fit within an LLM context window."""

    def __init__(self, max_chars: int = DEFAULT_MAX_CHARS) -> None:
        self.max_chars = max_chars

    def chunk(self, conversation: Conversation) -> list[Conversation]:
        """Split a conversation into smaller chunks.

        Each chunk stays under max_chars when serialized to text.
        Splits at message boundaries to avoid cutting messages.
        """
        if not conversation.messages:
            return []

        chunks: list[Conversation] = []
        current_messages: list[ChatMessage] = []
        current_chars = 0

        for message in conversation.messages:
            msg_text = str(message)
            msg_len = len(msg_text)

            if current_chars + msg_len > self.max_chars and current_messages:
                chunks.append(Conversation(messages=list(current_messages)))
                current_messages = []
                current_chars = 0

            current_messages.append(message)
            current_chars += msg_len + 1  # +1 for newline

        if current_messages:
            chunks.append(Conversation(messages=list(current_messages)))

        return chunks

    def needs_chunking(self, conversation: Conversation) -> bool:
        """Check if a conversation exceeds the chunk size limit."""
        return len(conversation.to_text()) > self.max_chars
