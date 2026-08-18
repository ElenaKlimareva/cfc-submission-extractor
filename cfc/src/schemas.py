from pathlib import Path

from pydantic import BaseModel, Field


class IndexedSubmission(BaseModel):
    """Submission file paths before document text has been loaded."""

    submission_id: str
    email_path: Path | None
    attachments: list[Path] = Field(default_factory=list)


class LoadedSubmission(BaseModel):
    """Submission content loaded from disk."""

    submission_id: str
    email_text: str
    attachments: list[str] = Field(default_factory=list)


class ExtractedFields(BaseModel):
    """Fields extracted by the LLM."""

    company_name: str | None = None

    revenue: int | None = Field(default=None, ge=0)

    countries: list[str] | None = None
    industry: str | None = None
    requested_coverages: list[str] | None = None


class SubmissionExtraction(BaseModel):
    """Final record including the submission identifier."""

    submission_id: str

    company_name: str | None = None

    revenue: int | None = Field(default=None, ge=0)

    countries: list[str] | None = None
    industry: str | None = None
    requested_coverages: list[str] | None = None
