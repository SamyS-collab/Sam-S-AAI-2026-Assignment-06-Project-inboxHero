# Policy Validator

"""
Responsibilities:
- Validate generated content
- Detect secrets and credentials
- Detect unsafe output
- Produce validation decisions

Non-responsibilities:
- Modifying content
- Generating content
- Writing files
- Calling LLMs
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    Result returned by PolicyValidator.
    """

    allowed: bool
    reason: str

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
        }


class PolicyValidator:
    """
    Deterministic output validator.

    Detects:
    - Credentials
    - API keys
    - Tokens
    - Connection strings
    """

    CREDENTIAL_URL_PATTERN = re.compile(
        r"\b[a-z]+://[^/\s:]+:[^@\s]+@",
        re.IGNORECASE,
    )

    PASSWORD_PATTERN = re.compile(
        r"(password\s*[:=]\s*\S+)",
        re.IGNORECASE,
    )

    TOKEN_PATTERN = re.compile(
        r"(token\s*[:=]\s*\S+)",
        re.IGNORECASE,
    )

    API_KEY_PATTERN = re.compile(
        r"(api[_\- ]?key\s*[:=]\s*\S+)",
        re.IGNORECASE,
    )

    SECRET_PATTERN = re.compile(
        r"(secret\s*[:=]\s*\S+)",
        re.IGNORECASE,
    )

    def validate(
        self,
        content: str,
    ) -> ValidationResult:
        """
        Validate generated content.

        Returns:
            ValidationResult
        """

        if not isinstance(content, str):
            raise TypeError(
                "Content must be a string."
            )

        if self.CREDENTIAL_URL_PATTERN.search(
            content
        ):
            return ValidationResult(
                allowed=False,
                reason=(
                    "Credential-bearing "
                    "connection string detected."
                ),
            )

        if self.PASSWORD_PATTERN.search(
            content
        ):
            return ValidationResult(
                allowed=False,
                reason=(
                    "Password disclosure detected."
                ),
            )

        if self.TOKEN_PATTERN.search(
            content
        ):
            return ValidationResult(
                allowed=False,
                reason=(
                    "Token disclosure detected."
                ),
            )

        if self.API_KEY_PATTERN.search(
            content
        ):
            return ValidationResult(
                allowed=False,
                reason=(
                    "API key disclosure detected."
                ),
            )

        if self.SECRET_PATTERN.search(
            content
        ):
            return ValidationResult(
                allowed=False,
                reason=(
                    "Secret disclosure detected."
                ),
            )

        return ValidationResult(
            allowed=True,
            reason="Content passed validation.",
        )
