"""Compliance guard: RRN and financial PII masking."""

import re

RRN_PATTERN = re.compile(
    r"\b(\d{6})[-\s]?([1-4]\d{6})\b"
)
FINANCIAL_PATTERN = re.compile(
    r"\b(\d{3,4}[-\s]?\d{2,4}[-\s]?\d{4,7})\b"
)
ACCOUNT_PATTERN = re.compile(r"\b\d{10,14}\b")

CLOSING_KEYWORDS = ("감사합니다", "수고하세요", "고맙습니다")


def mask_message(raw: str) -> tuple[str, int]:
    """Return masked text and COMPLIANCE_YN (1=violation, 0=clean)."""
    compliance = 0
    masked = raw

    if RRN_PATTERN.search(masked):
        compliance = 1
        masked = RRN_PATTERN.sub("[RRN Omitted]", masked)

    if FINANCIAL_PATTERN.search(masked) or ACCOUNT_PATTERN.search(masked):
        compliance = 1
        masked = FINANCIAL_PATTERN.sub("[Masked Financial Info]", masked)
        masked = ACCOUNT_PATTERN.sub("[Masked Financial Info]", masked)

    return masked, compliance


def is_closing_message(message: str) -> bool:
    return any(kw in message for kw in CLOSING_KEYWORDS)
