"""DOCX parser for WhatsApp chat exports."""

from __future__ import annotations

from pathlib import Path

from whatsapp_analyzer.models.message import Conversation
from whatsapp_analyzer.parsers.base import BaseParser
from whatsapp_analyzer.parsers.text_parser import WhatsAppTextParser


class DocxParser(BaseParser):
    """Parse WhatsApp chat text extracted from DOCX files."""

    def __init__(self) -> None:
        self._text_parser = WhatsAppTextParser()

    def can_handle(self, source: str) -> bool:
        path = Path(source)
        return path.suffix.lower() == ".docx" and path.exists()

    def parse(self, source: str) -> Conversation:
        """Extract text from DOCX and delegate to the text parser."""
        from docx import Document

        doc = Document(source)
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        full_text = "\n".join(text_parts)
        return self._text_parser.parse_text(full_text)
