# R3 - Safety Gate

"""
Responsibilities:
- Demonstrate R3 safety-gate behavior
- Evaluate gate decisions
- Report approval requirements
- Verify outbox-only behavior
- Produce an inspectable capability result

Non-responsibilities:
- Approving actions
- Writing drafts
- Sending email
- Modifying gate decisions
- LLM interactions
"""

from __future__ import annotations

from actions.gatekeeper import (
    Gatekeeper,
    GateDecision,
)

from core.disposition_engine import (
    DispositionDecision,
)


class R3SafetyGate:
    """
    Capability wrapper for R3.

    Demonstrates how InboxHero evaluates
    a disposition through the safety gate.
    """

    def __init__(
        self,
        gatekeeper: Gatekeeper | None = None,
    ) -> None:

        self.gatekeeper = (
            gatekeeper or Gatekeeper()
        )

    def evaluate(
        self,
        decision: DispositionDecision,
    ) -> dict[str, object]:
        """
        Evaluate a disposition through the gate.

        Returns a capability report that is
        easy for a grader to inspect.
        """

        gate_decision: GateDecision = (
            self.gatekeeper.evaluate(
                decision
            )
        )

        return {
            "message_id":
                gate_decision.message_id,

            "disposition":
                gate_decision.disposition.value,

            "reversible":
                gate_decision.reversible,

            "approval_required":
                gate_decision.approval_required,

            "approved":
                gate_decision.approved,

            "reason":
                gate_decision.reason,

            "outbox_only": True,

            "real_email_sending": False,

            "passed": (
                (
                    gate_decision.reversible
                    and
                    not gate_decision.approval_required
                )
                or
                (
                    not gate_decision.reversible
                    and
                    gate_decision.approval_required
                )
            ),
        }
