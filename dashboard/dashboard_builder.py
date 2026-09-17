# Dashboard Builder

"""
Responsibilities:
- Build dashboard data
- Aggregate dashboard panes
- Produce dashboard model

Non-responsibilities:
- HTML rendering
- Security analysis
- Commitment extraction
- Conflict detection
- LLM interactions
"""

from __future__ import annotations

from dataclasses import dataclass

from commitments.extractor import Commitment
from commitments.conflict_detector import (
    CommitmentConflict,
)


@dataclass(frozen=True, slots=True)
class Dashboard:
    """
    Canonical dashboard model.

    R6 requires exactly three panes.
    """

    pending_actions: list[dict]
    flagged_items: list[dict]
    commitments: dict

    def to_dict(self) -> dict:
        """
        JSON serializable dashboard representation.
        """

        return {
            "pending_actions": self.pending_actions,
            "flagged_items": self.flagged_items,
            "commitments": self.commitments,
        }


class DashboardBuilder:
    """
    Builds the InboxHero dashboard.

    Produces exactly three panes:

    1. Pending Actions
    2. Flagged Items
    3. Commitments
    """

    def build(
        self,
        pending_actions: list[dict],
        flagged_items: list[dict],
        commitments: list[Commitment],
        conflicts: list[CommitmentConflict],
    ) -> Dashboard:
        """
        Build dashboard model.
        """

        commitment_entries = [
            commitment.to_dict()
            for commitment in commitments
        ]

        conflict_entries = [
            conflict.to_dict()
            for conflict in conflicts
        ]

        return Dashboard(
            pending_actions=pending_actions,
            flagged_items=flagged_items,
            commitments={
                "items": commitment_entries,
                "conflicts": conflict_entries,
            },
        )
