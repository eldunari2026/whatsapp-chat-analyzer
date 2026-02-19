"""FastAPI backend for WhatsApp Chat Analyzer."""

from __future__ import annotations

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Add src/ to path so we can import the existing analyzer code
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from whatsapp_analyzer.analyzer.core import ChatAnalyzer
from whatsapp_analyzer.models.analysis import AnalysisResult

app = FastAPI(title="WhatsApp Chat Analyzer API", version="0.1.0")

# CORS — allow the Netlify frontend to call this API
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def _get_analyzer() -> ChatAnalyzer:
    return ChatAnalyzer(model=OLLAMA_MODEL, host=OLLAMA_HOST)


def _result_to_dict(result: AnalysisResult) -> dict:
    return {
        "summary": result.summary,
        "topics": result.topics,
        "action_items": result.action_items,
        "participant_summaries": result.participant_summaries,
        "message_count": result.message_count,
        "participant_count": result.participant_count,
        "date_range": result.date_range,
    }


# ── Health check ──────────────────────────────────────────────


@app.get("/api/health")
def health():
    """Check if the API and Ollama are running."""
    analyzer = _get_analyzer()
    try:
        ollama_ok = analyzer._llm.is_available()
    except Exception:
        ollama_ok = False

    return {
        "status": "ok",
        "ollama_available": ollama_ok,
        "model": OLLAMA_MODEL,
    }


# ── Parse only (no LLM) ──────────────────────────────────────


@app.post("/api/parse/text")
def parse_text(text: str = Form(...)):
    """Parse raw WhatsApp chat text without LLM analysis."""
    analyzer = _get_analyzer()
    try:
        conversation = analyzer.parse(text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message_count": len(conversation),
        "participants": conversation.participants,
        "start_date": conversation.start_date.isoformat() if conversation.start_date else None,
        "end_date": conversation.end_date.isoformat() if conversation.end_date else None,
        "messages": [
            {
                "timestamp": m.timestamp.isoformat(),
                "sender": m.sender,
                "content": m.content,
                "is_system": m.is_system,
                "is_media": m.is_media,
            }
            for m in conversation.messages
        ],
    }


@app.post("/api/parse/file")
def parse_file(file: UploadFile = File(...)):
    """Parse an uploaded chat export file without LLM analysis."""
    suffix = Path(file.filename or "upload.txt").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    analyzer = _get_analyzer()
    try:
        conversation = analyzer.parse(tmp_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return {
        "message_count": len(conversation),
        "participants": conversation.participants,
        "start_date": conversation.start_date.isoformat() if conversation.start_date else None,
        "end_date": conversation.end_date.isoformat() if conversation.end_date else None,
        "messages": [
            {
                "timestamp": m.timestamp.isoformat(),
                "sender": m.sender,
                "content": m.content,
                "is_system": m.is_system,
                "is_media": m.is_media,
            }
            for m in conversation.messages
        ],
    }


# ── Full LLM analysis ────────────────────────────────────────


@app.post("/api/analyze/text")
def analyze_text(
    text: str = Form(...),
    participant: str = Form(None),
    start_date: str = Form(None),
    end_date: str = Form(None),
):
    """Full LLM-powered analysis of pasted WhatsApp chat text."""
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    analyzer = _get_analyzer()
    try:
        result = analyzer.analyze(
            text, participant=participant, start_date=start_dt, end_date=end_dt
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return _result_to_dict(result)


@app.post("/api/analyze/file")
def analyze_file(
    file: UploadFile = File(...),
    participant: str = Form(None),
    start_date: str = Form(None),
    end_date: str = Form(None),
):
    """Full LLM-powered analysis of an uploaded chat export file."""
    suffix = Path(file.filename or "upload.txt").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    analyzer = _get_analyzer()
    try:
        result = analyzer.analyze(
            tmp_path, participant=participant, start_date=start_dt, end_date=end_dt
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return _result_to_dict(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
