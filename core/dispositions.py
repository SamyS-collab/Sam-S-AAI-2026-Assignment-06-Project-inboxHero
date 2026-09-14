# Disposition definitions for InboxHero.

"""
Every message MUST receive exactly one disposition.

Part 2 (Zeroing It):
- Assign every message exactly one disposition.
- Record a reason for the disposition.
"""

from enum import Enum

class Disposition(str, Enum):
    """
    Canonical message dispositions.

    ARCHIVE:
        Informational message requiring no further action.

    REPLY:
        A response can be safely drafted.

    DEFER:
        Action is required later, but not immediately.

    ESCALATE:
        Human review or decision is required.

    FLAG:
        Security, trust, compliance, or policy concern.
    """

    ARCHIVE = "ARCHIVE"
    REPLY = "REPLY"
    DEFER = "DEFER"
    ESCALATE = "ESCALATE"
    FLAG = "FLAG"

    @classmethod
    def values(cls) -> list[str]:
        """
        Return all disposition values.

        Example:
            ['ARCHIVE', 'REPLY', 'DEFER', 'ESCALATE', 'FLAG']
        """
        return [item.value for item in cls]
