"""Data model for analysis results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AnalysisResult:
    """Structured output from the chat analyzer."""

    summary: str = ""
    topics: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    participant_summaries: dict[str, str] = field(default_factory=dict)
    message_count: int = 0
    participant_count: int = 0
    date_range: str = ""

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "topics": self.topics,
            "action_items": self.action_items,
            "participant_summaries": self.participant_summaries,
            "message_count": self.message_count,
            "participant_count": self.participant_count,
            "date_range": self.date_range,
        }

    def format_report(self) -> str:
        """Format the analysis result as a human-readable report."""
        sections = []

        sections.append("=" * 60)
        sections.append("WHATSAPP CHAT ANALYSIS REPORT")
        sections.append("=" * 60)

        if self.date_range:
            sections.append(f"\nDate Range: {self.date_range}")
        sections.append(f"Messages: {self.message_count}")
        sections.append(f"Participants: {self.participant_count}")

        if self.summary:
            sections.append(f"\n{'─' * 40}")
            sections.append("SUMMARY")
            sections.append(f"{'─' * 40}")
            sections.append(self.summary)

        if self.topics:
            sections.append(f"\n{'─' * 40}")
            sections.append("KEY TOPICS")
            sections.append(f"{'─' * 40}")
            for i, topic in enumerate(self.topics, 1):
                sections.append(f"  {i}. {topic}")

        if self.action_items:
            sections.append(f"\n{'─' * 40}")
            sections.append("ACTION ITEMS")
            sections.append(f"{'─' * 40}")
            for i, item in enumerate(self.action_items, 1):
                sections.append(f"  {i}. {item}")

        if self.participant_summaries:
            sections.append(f"\n{'─' * 40}")
            sections.append("PARTICIPANT ANALYSIS")
            sections.append(f"{'─' * 40}")
            for name, summary in self.participant_summaries.items():
                sections.append(f"\n  [{name}]")
                sections.append(f"  {summary}")

        sections.append("\n" + "=" * 60)
        return "\n".join(sections)
