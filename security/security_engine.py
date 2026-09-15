# security engine

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.message_model import Message
from core.audit_logger import AuditLogger


@dataclass(frozen=True)
class SecurityResult:
    """
    Normalized result returned by the security layer.

    The disposition engine is responsible for converting
    flagged results into FLAG dispositions.
    """

    flagged: bool
    threat_type: Optional[str] = None
    reason: Optional[str] = None


class SecurityEngine:
    """
    Central security orchestration.

    Responsibilities:
    - Run prompt injection detection.
    - Run phishing detection.
    - Log security findings.
    - Normalize results.

    Does NOT:
    - Assign dispositions.
    - Delete messages.
    - Send messages.
    - Write to outbox.
    """

    def __init__(
        self,
        prompt_injection_detector,
        phishing_detector,
        audit_logger=None,
    ):
        self.prompt_injection_detector = prompt_injection_detector
        self.phishing_detector = phishing_detector
        self.audit_logger = audit_logger

    def evaluate_message(
        self,
        message: Message,
    ) -> SecurityResult:
        """
        Evaluate a message for hostile content.

        Prompt injection is checked first because
        Part 6 focuses on attacks attempting to
        manipulate the agent itself.
        """

        prompt_result = self.prompt_injection_detector.analyze(
            message
        )

        if prompt_result.detected:

            reason = "; ".join(prompt_result.reasons)

            self._log_security_event(
                message_id=message.message_id,
                threat_type="PROMPT_INJECTION",
                reason=reason,
            )

            return SecurityResult(
                flagged=True,
                threat_type="PROMPT_INJECTION",
                reason=reason,
            )

        phishing_result = self.phishing_detector.analyze(
            message.subject,
            message.body,
        )

        if phishing_result["is_phishing"]:

            reason = "; ".join(
                phishing_result["reasons"]
            )

            self._log_security_event(
                message_id=message.message_id,
                threat_type="PHISHING",
                reason=reason,
            )

            return SecurityResult(
                flagged=True,
                threat_type="PHISHING",
                reason=reason,
            )

        return SecurityResult(flagged=False)

    def _log_security_event(
        self,
        message_id: str,
        threat_type: str,
        reason: str,
    ) -> None:

        if self.audit_logger is None:
            return

        self.audit_logger.log(
            "SECURITY_FLAGGED",
            message_id=message_id,
            threat_type=threat_type,
            action="REFUSED_AND_FLAGGED",
            reason=reason,
        )