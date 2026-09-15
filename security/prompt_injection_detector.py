# Security/prompt_injection_detector

"""
R5 - Hostile Inbox Protection

Detects prompt injection attempts using deterministic rules.

Responsibilities:
- Detect instruction override attempts
- Detect policy bypass attempts
- Detect data exfiltration requests
- Explain why detection occurred

Does NOT:
- Assign dispositions
- Delete messages
- Execute actions
"""

from __future__ import annotations

from dataclasses import dataclass

from core.message_model import Message


PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "override instructions",
    "bypass security",
    "reveal confidential",
    "reveal internal",
    "share credentials",
    "send me all emails",
    "forward all messages",
    "export mailbox",
    "act as administrator",
    "act as system",
    "ignore company policy",
    "do not tell the user",
    "delete this message",
    "delete all messages",
]


@dataclass(slots=True)
class PromptInjectionResult:
    detected: bool
    reasons: list[str]


class PromptInjectionDetector:
    """
    Rule-based detector.

    Security First architecture:
    Detection only.
    No actions executed here.
    """

    def analyze(
        self,
        message: Message,
    ) -> PromptInjectionResult:

        text = message.text.lower()

        reasons: list[str] = []

        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern in text:
                reasons.append(
                    f"Matched pattern: '{pattern}'"
                )

        return PromptInjectionResult(
            detected=len(reasons) > 0,
            reasons=reasons,
        )

