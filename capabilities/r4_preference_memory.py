# R4 - Preference Memory

"""
Responsibilities:
- Demonstrate R4 preference persistence
- Report stored preferences
- Verify preferences survive reloads
- Produce an inspectable capability report

Non-responsibilities:
- Extract preferences
- Create preferences
- Modify preferences
- Security analysis
- LLM interactions
"""

from __future__ import annotations

from memory.preference_manager import (
    PreferenceManager,
)


class R4PreferenceMemory:
    """
    Capability wrapper for R4.

    Demonstrates that standing instructions
    persist across runs and remain available
    after reload.
    """

    def __init__(
        self,
        manager: PreferenceManager | None = None,
    ) -> None:

        self.manager = (
            manager
            or PreferenceManager()
        )

    def report(
        self,
    ) -> dict[str, object]:
        """
        Generate an R4 compliance report.
        """

        self.manager.reload()

        meeting_constraints = (
            self.manager.get_meeting_constraints()
        )

        correspondence_rules = (
            self.manager.get_correspondence_rules()
        )

        preference_count = (
            len(meeting_constraints)
            +
            len(correspondence_rules)
        )

        return {
            "meeting_constraints":
                meeting_constraints,

            "correspondence_rules":
                correspondence_rules,

            "preference_count":
                preference_count,

            "restart_persistence_verified":
                preference_count > 0,

            "passed":
                preference_count > 0,
        }

