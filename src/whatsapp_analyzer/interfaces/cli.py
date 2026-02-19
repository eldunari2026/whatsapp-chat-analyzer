"""Click-based CLI for WhatsApp Chat Analyzer."""

from __future__ import annotations

import sys
from datetime import datetime

import click

from whatsapp_analyzer.analyzer.core import ChatAnalyzer


@click.group()
@click.version_option(package_name="whatsapp-analyzer")
def cli():
    """WhatsApp Group Chat Analyzer - local LLM powered analysis."""


@cli.command()
@click.argument("source")
@click.option("--model", default="llama3.1:8b", help="Ollama model name.")
@click.option("--host", default="http://localhost:11434", help="Ollama server URL.")
@click.option("--participant", default=None, help="Filter by participant name.")
@click.option(
    "--start-date",
    default=None,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Start date filter (YYYY-MM-DD).",
)
@click.option(
    "--end-date",
    default=None,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="End date filter (YYYY-MM-DD).",
)
def analyze(
    source: str,
    model: str,
    host: str,
    participant: str | None,
    start_date: datetime | None,
    end_date: datetime | None,
):
    """Run full LLM-powered analysis on a WhatsApp chat export.

    SOURCE can be a file path (.txt, .pdf, .docx, .png/.jpg) or raw pasted text.
    """
    analyzer = ChatAnalyzer(model=model, host=host)

    click.echo("Parsing input...")
    try:
        result = analyzer.analyze(
            source,
            participant=participant,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except RuntimeError as e:
        click.echo(f"LLM Error: {e}", err=True)
        click.echo(
            "Make sure Ollama is running (ollama serve) and the model is pulled.",
            err=True,
        )
        sys.exit(1)

    click.echo(result.format_report())


@cli.command("parse-only")
@click.argument("source")
def parse_only(source: str):
    """Parse a chat export without LLM analysis (no Ollama required).

    SOURCE can be a file path (.txt, .pdf, .docx, .png/.jpg).
    """
    analyzer = ChatAnalyzer()

    try:
        conversation = analyzer.parse(source)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Parsed {len(conversation)} messages")
    click.echo(f"Participants: {', '.join(conversation.participants)}")

    if conversation.start_date and conversation.end_date:
        click.echo(
            f"Date range: {conversation.start_date:%Y-%m-%d} to "
            f"{conversation.end_date:%Y-%m-%d}"
        )

    click.echo(f"\n{'─' * 40}")
    click.echo("MESSAGES")
    click.echo(f"{'─' * 40}")

    for msg in conversation.messages:
        click.echo(str(msg))


if __name__ == "__main__":
    cli()
