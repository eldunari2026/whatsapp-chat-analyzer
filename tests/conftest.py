"""Shared fixtures for tests."""

from __future__ import annotations

from datetime import datetime

import pytest

from whatsapp_analyzer.models.message import ChatMessage, Conversation


SAMPLE_TEXT_24H = """\
12/01/2024, 09:00 - Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them. Tap to learn more.
12/01/2024, 09:01 - Alice: Hey everyone!
12/01/2024, 09:02 - Bob: Hi Alice!
12/01/2024, 09:03 - Alice: Here's the plan:
1. Design phase
2. Development
12/01/2024, 09:05 - Charlie: <Media omitted>
12/01/2024, 09:06 - Charlie: Shared the wireframes.
"""

SAMPLE_TEXT_12H = """\
1/12/2024, 9:00 AM - Alice: Good morning!
1/12/2024, 9:01 AM - Bob: Morning!
"""

SAMPLE_TEXT_BRACKETED = """\
[12/01/2024, 09:00:15] Alice: Hello from iOS!
[12/01/2024, 09:01:30] Bob: Hi there!
"""


@pytest.fixture
def sample_24h_text() -> str:
    return SAMPLE_TEXT_24H


@pytest.fixture
def sample_12h_text() -> str:
    return SAMPLE_TEXT_12H


@pytest.fixture
def sample_bracketed_text() -> str:
    return SAMPLE_TEXT_BRACKETED


@pytest.fixture
def sample_conversation() -> Conversation:
    return Conversation(
        messages=[
            ChatMessage(
                timestamp=datetime(2024, 1, 12, 9, 0),
                sender="System",
                content="Messages and calls are end-to-end encrypted.",
                is_system=True,
            ),
            ChatMessage(
                timestamp=datetime(2024, 1, 12, 9, 1),
                sender="Alice",
                content="Hey everyone!",
            ),
            ChatMessage(
                timestamp=datetime(2024, 1, 12, 9, 2),
                sender="Bob",
                content="Hi Alice!",
            ),
            ChatMessage(
                timestamp=datetime(2024, 1, 12, 9, 5),
                sender="Charlie",
                content="Sounds good.",
            ),
        ]
    )
