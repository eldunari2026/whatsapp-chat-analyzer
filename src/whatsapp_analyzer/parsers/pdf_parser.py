"""PDF parser for WhatsApp chat exports."""

from __future__ import annotations

from pathlib import Path

from whatsapp_analyzer.models.message import Conversation
from whatsapp_analyzer.parsers.base import BaseParser
from whatsapp_analyzer.parsers.text_parser import WhatsAppTextParser


class PDFParser(BaseParser):
    """Parse WhatsApp chat text extracted from PDF files."""

    def __init__(self) -> None:
        self._text_parser = WhatsAppTextParser()

    def can_handle(self, source: str) -> bool:
        path = Path(source)
        return path.suffix.lower() == ".pdf" and path.exists()

    def parse(self, source: str) -> Conversation:
        """Extract text from PDF and delegate to the text parser."""
        import pdfplumber

        text_parts: list[str] = []
        with pdfplumber.open(source) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        full_text = "\n".join(text_parts)
        return self._text_parser.parse_text(full_text)
