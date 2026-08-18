from src.mistral_extractor import format_submission
from src.schemas import LoadedSubmission


def test_format_submission_preserves_document_boundaries_and_order() -> None:
    submission = LoadedSubmission(
        submission_id="E001",
        email_text="Email body",
        attachments=["First attachment", "Second attachment"],
    )

    assert format_submission(submission) == (
        "=== EMAIL: E001_email.md ===\nEmail body\n\n"
        "=== ATTACHMENT 1 ===\nFirst attachment\n\n"
        "=== ATTACHMENT 2 ===\nSecond attachment"
    )
