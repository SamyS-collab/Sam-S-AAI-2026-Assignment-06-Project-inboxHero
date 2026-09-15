# security/phishing_detector

from __future__ import annotations

import re
from typing import Dict, List


URL_PATTERN = r"https?://[^\s]+"


PAYMENT_REDIRECTION_PATTERNS = [
    r"updated remittance details",
    r"banking partner has changed",
    r"disregard the account on file",
    r"new account below",
    r"wire confirmed",
    r"service interruption",
]

BEC_PATTERNS = [
    r"quick favor",
    r"keep this between us",
    r"don't loop in finance",
    r"dont loop in finance",
    r"can't get on a call",
    r"cannot get on a call",
    r"wire\s+\$?\d+",
]

CREDENTIAL_PATTERNS = [
    r"password expires",
    r"verify your credentials",
    r"re-verify your credentials",
    r"verify your account",
    r"login immediately",
    r"account.*suspend",
    r"lose access",
]


KEYWORDS = {
    "urgent",
    "wire",
    "routing",
    "remittance",
    "bank",
    "account",
    "password",
    "credential",
    "verify",
    "login",
    "suspended",
    "confidential",
    "finance",
}


class PhishingDetector:
    """
    Deterministic phishing detector.

    Responsibilities:
    - Detect phishing indicators.
    - Return evidence.
    - Do NOT assign dispositions.
    - Do NOT log.
    - Do NOT modify messages.
    """

    def analyze(self, subject: str, body: str) -> Dict:
        text = f"{subject}\n{body}".lower()

        reasons: List[str] = []

        payment_hits = self._match_patterns(
            text,
            PAYMENT_REDIRECTION_PATTERNS,
            "payment_redirection",
            reasons,
        )

        bec_hits = self._match_patterns(
            text,
            BEC_PATTERNS,
            "bec",
            reasons,
        )

        credential_hits = self._match_patterns(
            text,
            CREDENTIAL_PATTERNS,
            "credential",
            reasons,
        )

        keyword_hits = 0

        for keyword in KEYWORDS:
            if keyword in text:
                keyword_hits += 1
                reasons.append(f"keyword:{keyword}")

        urls = re.findall(URL_PATTERN, body)

        if urls:
            reasons.append("contains_url")

        score = (
            (payment_hits * 2)
            + (bec_hits * 2)
            + (credential_hits * 2)
            + keyword_hits
            + (2 if urls else 0)
        )

        is_phishing = False
        confidence = "low"

        # High-confidence BEC
        if bec_hits >= 2:
            is_phishing = True
            confidence = "high"

        # High-confidence credential harvesting
        elif credential_hits >= 2:
            is_phishing = True
            confidence = "high"

        # High-confidence payment redirection
        elif payment_hits >= 2:
            is_phishing = True
            confidence = "high"

        # Generic phishing scoring
        elif score >= 5:
            is_phishing = True
            confidence = "medium"

        return {
            "is_phishing": is_phishing,
            "confidence": confidence,
            "reasons": reasons,
            "score": score,
        }

    @staticmethod
    def _match_patterns(
        text: str,
        patterns: List[str],
        category: str,
        reasons: List[str],
    ) -> int:
        hits = 0

        for pattern in patterns:
            if re.search(pattern, text):
                hits += 1
                reasons.append(f"{category}:{pattern}")

        return hits