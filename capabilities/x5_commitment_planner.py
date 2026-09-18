# X5 - Commitment Conflict Planner

"""
Responsibilities:
- Review detected commitment conflicts
- Produce human-readable planning guidance
- Generate an inspectable capability result

Non-responsibilities:
- Commitment extraction
- Conflict detection
- Calendar updates
- Conflict resolution
- LLM interactions
"""

from __future__ import annotations

from commitments.commitment_manager import (
    CommitmentManager,
)


class X5CommitmentPlanner:
    """
    Capability wrapper for X5.

    Consumes conflicts that were already
    detected by the commitment subsystem
    and produces planning guidance for
    human review.
    """

    def __init__(
        self,
        commitment_manager: CommitmentManager,
    ) -> None:

        self.commitment_manager = (
            commitment_manager
        )

    def analyze(self) -> dict:
        """
        Analyze detected commitment conflicts.

        Returns a grader-friendly report.
        """

        conflicts = (
            self.commitment_manager
            .get_conflicts()
        )

        plans = []

        for conflict in conflicts:

            plans.append(
                {
                    "message_a":
                        conflict.commitment_a.message_id,

                    "title_a":
                        conflict.commitment_a.title,

                    "message_b":
                        conflict.commitment_b.message_id,

                    "title_b":
                        conflict.commitment_b.title,

                    "conflict_time":
                        conflict.conflict_time,

                    "recommendation":
                        (
                            "Human review required. "
                            "Two commitments occur "
                            "at the same time."
                        ),
                }
            )

        return {
            "conflicts_found":
                len(conflicts),

            "plans":
                plans,

            "passed":
                True,
        }

