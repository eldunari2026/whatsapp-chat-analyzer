"""Data models for WhatsApp chat messages and conversations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChatMessage:
    """A single WhatsApp chat message."""

    timestamp: datetime
    sender: str
    content: str
    is_system: bool = False
    is_media: bool = False

    def __str__(self) -> str:
        if self.is_system:
            return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.content}"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.sender}: {self.content}"


@dataclass
class Conversation:
    """A collection of WhatsApp chat messages with filtering capabilities."""

    messages: list[ChatMessage] = field(default_factory=list)

    @property
    def participants(self) -> list[str]:
        """Return unique non-system senders sorted alphabetically."""
        return sorted({m.sender for m in self.messages if not m.is_system})

    @property
    def start_date(self) -> datetime | None:
        if not self.messages:
            return None
        return self.messages[0].timestamp

    @property
    def end_date(self) -> datetime | None:
        if not self.messages:
            return None
        return self.messages[-1].timestamp

    def filter_by_participant(self, participant: str) -> Conversation:
        """Return a new Conversation with only messages from the given participant."""
        filtered = [
            m for m in self.messages
            if m.sender.lower() == participant.lower() or m.is_system
        ]
        return Conversation(messages=filtered)

    def filter_by_date_range(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> Conversation:
        """Return a new Conversation filtered to the given date range."""
        filtered = []
        for m in self.messages:
            if start and m.timestamp < start:
                continue
            if end and m.timestamp > end:
                continue
            filtered.append(m)
        return Conversation(messages=filtered)

    def to_text(self) -> str:
        """Serialize all messages back to plain text."""
        return "\n".join(str(m) for m in self.messages)

    def __len__(self) -> int:
        return len(self.messages)
