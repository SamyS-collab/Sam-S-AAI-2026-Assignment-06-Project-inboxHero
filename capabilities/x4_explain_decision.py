# X4 - Explain Why Decision Was Made

"""
Responsibilities:
- Explain disposition decisions
- Expose stored decision metadata
- Produce an inspectable capability report

Non-responsibilities:
- Generate new explanations
- Reclassify messages
- Reassign dispositions
- Call LLMs
- Modify message metadata
"""

from __future__ import annotations

from core.message_model import Message


class X4ExplainDecision:
    """
    Capability wrapper for X4.

    Uses the explanation data already
    stored by the DispositionEngine.
    """

    def explain(
        self,
        message: Message,
    ) -> dict[str, object]:
        """
        Explain why a disposition was assigned.

        Returns a grader-friendly report.
        """

        disposition = message.metadata.get(
            "disposition"
        )

        reason = message.metadata.get(
            "disposition_reason"
        )

        handled_by = message.metadata.get(
            "handled_by"
        )

        model_required = message.metadata.get(
            "model_required"
        )

        category = message.metadata.get(
            "category"
        )

        return {
            "message_id":
                message.message_id,

            "subject":
                message.subject,

            "category":
                category,

            "disposition":
                disposition,

            "reason":
                reason,

            "handled_by":
                handled_by,

            "model_required":
                model_required,

            "passed":
                (
                    bool(disposition)
                    and
                    bool(reason)
                ),
        }