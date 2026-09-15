# Preference Manager

"""
Responsibilities:
- Manage standing preferences
- Load preferences from PreferenceStore
- Save preference updates
- Provide preference lookup APIs
- Audit preference operations

Non-responsibilities:
- Message classification
- Security analysis
- LLM interactions
- Reply generation
- Preference extraction from messages
"""

from __future__ import annotations

from typing import Any

from core.audit_logger import AuditLogger
from memory.preference_store import PreferenceStore


class PreferenceManager:
    """
    Business layer for Standing Instructions (R4).
    """

    def __init__(
        self,
        store: PreferenceStore | None = None,
        logger: AuditLogger | None = None,
    ) -> None:
        self.store = store or PreferenceStore()
        self.logger = logger or AuditLogger()

        self.preferences = self.store.load()

        self.logger.log(
            "PREFERENCES_LOADED",
            meeting_constraints=len(
                self.preferences.get(
                    "meeting_constraints",
                    []
                )
            ),
            correspondence_rules=len(
                self.preferences.get(
                    "correspondence_rules",
                    []
                )
            ),
        )

    # --------------------------------------------------
    # Persistence
    # --------------------------------------------------

    def save(self) -> None:
        """
        Persist preferences.
        """

        self.store.save(self.preferences)

        self.logger.log(
            "PREFERENCES_SAVED"
        )

    def reload(self) -> None:
        """
        Reload preferences from disk.
        """

        self.preferences = self.store.load()

        self.logger.log(
            "PREFERENCES_RELOADED"
        )

    # --------------------------------------------------
    # Meeting Constraints
    # --------------------------------------------------

    def add_meeting_constraint(
            self,
            source_message_id: str,
            instruction: str,
        ) -> None:
            """
            Add standing meeting rule.

            Duplicate rules are ignored.
            """

            constraints = self.preferences.setdefault(
                "meeting_constraints",
                []
            )

            for constraint in constraints:
                if (
                    constraint.get("source_message_id")
                    == source_message_id
                    and
                    constraint.get("instruction")
                    == instruction
                ):
                    self.logger.log(
                        "MEETING_CONSTRAINT_DUPLICATE_SKIPPED",
                        source_message_id=source_message_id,
                        instruction=instruction,
                    )
                    return

            constraints.append(
                {
                    "source_message_id": source_message_id,
                    "instruction": instruction,
                }
            )

            self.save()

            self.logger.log(
                "MEETING_CONSTRAINT_ADDED",
                source_message_id=source_message_id,
                instruction=instruction,
            )

    def get_meeting_constraints(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all meeting constraints.
        """

        return self.preferences.get(
            "meeting_constraints",
            []
        )

    # --------------------------------------------------
    # Correspondence Rules
    # --------------------------------------------------

    def add_correspondence_rule(
        self,
        source_message_id: str,
        instruction: str,
    ) -> None:
        """
        Add standing correspondence rule.

        Duplicate rules are ignored.
        """

        rules = self.preferences.setdefault(
            "correspondence_rules",
            []
        )

        for rule in rules:
            if (
                rule.get("source_message_id")
                == source_message_id
                and
                rule.get("instruction")
                == instruction
            ):
                self.logger.log(
                    "CORRESPONDENCE_RULE_DUPLICATE_SKIPPED",
                    source_message_id=source_message_id,
                    instruction=instruction,
                )
                return

        rules.append(
            {
                "source_message_id": source_message_id,
                "instruction": instruction,
            }
        )

        self.save()

        self.logger.log(
            "CORRESPONDENCE_RULE_ADDED",
            source_message_id=source_message_id,
            instruction=instruction,
        )

    def get_correspondence_rules(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all correspondence preferences.
        """

        return self.preferences.get(
            "correspondence_rules",
            []
        )

    # --------------------------------------------------
    # Generic Access
    # --------------------------------------------------

    def get_all_preferences(
        self,
    ) -> dict[str, Any]:
        """
        Return entire preference structure.
        """

        return self.preferences
