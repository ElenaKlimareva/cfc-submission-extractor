from pathlib import Path

import pytest

from src.load_data import build_submission_index, read_submission, validate_submissions
from src.schemas import IndexedSubmission, LoadedSubmission


def write_file(directory: Path, name: str, text: str = "content") -> None:
    (directory / name).write_text(text, encoding="utf-8")


def test_build_submission_index_groups_and_orders_files(tmp_path: Path) -> None:
    write_file(tmp_path, "E002_email.md")
    write_file(tmp_path, "E001_attachment_10.md")
    write_file(tmp_path, "E001_email.md")
    write_file(tmp_path, "E001_attachment_2.md")

    assert build_submission_index(tmp_path) == [
        IndexedSubmission(
            submission_id="E001",
            email_path=tmp_path / "E001_email.md",
            attachments=[
                tmp_path / "E001_attachment_2.md",
                tmp_path / "E001_attachment_10.md",
            ],
        ),
        IndexedSubmission(
            submission_id="E002",
            email_path=tmp_path / "E002_email.md",
        ),
    ]


def test_build_submission_index_skips_unexpected_filenames(tmp_path: Path) -> None:
    write_file(tmp_path, "E001_email.md")
    write_file(tmp_path, "notes.md")

    submissions = build_submission_index(tmp_path)

    assert [submission.submission_id for submission in submissions] == ["E001"]


def test_validate_submissions_rejects_missing_email(tmp_path: Path) -> None:
    write_file(tmp_path, "E001_attachment_1.md")

    with pytest.raises(ValueError, match="E001"):
        validate_submissions(build_submission_index(tmp_path))


def test_read_submission_loads_email_and_attachments(tmp_path: Path) -> None:
    write_file(tmp_path, "E001_email.md", "email text")
    write_file(tmp_path, "E001_attachment_1.md", "attachment text")

    indexed_submission = build_submission_index(tmp_path)[0]

    assert read_submission(indexed_submission) == LoadedSubmission(
        submission_id="E001",
        email_text="email text",
        attachments=["attachment text"],
    )
