"""Core analyzer orchestrator - single entry point for both CLI and Web."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from whatsapp_analyzer.analyzer.chunker import ConversationChunker
from whatsapp_analyzer.analyzer.filters import apply_filters
from whatsapp_analyzer.llm.base import BaseLLMClient
from whatsapp_analyzer.llm.ollama_client import OllamaClient
from whatsapp_analyzer.llm import prompts
from whatsapp_analyzer.models.analysis import AnalysisResult
from whatsapp_analyzer.models.message import Conversation
from whatsapp_analyzer.parsers.text_parser import WhatsAppTextParser
from whatsapp_analyzer.parsers.pdf_parser import PDFParser
from whatsapp_analyzer.parsers.docx_parser import DocxParser
from whatsapp_analyzer.parsers.image_parser import ImageParser

logger = logging.getLogger(__name__)

MAX_PARTICIPANTS_FOR_ANALYSIS = 10


class ChatAnalyzer:
    """Main orchestrator for WhatsApp chat analysis.

    Auto-detects input format, parses, chunks, analyzes via LLM, and merges results.
    """

    def __init__(
        self,
        model: str = "llama3.1:8b",
        host: str = "http://localhost:11434",
        llm_client: BaseLLMClient | None = None,
    ) -> None:
        self._llm = llm_client or OllamaClient(model=model, host=host)
        self._chunker = ConversationChunker()
        self._parsers = [
            PDFParser(),
            DocxParser(),
            ImageParser(ollama_host=host),
            WhatsAppTextParser(),  # text parser last (broadest match)
        ]

    def parse(self, source: str) -> Conversation:
        """Auto-detect format and parse the source into a Conversation."""
        for parser in self._parsers:
            if parser.can_handle(source):
                logger.info("Using parser: %s", type(parser).__name__)
                return parser.parse(source)

        raise ValueError(
            f"No parser could handle the input. "
            f"Supported formats: .txt, .pdf, .docx, .png/.jpg (screenshot)"
        )

    def analyze(
        self,
        source: str,
        participant: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> AnalysisResult:
        """Full analysis pipeline: parse → filter → chunk → analyze → merge."""
        conversation = self.parse(source)

        if not conversation.messages:
            return AnalysisResult(summary="No messages found in the input.")

        # Apply filters
        filtered = apply_filters(
            conversation,
            participant=participant,
            start_date=start_date,
            end_date=end_date,
        )

        if not filtered.messages:
            return AnalysisResult(summary="No messages match the given filters.")

        # Build metadata
        result = AnalysisResult(
            message_count=len(filtered),
            participant_count=len(filtered.participants),
        )
        if filtered.start_date and filtered.end_date:
            result.date_range = (
                f"{filtered.start_date:%Y-%m-%d} to {filtered.end_date:%Y-%m-%d}"
            )

        # Chunk if needed and analyze
        chunks = self._chunker.chunk(filtered)
        logger.info("Split conversation into %d chunk(s)", len(chunks))

        if len(chunks) == 1:
            self._analyze_combined(chunks[0], result)
        else:
            self._analyze_multi_combined(chunks, result)

        return result

    def _analyze_combined(
        self, chunk: Conversation, result: AnalysisResult
    ) -> None:
        """Analyze a single chunk with ONE LLM call (summary+topics+actions+participants)."""
        chat_text = chunk.to_text()
        participants = chunk.participants[:MAX_PARTICIPANTS_FOR_ANALYSIS]

        participant_list = "\n".join(
            prompts.PARTICIPANT_LINE.format(name=p) for p in participants
        )

        raw = self._llm.generate(
            prompts.ANALYZE_ALL.format(
                chat_text=chat_text,
                participant_list=participant_list,
            )
        )
        self._parse_combined_response(raw, result)

    def _analyze_multi_combined(
        self, chunks: list[Conversation], result: AnalysisResult
    ) -> None:
        """Analyze multiple chunks — one LLM call per chunk, then one merge call."""
        partial_summaries = []
        partial_topics = []
        partial_actions = []

        for i, chunk in enumerate(chunks):
            logger.info("Analyzing chunk %d/%d", i + 1, len(chunks))
            chat_text = chunk.to_text()

            partial_summaries.append(
                self._llm.generate(prompts.SUMMARIZE.format(chat_text=chat_text))
            )
            partial_topics.append(
                self._llm.generate(prompts.EXTRACT_TOPICS.format(chat_text=chat_text))
            )
            partial_actions.append(
                self._llm.generate(
                    prompts.EXTRACT_ACTION_ITEMS.format(chat_text=chat_text)
                )
            )

        # Merge summaries
        result.summary = self._llm.generate(
            prompts.MERGE_SUMMARIES.format(
                summaries="\n\n---\n\n".join(partial_summaries)
            )
        )

        # Merge topics
        merged_topics = self._llm.generate(
            prompts.MERGE_TOPICS.format(topics="\n".join(partial_topics))
        )
        result.topics = self._parse_list(merged_topics)

        # Merge action items
        merged_actions = self._llm.generate(
            prompts.MERGE_ACTION_ITEMS.format(
                action_items="\n".join(partial_actions)
            )
        )
        result.action_items = self._parse_list(merged_actions)

    def _parse_combined_response(
        self, raw: str, result: AnalysisResult
    ) -> None:
        """Parse the combined ANALYZE_ALL response into structured fields."""
        sections = {"summary": "", "topics": "", "action items": "", "participants": ""}
        current_section = None

        for line in raw.split("\n"):
            line_lower = line.strip().lower().rstrip(":")
            if line_lower in sections:
                current_section = line_lower
                continue
            if current_section is not None:
                sections[current_section] += line + "\n"

        result.summary = sections["summary"].strip()
        result.topics = self._parse_list(sections["topics"])
        result.action_items = self._parse_list(sections["action items"])

        # Parse participant summaries from "- Name: summary" lines
        for line in sections["participants"].strip().split("\n"):
            line = line.strip()
            if line.startswith("- "):
                line = line[2:]
            if ": " in line:
                name, summary = line.split(": ", 1)
                result.participant_summaries[name.strip()] = summary.strip()

    @staticmethod
    def _parse_list(raw: str) -> list[str]:
        """Parse a bulleted list from LLM output into a clean list of strings."""
        items = []
        for line in raw.strip().split("\n"):
            line = line.strip()
            if line.startswith("- "):
                line = line[2:]
            elif line.startswith("* "):
                line = line[2:]
            elif len(line) > 2 and line[0].isdigit() and line[1] in ".)":
                line = line[2:]
            elif len(line) > 3 and line[:2].isdigit() and line[2] in ".)":
                line = line[3:]
            else:
                continue
            line = line.strip()
            if line:
                items.append(line)
        return items
