"""Shared JSONL output helpers for extraction predictions."""

import json
from pathlib import Path

from .schemas import SubmissionExtraction


def prepare_output_file(output_path: Path) -> None:
    """Create the parent directory and start an empty prediction JSONL file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("", encoding="utf-8")


def append_prediction(
    output_path: Path,
    prediction: SubmissionExtraction,
) -> None:
    """Append one validated prediction as one UTF-8 JSONL record."""
    with output_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(prediction.model_dump(), ensure_ascii=False) + "\n")
