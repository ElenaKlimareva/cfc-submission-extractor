import re
from pathlib import Path

from .schemas import (
    IndexedSubmission,
    LoadedSubmission,
)

FILE_PATTERN: re.Pattern[str] = re.compile(r"^(E\d{3})_(email|attachment_\d+)\.md$")


def build_submission_index(data_directory: str | Path) -> list[IndexedSubmission]:
    """
    Group submission files without reading their contents into memory.
    """

    data_directory = Path(data_directory)
    submissions: dict[str, IndexedSubmission] = {}

    for file_path in sorted(data_directory.glob("*.md")):
        match = FILE_PATTERN.match(file_path.name)

        if match is None:
            print(f"Skipping unexpected file: {file_path.name}")
            continue

        submission_id, document_type = match.groups()

        if submission_id not in submissions:
            submissions[submission_id] = IndexedSubmission(
                submission_id=submission_id,
                email_path=None,
            )

        if document_type == "email":
            submissions[submission_id].email_path = file_path
        else:
            submissions[submission_id].attachments.append(file_path)

    records = sorted(submissions.values(), key=lambda record: record.submission_id)

    for record in records:
        record.attachments.sort(key=lambda path: int(path.stem.rsplit("_", maxsplit=1)[1]))

    return records


def read_submission(submission_index: IndexedSubmission) -> LoadedSubmission:
    """Read one indexed submission into the extraction record shape."""

    email_path = submission_index.email_path
    if email_path is None:
        raise ValueError(f"Submission without an email: {submission_index.submission_id}")

    return LoadedSubmission(
        submission_id=submission_index.submission_id,
        email_text=email_path.read_text(encoding="utf-8"),
        attachments=[attachment_path.read_text(encoding="utf-8") for attachment_path in submission_index.attachments],
    )


def validate_submissions(submissions: list[IndexedSubmission]) -> None:
    """Check that every submission contains an email body."""

    missing_emails: list[str] = [record.submission_id for record in submissions if record.email_path is None]

    if missing_emails:
        raise ValueError(f"Submissions without an email: {missing_emails}")
