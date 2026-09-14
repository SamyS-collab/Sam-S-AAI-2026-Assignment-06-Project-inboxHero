# InboxHero Disposition Engine
"""
Responsibilities:
- Assign exactly one disposition to every message
- Assign a non-empty reason for every disposition
- Use the category previously assigned by the Router
- Record the decision in message metadata
- Identify messages that require additional model-assisted analysis

Non-responsibilities:
- Message classification
- Prompt-injection detection
- Phishing detection
- LLM calls
- Sending messages
- Human approval

Part 2: Zeroing It
Every message must finish with exactly one disposition and a stated reason.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.dispositions import Disposition
from core.message_model import Message


@dataclass(frozen=True, slots=True)
class DispositionDecision:
    """
    Immutable result produced by the DispositionEngine.

    Attributes:
        message_id:
            ID of the message receiving the disposition.

        disposition:
            Exactly one canonical InboxHero disposition.

        reason:
            Human-readable explanation for the decision.

        category:
            Category previously assigned by the Router.

        handled_by:
            Component responsible for the decision.

        model_required:
            True when a later LLM fallback must analyze the message.
    """

    message_id: str
    disposition: Disposition
    reason: str
    category: str
    handled_by: str
    model_required: bool

    def to_dict(self) -> dict[str, object]:
        """
        Return a JSON-serializable representation.
        """

        return {
            "message_id": self.message_id,
            "category": self.category,
            "disposition": self.disposition.value,
            "reason": self.reason,
            "handled_by": self.handled_by,
            "model_required": self.model_required,
        }


class DispositionEngine:
    """
    Assigns one disposition and one reason to every routed message.

    This engine expects the Router to have stored the category in:

        message.metadata["category"]

    Rule-handled categories receive deterministic dispositions.

    Unknown messages receive a safe DEFER disposition and are marked as
    requiring later model-assisted analysis. The LLM fallback can replace
    that preliminary decision before the final Part 2 report is generated.
    """

    CATEGORY_NEWSLETTER = "newsletter"
    CATEGORY_RECEIPT = "receipt"
    CATEGORY_NOTIFICATION = "notification"
    CATEGORY_MEETING = "meeting"
    CATEGORY_UNKNOWN = "unknown"

    ACTIONABLE_NOTIFICATION_SUBJECTS = {
        "appointment",
        "timesheet",
        "check-in is open",
        "event was scheduled",
    }

    ACTIONABLE_NOTIFICATION_BODIES = {
        "submit your timesheet",
        "reply confirm",
        "reply confirm to keep",
        "reply reschedule",
        "check in for",
    }

    def assign(self, message: Message) -> DispositionDecision:
        """
        Assign exactly one disposition and a non-empty reason.

        Args:
            message:
                A Message that has already passed through Router.route().

        Returns:
            DispositionDecision:
                The disposition, reason, category and processing metadata.

        Raises:
            TypeError:
                If message is not a Message instance.

            ValueError:
                If the message has no valid category or the generated
                decision is incomplete.
        """

        if not isinstance(message, Message):
            raise TypeError(
                "DispositionEngine.assign() expects a Message instance"
            )

        category_value = message.metadata.get(
            "category",
            self.CATEGORY_UNKNOWN,
        )

        if not isinstance(category_value, str):
            raise ValueError(
                f"Invalid category for message {message.message_id}: "
                f"{category_value!r}"
            )

        category = category_value.strip().lower()

        if not category:
            category = self.CATEGORY_UNKNOWN

        decision = self._decide(
            message=message,
            category=category,
        )

        self._validate_decision(decision)
        self._store_decision(message, decision)

        return decision

    def _decide(
        self,
        message: Message,
        category: str,
    ) -> DispositionDecision:
        """
        Apply deterministic disposition rules.

        Rule priority:

        1. Newsletter
        2. Receipt
        3. Meeting
        4. Actionable notification
        5. Informational notification
        6. Unknown fallback
        """

        if category == self.CATEGORY_NEWSLETTER:
            return self._build_decision(
                message=message,
                category=category,
                disposition=Disposition.ARCHIVE,
                reason=(
                    "Newsletter detected by the rule-based classifier; "
                    "no reply or further action is required."
                ),
                handled_by="rule",
                model_required=False,
            )

        if category == self.CATEGORY_RECEIPT:
            return self._build_decision(
                message=message,
                category=category,
                disposition=Disposition.ARCHIVE,
                reason=(
                    "Receipt, invoice, bill, or purchase confirmation "
                    "detected by the rule-based classifier."
                ),
                handled_by="rule",
                model_required=False,
            )

        if category == self.CATEGORY_MEETING:
            return self._build_decision(
                message=message,
                category=category,
                disposition=Disposition.REPLY,
                reason=(
                    "Meeting or scheduling request detected; "
                    "a response must be drafted before any commitment "
                    "is made."
                ),
                handled_by="rule",
                model_required=False,
            )

        if category == self.CATEGORY_NOTIFICATION:
            return self._notification_decision(message, category)

        return self._build_decision(
            message=message,
            category=category,
            disposition=Disposition.DEFER,
            reason=(
                "Message was not resolved by the rule-based classifiers "
                "and requires additional analysis."
            ),
            handled_by="fallback_pending",
            model_required=True,
        )

    def _notification_decision(
        self,
        message: Message,
        category: str,
    ) -> DispositionDecision:
        """
        Separate actionable notifications from informational notifications.

        This avoids archiving reminders such as timesheets, appointments,
        scheduled events and travel check-in notices.
        """

        subject = message.subject.casefold()
        body = message.body.casefold()

        actionable_subject = any(
            keyword in subject
            for keyword in self.ACTIONABLE_NOTIFICATION_SUBJECTS
        )

        actionable_body = any(
            keyword in body
            for keyword in self.ACTIONABLE_NOTIFICATION_BODIES
        )

        if actionable_subject or actionable_body:
            return self._build_decision(
                message=message,
                category=category,
                disposition=Disposition.DEFER,
                reason=(
                    "Notification contains a future action, reminder "
                    "appointment, event, or deadline that must be tracked."
                ),
                handled_by="rule",
                model_required=False,
            )

        return self._build_decision(
            message=message,
            category=category,
            disposition=Disposition.ARCHIVE,
            reason=(
                "Informational notification detected by the rule-based "
                "classifier; no direct response is required."
            ),
            handled_by="rule",
            model_required=False,
        )

    @staticmethod
    def _build_decision(
        message: Message,
        category: str,
        disposition: Disposition,
        reason: str,
        handled_by: str,
        model_required: bool,
    ) -> DispositionDecision:
        """
        Construct a disposition decision.
        """

        return DispositionDecision(
            message_id=message.message_id,
            disposition=disposition,
            reason=reason,
            category=category,
            handled_by=handled_by,
            model_required=model_required,
        )

    @staticmethod
    def _validate_decision(
        decision: DispositionDecision,
    ) -> None:
        """
        Ensure the decision satisfies Part 2 requirements.
        """

        if not isinstance(decision.disposition, Disposition):
            raise ValueError(
                f"Message {decision.message_id} has an invalid disposition"
            )

        if not decision.reason.strip():
            raise ValueError(
                f"Message {decision.message_id} has no disposition reason"
            )

        if not decision.category.strip():
            raise ValueError(
                f"Message {decision.message_id} has no category"
            )

        if not decision.handled_by.strip():
            raise ValueError(
                f"Message {decision.message_id} has no processing source"
            )

    @staticmethod
    def _store_decision(
        message: Message,
        decision: DispositionDecision,
    ) -> None:
        """
        Store the decision on the Message metadata.

        This works with the currently frozen Message model without adding
        disposition fields to the dataclass.
        """

        message.metadata["disposition"] = decision.disposition.value
        message.metadata["disposition_reason"] = decision.reason
        message.metadata["handled_by"] = decision.handled_by
        message.metadata["model_required"] = decision.model_required
