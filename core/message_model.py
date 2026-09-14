# Inbox Hero - Canonical Message Model

"""
Canonical message representation used throughout the system.

Responsibilities:
- Normalize inbox records
- Validate required fields
- Provide serialization helpers

Non-responsibilities:
- Classification
- Security analysis
- Dispositions
- LLM interactions

"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Message:
    """
    Canonical InboxHero message model.

    All inbox records should be converted to this object
    before any downstream processing occurs.
    """

    message_id: str
    sender: str
    subject: str
    body: str

    timestamp: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """
        Validate required fields.

        Raises:
            ValueError: If required fields are missing.
        """

        if not self.message_id:
            raise ValueError("message_id is required")

        if not self.sender:
            raise ValueError(
                f"sender is required for message {self.message_id}"
            )

        if self.subject is None:
            raise ValueError(
                f"subject is required for message {self.message_id}"
            )

        if self.body is None:
            raise ValueError(
                f"body is required for message {self.message_id}"
            )

    @property
    def text(self) -> str:
        """
        Combined searchable message text.

        Useful for:
        - classifiers
        - retrieval
        - security scanning
        """

        return f"{self.subject}\n\n{self.body}"

    @property
    def is_empty(self) -> bool:
        """
        True if both subject and body are effectively empty.
        """

        return not (
            self.subject.strip() or
            self.body.strip()
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize message back to dictionary form.
        """

        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Message":
        """
        Create Message from inbox payload.

        Supports common field variants while preserving
        the full raw payload inside metadata.

        Accepted aliases:
        - id / message_id
        - sender / from
        """

        message = cls(
            message_id=payload.get(
                "message_id",
                payload.get("id", "")
            ),
            sender=payload.get(
                "sender",
                payload.get("from", "")
            ),
            subject=payload.get(
                "subject",
                ""
            ),
            body=payload.get(
                "body",
                ""
            ),
            timestamp=payload.get(
                "timestamp"
            ),
            metadata=payload.copy(),
        )

        message.validate()

        return message

    def __str__(self) -> str:
        return (
            f"Message("
            f"id={self.message_id}, "
            f"sender={self.sender}, "
            f"subject={self.subject!r}"
            f")"
        )
