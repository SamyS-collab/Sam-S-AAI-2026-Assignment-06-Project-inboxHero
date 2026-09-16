# Conflict Detector

"""
Responsibilities:
- Detect conflicting commitments
- Compare commitment schedules
- Return conflict records

Non-responsibilities:
- Commitment extraction
- Commitment persistence
- Dashboard generation
- LLM interactions
"""

from __future__ import annotations

from dataclasses import dataclass

from commitments.extractor import Commitment


@dataclass(frozen=True, slots=True)
class CommitmentConflict:
    """
    Represents a scheduling conflict between
    two commitments.
    """

    commitment_a: Commitment
    commitment_b: Commitment
    conflict_time: str

    def to_dict(self) -> dict:
        return {
            "commitment_a": (
                self.commitment_a.to_dict()
            ),
            "commitment_b": (
                self.commitment_b.to_dict()
            ),
            "conflict_time": self.conflict_time,
        }


class ConflictDetector:
    """
    Deterministic commitment conflict detector.

    Detects overlapping commitments by
    comparing normalized event timestamps.
    """

    def detect(
        self,
        commitments: list[Commitment],
    ) -> list[CommitmentConflict]:
        """
        Detect scheduling conflicts.

        Returns:
            list[CommitmentConflict]
        """

        conflicts: list[
            CommitmentConflict
        ] = []

        for index, current in enumerate(
            commitments
        ):

            if current.event_time == "UNKNOWN":
                continue

            for candidate in commitments[
                index + 1:
            ]:

                if (
                    candidate.event_time
                    == "UNKNOWN"
                ):
                    continue

                if (
                    current.event_time
                    == candidate.event_time
                ):

                    conflicts.append(
                        CommitmentConflict(
                            commitment_a=current,
                            commitment_b=candidate,
                            conflict_time=(
                                current.event_time
                            ),
                        )
                    )

        return conflicts
