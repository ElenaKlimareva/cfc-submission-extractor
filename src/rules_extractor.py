"""Email-only heuristic baseline for structured submission extraction.

The baseline intentionally reads only the broker email. It provides a cheap,
deterministic benchmark for the attachment-aware LLM extractor; it is not
intended to be a complete rule-based submission intake system.
"""

import re

import pycountry

from .schemas import LoadedSubmission, SubmissionExtraction

COVERAGE_ALIASES: dict[str, tuple[str, ...]] = {
    "Cyber": ("Cyber",),
    "Professional Indemnity": ("Professional Indemnity", "PI"),
    "Property": ("Property",),
    "General Liability": ("General Liability", "GL"),
    "Management Liability": ("Management Liability",),
    "Media Liability": ("Media Liability",),
    "Technology E&O": ("Technology E&O", "Tech E&O"),
    "Kidnap & Ransom": ("Kidnap & Ransom", "K&R"),
    "Product Liability": ("Product Liability",),
    "Directors & Officers": ("Directors & Officers", "D&O"),
}

COUNTRY_ALIASES: dict[str, str] = {
    "UK": "United Kingdom",
    "U.K.": "United Kingdom",
    "USA": "United States",
    "U.S.A.": "United States",
    "US": "United States",
    "U.S.": "United States",
    "UAE": "United Arab Emirates",
    "U.A.E.": "United Arab Emirates",
}


def build_country_lookup() -> dict[str, str]:
    """Map ISO country names and common aliases to canonical names."""

    lookup: dict[str, str] = {}

    for country in pycountry.countries:
        canonical_name = country.name

        for attribute in ("name", "official_name", "common_name"):
            value = getattr(country, attribute, None)
            if value:
                lookup[value.casefold()] = canonical_name

    lookup.update({alias.casefold(): canonical_name for alias, canonical_name in COUNTRY_ALIASES.items()})

    return lookup


COUNTRY_LOOKUP = build_country_lookup()


def extract_company_name(email_text: str) -> str | None:
    """Extract a company name from the email subject."""

    match = re.search(
        r"^Subject:\s*(.+)$",
        email_text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    if match is None:
        return None

    subject = match.group(1).strip()

    # Remove generic subject prefixes
    subject = re.sub(
        r"^Group submission\s*-\s*",
        "",
        subject,
        flags=re.IGNORECASE,
    )

    # Remove generic submission descriptions
    subject = re.split(
        (
            r"\s+-\s+"
            r"(?:New Business Submission|Renewal Submission|"
            r"Coverage enquiry|Group submission|New business)"
        ),
        subject,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    subject = re.sub(
        r"\s+renewal$",
        "",
        subject,
        flags=re.IGNORECASE,
    )

    return subject.strip() or None


def extract_revenue(email_text: str) -> int | None:
    """
    Extract the first GBP value from the email.

    This is intentionally a simple baseline rule.
    """

    match = re.search(
        r"£\s*([\d,]+)",
        email_text,
    )

    if match is None:
        return None

    return int(match.group(1).replace(",", ""))


def split_items(text: str) -> list[str]:
    """Split a comma-separated or 'and'-separated list."""

    items = re.split(
        r",|\band\b",
        text,
        flags=re.IGNORECASE,
    )

    return [item.strip() for item in items if item.strip()]


def canonicalize_countries(items: list[str]) -> list[str] | None:
    """Keep recognized countries and return their canonical ISO names."""

    countries: list[str] = []

    for item in items:
        canonical_name = COUNTRY_LOOKUP.get(item.casefold())

        if canonical_name and canonical_name not in countries:
            countries.append(canonical_name)

    return countries or None


def extract_countries(
    email_text: str,
) -> list[str] | None:
    """Extract countries or territories from the email."""

    patterns: list[str] = [
        r"operates in (.+?) and is active in",
        (
            r"(?:confirmed active territories|territories):"
            r"\s*(.+?)(?:\.|\n)"
        ),
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            email_text,
            flags=re.IGNORECASE,
        )

        if match is not None:
            return canonicalize_countries(split_items(match.group(1)))

    return None


def extract_industry(email_text: str) -> str | None:
    """Extract the industry description."""

    patterns: list[str] = [
        r"active in the (.+?) sector",
        r"Industry:\s*(.+?)(?:\.|\n)",
        r"describes itself as a (.+?) business",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            email_text,
            flags=re.IGNORECASE,
        )

        if match is not None:
            industry = match.group(1).strip()
            return industry.title()

    return None


def extract_requested_coverages(
    email_text: str,
) -> list[str] | None:
    """Extract explicitly requested coverages."""

    patterns: list[str] = [
        r"Coverages requested:\s*(.+?)(?:\.|\n)",
        r"Coverages:\s*(.+?)(?:\.|\n)",
        r"Client is seeking\s*(.+?)\s*only(?:\.|\n)",
        r"Requested going forward:\s*(.+?)(?:\.|\n)",
        r"Primary request:\s*(.+?)(?:\.|\n)",
    ]

    coverage_text: str | None = None

    for pattern in patterns:
        match = re.search(
            pattern,
            email_text,
            flags=re.IGNORECASE,
        )

        if match is not None:
            coverage_text = match.group(1)
            break

    if coverage_text is None:
        return None

    coverage_matches: list[tuple[int, str]] = []

    for canonical_name, aliases in COVERAGE_ALIASES.items():
        positions = []

        for alias in aliases:
            match = re.search(
                rf"(?<!\w){re.escape(alias)}(?!\w)",
                coverage_text,
                flags=re.IGNORECASE,
            )

            if match is not None:
                positions.append(match.start())

        if positions:
            coverage_matches.append((min(positions), canonical_name))

    coverage_matches.sort()

    extracted = [coverage for _, coverage in coverage_matches]

    return extracted or None


def extract_submission_email_heuristic(submission: LoadedSubmission) -> SubmissionExtraction:
    """Apply the email-only heuristic baseline to one submission."""

    email_text = submission.email_text

    return SubmissionExtraction(
        submission_id=submission.submission_id,
        company_name=extract_company_name(email_text),
        revenue=extract_revenue(email_text),
        countries=extract_countries(email_text),
        industry=extract_industry(email_text),
        requested_coverages=(extract_requested_coverages(email_text)),
    )
