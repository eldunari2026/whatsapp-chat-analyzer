"""Image parser for WhatsApp chat screenshots using LLaVA or OCR fallback."""

from __future__ import annotations

import base64
import logging
from pathlib import Path

from whatsapp_analyzer.models.message import Conversation
from whatsapp_analyzer.parsers.base import BaseParser
from whatsapp_analyzer.parsers.text_parser import WhatsAppTextParser

logger = logging.getLogger(__name__)

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}

_LLAVA_PROMPT = (
    "This is a screenshot of a WhatsApp group chat. "
    "Extract ALL the chat messages exactly as they appear. "
    "Format each message as: DD/MM/YYYY, HH:MM - Sender: message\n"
    "Include timestamps, sender names, and full message text. "
    "Do not add any commentary, just output the extracted messages."
)


class ImageParser(BaseParser):
    """Parse WhatsApp chat screenshots using LLaVA vision model or OCR fallback."""

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        vision_model: str = "llava",
    ) -> None:
        self._text_parser = WhatsAppTextParser()
        self._ollama_host = ollama_host
        self._vision_model = vision_model

    def can_handle(self, source: str) -> bool:
        path = Path(source)
        return path.suffix.lower() in _IMAGE_EXTENSIONS and path.exists()

    def parse(self, source: str) -> Conversation:
        """Extract chat text from image using LLaVA, falling back to OCR."""
        text = self._try_llava(source)
        if not text:
            text = self._try_ocr(source)
        if not text:
            logger.warning("Could not extract text from image: %s", source)
            return Conversation()
        return self._text_parser.parse_text(text)

    def _try_llava(self, image_path: str) -> str | None:
        """Try to extract chat text using LLaVA vision model via Ollama."""
        try:
            import ollama

            image_bytes = Path(image_path).read_bytes()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            client = ollama.Client(host=self._ollama_host)
            response = client.generate(
                model=self._vision_model,
                prompt=_LLAVA_PROMPT,
                images=[image_b64],
            )
            text = response.get("response", "").strip()
            if text:
                logger.info("Successfully extracted text using LLaVA")
                return text
        except Exception as e:
            logger.info("LLaVA extraction failed, falling back to OCR: %s", e)
        return None

    def _try_ocr(self, image_path: str) -> str | None:
        """Fall back to pytesseract OCR for text extraction."""
        try:
            from PIL import Image
            import pytesseract

            image = Image.open(image_path)
            text = pytesseract.image_to_string(image).strip()
            if text:
                logger.info("Successfully extracted text using OCR")
                return text
        except Exception as e:
            logger.warning("OCR extraction failed: %s", e)
        return None
