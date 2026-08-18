from mistralai.client import Mistral
from mistralai.client.errors import MistralError, NoResponseError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from .schemas import (
    ExtractedFields,
    LoadedSubmission,
    SubmissionExtraction,
)

MAX_RETRIES = 5
BACKOFF_MULTIPLIER_SECONDS = 1
BACKOFF_EXPONENTIAL_BASE = 2
BACKOFF_MAX_SECONDS = 30
RETRYABLE_STATUS_CODES: set[int] = {408, 409, 429, 500, 502, 503, 504}


def _is_retryable_exception(exception: BaseException) -> bool:
    """Return whether a failed request should be attempted again."""
    if isinstance(exception, (NoResponseError, TimeoutError)):
        return True
    return isinstance(exception, MistralError) and exception.status_code in RETRYABLE_STATUS_CODES


def format_submission(submission: LoadedSubmission) -> str:
    """
    Combine an email and its attachments while preserving
    document boundaries.
    """

    sections = [(f"=== EMAIL: {submission.submission_id}_email.md ===\n{submission.email_text}")]

    for attachment_number, attachment_text in enumerate(submission.attachments, start=1):
        sections.append(f"=== ATTACHMENT {attachment_number} ===\n{attachment_text}")

    return "\n\n".join(sections)


@retry(
    retry=retry_if_exception(_is_retryable_exception),
    wait=wait_exponential(
        multiplier=BACKOFF_MULTIPLIER_SECONDS,
        exp_base=BACKOFF_EXPONENTIAL_BASE,
        min=BACKOFF_MULTIPLIER_SECONDS,
        max=BACKOFF_MAX_SECONDS,
    ),
    stop=stop_after_attempt(MAX_RETRIES + 1),
    reraise=True,
)
def extract_with_mistral(
    client: Mistral,
    model: str,
    system_prompt: str,
    submission: LoadedSubmission,
) -> SubmissionExtraction:
    """Extract one submission using Mistral."""

    submission_text = format_submission(submission)

    response = client.chat.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": submission_text,
            },
        ],
        response_format=ExtractedFields,
        temperature=0,
        max_tokens=500,
    )

    if response.choices is None:
        raise ValueError("Mistral response did not contain choices")

    message = response.choices[0].message

    if message is None:
        raise ValueError("Mistral response did not contain a message")

    raw_content = message.content

    if not isinstance(raw_content, str):
        raise TypeError("Mistral did not return text content")

    extracted_fields = ExtractedFields.model_validate_json(raw_content)

    return SubmissionExtraction(
        submission_id=submission.submission_id,
        **extracted_fields.model_dump(),
    )
