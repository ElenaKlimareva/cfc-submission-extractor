"""Run the email-only heuristic extractor over all submissions."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.load_data import (
    build_submission_index,
    read_submission,
    validate_submissions,
)
from src.prediction_output import append_prediction, prepare_output_file
from src.rules_extractor import extract_submission_email_heuristic


def parse_arguments() -> argparse.Namespace:
    """Read rule-extraction options."""
    parser = argparse.ArgumentParser(description="Extract insurance submissions with email-only rules.")
    parser.add_argument(
        "--output",
        default="outputs/rule_predictions.jsonl",
        help="Prediction JSONL path relative to the project root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    submissions = build_submission_index(PROJECT_ROOT / "data" / "sample_emails")
    validate_submissions(submissions)

    output_path = PROJECT_ROOT / args.output

    prepare_output_file(output_path)
    for indexed_submission in submissions:
        prediction = extract_submission_email_heuristic(read_submission(indexed_submission))
        append_prediction(output_path, prediction)

    print(f"Predictions created: {len(submissions)}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
