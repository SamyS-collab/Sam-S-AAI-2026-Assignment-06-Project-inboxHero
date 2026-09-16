# Gatekeeper

"""
Responsibilities:
- Evaluate action safety
- Determine if approval is required
- Classify reversible vs irreversible actions
- Produce gate decisions

Non-responsibilities:
- Collect approvals
- Write files
- Generate replies
- Send email
- Call LLMs
"""

from __future__ import annotations

from dataclasses import dataclass

from core.dispositions import Disposition
from core.disposition_engine import DispositionDecision


@dataclass(frozen=True, slots=True)
class GateDecision:
    """
    Result of action safety evaluation.
    """

    message_id: str
    disposition: Disposition
    reversible: bool
    approval_required: bool
    approved: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "message_id": self.message_id,
            "disposition": self.disposition.value,
            "reversible": self.reversible,
            "approval_required": self.approval_required,
            "approved": self.approved,
            "reason": self.reason,
        }


class Gatekeeper:
    """
    R3 safety gate.

    Evaluates whether a disposition may proceed
    automatically or requires human approval.
    """

    def evaluate(
        self,
        decision: DispositionDecision,
    ) -> GateDecision:
        """
        Evaluate a disposition decision.

        Returns:
            GateDecision
        """

        if not isinstance(
            decision,
            DispositionDecision,
        ):
            raise TypeError(
                "Gatekeeper.evaluate() expects "
                "a DispositionDecision"
            )

        disposition = decision.disposition

        # --------------------------------------
        # Reversible Actions
        # --------------------------------------

        if disposition in {
            Disposition.ARCHIVE,
            Disposition.DEFER,
            Disposition.FLAG,
            Disposition.ESCALATE,
            Disposition.REPLY,
        }:
            return GateDecision(
                message_id=decision.message_id,
                disposition=disposition,
                reversible=True,
                approval_required=False,
                approved=True,
                reason=(
                    "Disposition is currently "
                    "reversible and may proceed "
                    "without human approval."
                ),
            )

        # --------------------------------------
        # Defensive Fallback
        # --------------------------------------

        return GateDecision(
            message_id=decision.message_id,
            disposition=disposition,
            reversible=False,
            approval_required=True,
            approved=False,
            reason=(
                "Unknown action type encountered. "
                "Human review required."
            ),
        )
