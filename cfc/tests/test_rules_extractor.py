from src.rules_extractor import extract_submission_email_heuristic
from src.schemas import LoadedSubmission, SubmissionExtraction


def test_email_heuristic_extracts_core_fields_and_ignores_attachments() -> None:
    submission = LoadedSubmission(
        submission_id="E001",
        email_text=(
            "Subject: Acme Ltd - New Business Submission\n"
            "Revenue: £1,250,000. Policy limit: £5,000,000.\n"
            "Confirmed active territories: UK, Germany, UAE.\n"
            "Industry: software development\n"
            "Coverages requested: D&O, PI, Tech E&O and K&R.\n"
        ),
        attachments=["Industry: Manufacturing\n"],
    )

    assert extract_submission_email_heuristic(submission) == SubmissionExtraction(
        submission_id="E001",
        company_name="Acme Ltd",
        revenue=1_250_000,
        countries=["United Kingdom", "Germany", "United Arab Emirates"],
        industry="Software Development",
        requested_coverages=[
            "Directors & Officers",
            "Professional Indemnity",
            "Technology E&O",
            "Kidnap & Ransom",
        ],
    )


def test_email_heuristic_does_not_invent_unsupported_values() -> None:
    result = extract_submission_email_heuristic(
        LoadedSubmission(
            submission_id="E002",
            email_text="Revenue: EUR 1,250,000\nTerritories: Europe, North America.\n",
        )
    )

    assert result.company_name is None
    assert result.revenue is None
    assert result.countries is None
    assert result.industry is None
    assert result.requested_coverages is None
