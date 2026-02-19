"""Filters for narrowing down conversation scope."""

from __future__ import annotations

from datetime import datetime

from whatsapp_analyzer.models.message import Conversation


def apply_filters(
    conversation: Conversation,
    participant: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> Conversation:
    """Apply participant and date range filters to a conversation.

    Args:
        conversation: The conversation to filter.
        participant: If set, only include messages from this sender.
        start_date: If set, exclude messages before this date.
        end_date: If set, exclude messages after this date.

    Returns:
        A new filtered Conversation.
    """
    result = conversation

    if start_date or end_date:
        result = result.filter_by_date_range(start=start_date, end=end_date)

    if participant:
        result = result.filter_by_participant(participant)

    return result
