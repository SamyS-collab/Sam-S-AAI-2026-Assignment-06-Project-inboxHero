# Dashboard Builder

"""
Responsibilities:
- Build dashboard data
- Validate dashboard item structure
- Aggregate exactly three dashboard panes
- Produce the canonical Dashboard model

Non-responsibilities:
- HTML rendering
- Security analysis
- Commitment extraction
- Conflict detection
- Disposition decisions
- LLM interactions
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from commitments.extractor import Commitment
from commitments.conflict_detector import (
    CommitmentConflict,
)


@dataclass(frozen=True, slots=True)
class Dashboard:
    """
    Canonical dashboard model.

    Part 7 requires exactly three panes:

    1. Pending Actions
    2. Flagged Items
    3. Commitments
    """

    pending_actions: list[dict[str, Any]]
    flagged_items: list[dict[str, Any]]
    commitments: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """
        Return a JSON-serializable dashboard representation.

        Exactly three top-level keys are returned.
        """

        return {
            "pending_actions": self.pending_actions,
            "flagged_items": self.flagged_items,
            "commitments": self.commitments,
        }


class DashboardBuilder:
    """
    Builds the InboxHero dashboard data model.

    The resulting dashboard always contains exactly
    the three panes required by Part 7.
    """

    REQUIRED_PENDING_ACTION_FIELDS = {
        "message_id",
        "action",
        "human_reason",
    }

    REQUIRED_FLAGGED_ITEM_FIELDS = {
        "message_id",
        "threat_type",
        "attempted_action",
        "system_response",
    }

    # --------------------------------------------------
    # Dashboard Build
    # --------------------------------------------------

    def _require_non_empty_string(
        self,
        value: str,
        field_name: str,
    ) -> None:
        """
        Validate required string fields.
        """

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        if not value.strip():
            raise ValueError(
                f"{field_name} cannot be empty."
            )

    def build(
        self,
        pending_actions: list[dict[str, Any]],
        flagged_items: list[dict[str, Any]],
        commitments: list[Commitment],
        conflicts: list[CommitmentConflict],
    ) -> Dashboard:
        """
        Build the canonical dashboard model.

        Args:
            pending_actions:
                Actions requiring human involvement.

            flagged_items:
                Items on which the system refused to act.

            commitments:
                Commitments extracted from inbox messages.

            conflicts:
                Conflicts detected between commitments.

        Returns:
            Dashboard containing exactly three panes.
        """

        self._validate_pending_actions(
            pending_actions
        )

        self._validate_flagged_items(
            flagged_items
        )

        self._validate_commitments(
            commitments
        )

        self._validate_conflicts(
            conflicts
        )

        commitment_entries = [
            commitment.to_dict()
            for commitment in commitments
        ]

        conflict_entries = [
            conflict.to_dict()
            for conflict in conflicts
        ]

        return Dashboard(
            pending_actions=[
                dict(item)
                for item in pending_actions
            ],
            flagged_items=[
                dict(item)
                for item in flagged_items
            ],
            commitments={
                "items": commitment_entries,
                "conflicts": conflict_entries,
            },
        )

    # --------------------------------------------------
    # Pending Action Builder
    # --------------------------------------------------

    def build_pending_action(
        self,
        message_id: str,
        action: str,
        human_reason: str,
    ) -> dict[str, str]:
        """
        Build a rubric-compliant pending-action row.

        Each pending action identifies:
        - the source message
        - the proposed action
        - why human involvement is required
        """

        self._require_non_empty_string(
            value=message_id,
            field_name="message_id",
        )

        self._require_non_empty_string(
            value=action,
            field_name="action",
        )

        self._require_non_empty_string(
            value=human_reason,
            field_name="human_reason",
        )

        return {
            "message_id": message_id,
            "action": action,
            "human_reason": human_reason,
        }

    # --------------------------------------------------
    # Flagged Item Builder
    # --------------------------------------------------

    def build_flagged_item(
        self,
        message_id: str,
        threat_type: str,
        attempted_action: str,
        system_response: str,
    ) -> dict[str, str]:
        """
        Build a rubric-compliant flagged-item row.

        Each flagged item identifies:
        - the source message
        - the detected threat or grounding failure
        - what was attempted
        - what the system did instead
        """

        self._require_non_empty_string(
            value=message_id,
            field_name="message_id",
        )

        self._require_non_empty_string(
            value=threat_type,
            field_name="threat_type",
        )

        self._require_non_empty_string(
            value=attempted_action,
            field_name="attempted_action",
        )

        self._require_non_empty_string(
            value=system_response,
            field_name="system_response",
        )

        return {
            "message_id": message_id,
            "threat_type": threat_type,
            "attempted_action": attempted_action,
            "system_response": system_response,
        }

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def _validate_pending_actions(
        self,
        pending_actions: list[dict[str, Any]],
    ) -> None:
        """
        Validate all pending-action rows.
        """

        if not isinstance(
            pending_actions,
            list,
        ):
            raise TypeError(
                "pending_actions must be a list"
            )

        for index, item in enumerate(
            pending_actions
        ):
            if not isinstance(item, dict):
                raise TypeError(
                    "Each pending action must be "
                    f"a dictionary. Invalid index: {index}"
                )

            missing_fields = (
                self.REQUIRED_PENDING_ACTION_FIELDS
                - item.keys()
            )

            if missing_fields:
                raise ValueError(
                    "Pending action is missing "
                    f"required fields: "
                    f"{sorted(missing_fields)}"
                )

            for field_name in (
                self.REQUIRED_PENDING_ACTION_FIELDS
            ):
                self._require_non_empty_string(
                    value=item[field_name],
                    field_name=field_name,
                )

    def _validate_flagged_items(
        self,
        flagged_items: list[dict[str, Any]],
    ) -> None:
        """
        Validate all flagged-item rows.
        """

        if not isinstance(
            flagged_items,
            list,
        ):
            raise TypeError(
                "flagged_items must be a list"
            )

        for index, item in enumerate(
            flagged_items
        ):
            if not isinstance(item, dict):
                raise TypeError(
                    "Each flagged item must be "
                    f"a dictionary. Invalid index: {index}"
                )

            missing_fields = (
                self.REQUIRED_FLAGGED_ITEM_FIELDS
                - item.keys()
            )

            if missing_fields:
                raise ValueError(
                    "Flagged item is missing "
                    f"required fields: "
                    f"{sorted(missing_fields)}"
                )

            for field_name in (
                self.REQUIRED_FLAGGED_ITEM_FIELDS
            ):
                self._require_non_empty_string(
                    value=item[field_name],
                    field_name=field_name,
                )

    @staticmethod
    def _validate_commitments(
        commitments: list[Commitment],
    ) -> None:
        """
        Verify that commitments use the canonical model.
        """

        if not isinstance(commitments, list):
            raise TypeError(
                "commitments must be a list"
            )

        for commitment in commitments:
            if not isinstance(
                commitment,
                Commitment,
            ):
                raise TypeError(
                    "Each commitment must be "
                    "a Commitment object"
                )

    @staticmethod
    def _validate_conflicts(
        conflicts: list[CommitmentConflict],
    ) -> None:
        """
        Verify that conflicts use the canonical model.
        """

        if not isinstance(conflicts, list):
            raise TypeError(
                "conflicts must be a list"
            )

   
