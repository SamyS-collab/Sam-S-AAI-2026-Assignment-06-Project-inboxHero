# R5 Hostile Inbox Protection

"""
Responsibilities:
- Evaluate messages using SecurityEngine
- Refuse hostile instructions
- Flag hostile messages
- Log hostile message handling
- Generate user notifications

Non-responsibilities:
- Prompt injection detection
- Phishing detection
- Message deletion
- Dashboard rendering
- LLM interactions
"""

from dataclasses import dataclass

from core.message_model import Message
from core.audit_logger import AuditLogger


@dataclass(frozen=True)
class HostileInboxResult:

    message_id: str
    threat_type: str
    refused: bool
    flagged: bool
    notification: str

    def to_dict(self):

        return {
            "message_id": self.message_id,
            "threat_type": self.threat_type,
            "refused": self.refused,
            "flagged": self.flagged,
            "notification": self.notification,
        }


class HostileInboxProtection:

    def __init__(
        self,
        security_engine,
        logger=None,
    ):
        if security_engine is None:
            raise ValueError(
                "HostileInboxProtection requires "
                "a SecurityEngine instance."
            )

        self.security_engine = security_engine
        self.logger = logger or AuditLogger()
        
    def evaluate(
        self,
        message,
    ):

        result = (
            self.security_engine.evaluate_message(
                message
            )
        )

        if not result.flagged:
            return None

        notification = (
            self._build_notification(
                result.threat_type
            )
        )

        self.logger.log(
            "HOSTILE_MESSAGE_DETECTED",
            message_id=message.message_id,
            threat_type=result.threat_type,
        )

        self.logger.log(
            "HOSTILE_MESSAGE_REFUSED",
            message_id=message.message_id,
            threat_type=result.threat_type,
        )

        self.logger.log(
            "USER_NOTIFICATION_CREATED",
            message_id=message.message_id,
            threat_type=result.threat_type,
        )

        return HostileInboxResult(
            message_id=message.message_id,
            threat_type=(
                result.threat_type
                or "UNKNOWN"
            ),
            refused=True,
            flagged=True,
            notification=notification,
        )

    @staticmethod
    def _build_notification(
        threat_type,
    ):

        if threat_type == "PHISHING":
            return (
                "Potential phishing attempt "
                "was refused and flagged."
            )

        if threat_type == "PROMPT_INJECTION":
            return (
                "Prompt-injection attempt "
                "was refused and flagged."
            )

        return (
            "Potential hostile message "
            "was refused and flagged."
        )
