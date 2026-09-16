# Commitment Manager

"""
Responsibilities:
- Build commitments from messages
- Detect conflicts
- Persist commitments
- Persist conflicts
- Provide retrieval APIs

Non-responsibilities:
- Commitment extraction logic
- Conflict detection logic
- Dashboard generation
- LLM interactions
"""

from __future__ import annotations

import json
from pathlib import Path

from commitments.extractor import (
    Commitment,
    CommitmentExtractor,
)

from commitments.conflict_detector import (
    ConflictDetector,
    CommitmentConflict,
)


class CommitmentManager:
    """
    Orchestrates commitment extraction,
    conflict detection, and persistence.
    """

    DEFAULT_DATA = {
        "commitments": [],
        "conflicts": [],
    }

    def __init__(
        self,
        data_path: str = "data/commitments.json",
        extractor: CommitmentExtractor | None = None,
        detector: ConflictDetector | None = None,
    ) -> None:

        project_root = Path(__file__).resolve().parent.parent

        self.data_path = project_root / data_path

        self.data_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.extractor = (
            extractor or CommitmentExtractor()
        )

        self.detector = (
            detector or ConflictDetector()
        )

        self.commitments: list[
            Commitment
        ] = []

        self.conflicts: list[
            CommitmentConflict
        ] = []

        self._initialize_storage()

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------

    def _initialize_storage(self) -> None:

        if not self.data_path.exists():
            self.save()

    # --------------------------------------------------
    # Build
    # --------------------------------------------------

    def build(
        self,
        messages,
    ) -> None:
        """
        Build commitments and conflicts
        from message objects.
        """

        self.commitments = []

        for message in messages:

            commitment = (
                self.extractor.extract(
                    message
                )
            )

            if commitment:
                self.commitments.append(
                    commitment
                )

        self.conflicts = (
            self.detector.detect(
                self.commitments
            )
        )

    # --------------------------------------------------
    # Retrieval
    # --------------------------------------------------

    def get_commitments(
        self,
    ) -> list[Commitment]:

        return list(self.commitments)

    def get_conflicts(
        self,
    ) -> list[CommitmentConflict]:

        return list(self.conflicts)

    # --------------------------------------------------
    # Persistence
    # --------------------------------------------------

    def save(
        self,
    ) -> None:
        """
        Persist commitments and conflicts.
        """

        payload = {
            "commitments": [
                commitment.to_dict()
                for commitment
                in self.commitments
            ],
            "conflicts": [
                {
                    "commitment_a_id":
                        conflict.commitment_a.message_id,

                    "commitment_b_id":
                        conflict.commitment_b.message_id,

                    "conflict_time":
                        conflict.conflict_time,
                }
                for conflict
                in self.conflicts
            ],
        }

        with open(
            self.data_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                payload,
                file,
                indent=4,
                ensure_ascii=False,
            )

    def load(
        self,
    ) -> dict:

        with open(
            self.data_path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

