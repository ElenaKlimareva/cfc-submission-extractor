"""Run Mistral extraction over all indexed submissions."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mistralai.client import Mistral

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.load_data import (
    build_submission_index,
    read_submission,
    validate_submissions,
)
from src.mistral_extractor import extract_with_mistral
from src.prediction_output import append_prediction, prepare_output_file

DEFAULT_OUTPUT = "outputs/mistral_predictions.jsonl"
DEFAULT_MODEL = "ministral-8b-latest"
DEFAULT_SYSTEM_PROMPT = "prompts/extraction_system_prompt.txt"


def parse_arguments() -> argparse.Namespace:
    """Read LLM extraction options."""
    parser = argparse.ArgumentParser(description="Extract all insurance submissions using Mistral.")
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Prediction JSONL path relative to the project root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    output_path = PROJECT_ROOT / args.output
    prompt_path = PROJECT_ROOT / DEFAULT_SYSTEM_PROMPT

    submissions = build_submission_index(PROJECT_ROOT / "data" / "sample_emails")
    validate_submissions(submissions)

    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY was not found")

    system_prompt = prompt_path.read_text(encoding="utf-8")
    client = Mistral(api_key=api_key)

    prepare_output_file(output_path)
    for submission in submissions:
        prediction = extract_with_mistral(
            client=client,
            model=DEFAULT_MODEL,
            system_prompt=system_prompt,
            submission=read_submission(submission),
        )
        append_prediction(output_path, prediction)

    print("\nExtraction complete")
    print("Predictions created:", len(submissions))
    print("Saved to:", output_path)


if __name__ == "__main__":
    main()
