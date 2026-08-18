import json
from pathlib import Path

from src.prediction_output import append_prediction, prepare_output_file
from src.schemas import SubmissionExtraction


def test_prediction_output_creates_fresh_utf8_jsonl_file(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "predictions.jsonl"
    prepare_output_file(output_path)
    append_prediction(output_path, SubmissionExtraction(submission_id="old"))

    prepare_output_file(output_path)
    predictions = [
        SubmissionExtraction(submission_id="E001", company_name="Café Ltd"),
        SubmissionExtraction(submission_id="E002", revenue=1_000_000),
    ]
    for prediction in predictions:
        append_prediction(output_path, prediction)

    output_text = output_path.read_text(encoding="utf-8")
    assert [json.loads(line) for line in output_text.splitlines()] == [
        prediction.model_dump() for prediction in predictions
    ]
    assert "Café Ltd" in output_text
