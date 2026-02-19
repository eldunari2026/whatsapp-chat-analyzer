"""WhatsApp text chat parser with multi-format regex support."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from whatsapp_analyzer.models.message import ChatMessage, Conversation
from whatsapp_analyzer.parsers.base import BaseParser

# Unicode characters WhatsApp injects into exports (LTR/RTL marks, etc.)
_UNICODE_JUNK = re.compile(r"[\u200e\u200f\u202a\u202b\u202c\u200b\u200d\ufeff]")

# Regex patterns for different WhatsApp timestamp formats
# Format 1: DD/MM/YYYY, HH:MM - Sender: message (24h, common in EU/Asia)
# Format 2: MM/DD/YY, H:MM AM/PM - Sender: message (12h, common in US)
# Format 3: [DD/MM/YYYY, HH:MM:SS] Sender: message (bracketed, iOS export)
# Format 4: DD/MM/YY, HH:MM - Sender: message (2-digit year)
_PATTERNS = [
    # [HH:MM, DD/MM/YYYY] Sender: message (time-first bracketed, common in India/Asia)
    re.compile(
        r"^\[(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?),\s+(\d{1,2}/\d{1,2}/\d{2,4})\]\s+"
    ),
    # [DD/MM/YYYY, HH:MM:SS] Sender: message (date-first bracketed, iOS export)
    re.compile(
        r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?)\]\s+"
    ),
    # DD/MM/YYYY, HH:MM - Sender: message  OR  MM/DD/YY, H:MM AM/PM -
    re.compile(
        r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}(?::\d{2})?\s*[APap][Mm]?)\s+[-–—]\s+"
    ),
    re.compile(
        r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}(?::\d{2})?)\s+[-–—]\s+"
    ),
]

# Date formats to try when parsing timestamps (date_str, time_str already split)
_DATE_FORMATS = [
    "%d/%m/%Y, %H:%M",
    "%d/%m/%Y, %H:%M:%S",
    "%m/%d/%Y, %I:%M %p",
    "%m/%d/%Y, %I:%M:%S %p",
    "%d/%m/%y, %H:%M",
    "%d/%m/%y, %H:%M:%S",
    "%m/%d/%y, %I:%M %p",
    "%m/%d/%y, %I:%M:%S %p",
    "%d/%m/%Y, %I:%M %p",
    "%d/%m/%Y, %I:%M:%S %p",
]

# For [time, date] format — we swap the groups so date comes first
_TIME_FIRST_PATTERN = _PATTERNS[0]

# System message indicators
_SYSTEM_INDICATORS = [
    "messages and calls are end-to-end encrypted",
    "created group",
    "added you",
    "added ",
    "removed ",
    "left",
    "changed the subject",
    "changed this group",
    "changed the group",
    "you were added",
    "security code changed",
    "joined using this group",
]

_MEDIA_INDICATOR = "<media omitted>"


def _parse_timestamp(date_str: str, time_str: str) -> datetime | None:
    """Try all known date formats to parse a timestamp."""
    combined = f"{date_str}, {time_str.strip()}"
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(combined, fmt)
        except ValueError:
            continue
    return None


def _is_system_message(content: str) -> bool:
    """Check if a message is a WhatsApp system message."""
    lower = content.lower()
    return any(indicator in lower for indicator in _SYSTEM_INDICATORS)


class WhatsAppTextParser(BaseParser):
    """Parser for WhatsApp exported text chat files and raw pasted text."""

    def can_handle(self, source: str) -> bool:
        """Check if source is a .txt file or looks like raw WhatsApp text."""
        path = Path(source)
        if path.suffix == ".txt" and path.exists():
            return True
        # Check if raw text has WhatsApp message patterns (clean unicode first)
        cleaned = _UNICODE_JUNK.sub("", source[:1000])
        for pattern in _PATTERNS:
            if pattern.search(cleaned):
                return True
        return False

    def parse(self, source: str) -> Conversation:
        """Parse WhatsApp text from a file path or raw string."""
        text = self._read_source(source)
        return self.parse_text(text)

    def parse_text(self, text: str) -> Conversation:
        """Parse raw WhatsApp chat text into a Conversation."""
        lines = text.split("\n")
        messages: list[ChatMessage] = []
        current_msg: ChatMessage | None = None

        for line in lines:
            parsed = self._try_parse_line(line)
            if parsed is not None:
                if current_msg is not None:
                    messages.append(current_msg)
                current_msg = parsed
            elif current_msg is not None:
                # Continuation of a multi-line message
                current_msg.content += "\n" + line
            # else: skip lines before the first message

        if current_msg is not None:
            messages.append(current_msg)

        return Conversation(messages=messages)

    def _read_source(self, source: str) -> str:
        """Read text from file path or return as-is if raw text."""
        path = Path(source)
        if path.exists() and path.is_file():
            raw = path.read_bytes()
            # Try UTF-8-SIG (strips BOM), then UTF-8, then UTF-16, then latin-1
            for encoding in ("utf-8-sig", "utf-8", "utf-16", "latin-1"):
                try:
                    return raw.decode(encoding)
                except (UnicodeDecodeError, UnicodeError):
                    continue
            return raw.decode("utf-8", errors="replace")
        return source

    @staticmethod
    def _clean_line(line: str) -> str:
        """Strip invisible Unicode characters WhatsApp injects into exports."""
        return _UNICODE_JUNK.sub("", line).strip()

    def _try_parse_line(self, line: str) -> ChatMessage | None:
        """Try to parse a single line as a WhatsApp message."""
        line = self._clean_line(line)
        if not line:
            return None

        for pattern in _PATTERNS:
            match = pattern.match(line)
            if match:
                return self._extract_message(match, line, pattern)

        return None

    def _extract_message(
        self, match: re.Match, line: str, pattern: re.Pattern
    ) -> ChatMessage | None:
        """Extract a ChatMessage from a regex match."""
        group1 = match.group(1)
        group2 = match.group(2)

        # For [time, date] format the groups are swapped
        if pattern is _TIME_FIRST_PATTERN:
            date_str = group2
            time_str = group1
        else:
            date_str = group1
            time_str = group2

        timestamp = _parse_timestamp(date_str, time_str)

        if timestamp is None:
            return None

        rest = line[match.end():]

        # Check for "Sender: content" pattern
        sender_match = re.match(r"^([^:]+?):\s(.*)", rest, re.DOTALL)

        if sender_match:
            sender = sender_match.group(1).strip()
            content = sender_match.group(2).strip()
            is_media = _MEDIA_INDICATOR in content.lower()
            is_system = _is_system_message(content)
            return ChatMessage(
                timestamp=timestamp,
                sender=sender,
                content=content,
                is_system=is_system,
                is_media=is_media,
            )
        else:
            # System message (no sender)
            content = rest.strip()
            return ChatMessage(
                timestamp=timestamp,
                sender="System",
                content=content,
                is_system=True,
                is_media=False,
            )
