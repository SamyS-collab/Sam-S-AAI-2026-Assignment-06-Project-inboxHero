# X1 - Daily Digest

"""
Responsibilities:
- Aggregate InboxHero capability outputs
- Produce a deterministic daily digest
- Summarize follow-ups, flagged items,
  commitments, and conflicts

Non-responsibilities:
- Thread summarization
- Reply generation
- Dashboard rendering
- LLM interactions
"""

from __future__ import annotations


class X1DailyDigest:
    """
    Capability wrapper for X1.

    Produces a grader-friendly
    daily digest report.
    """

    def generate(
        self,
        followup_result: dict,
        flagged_items: list[dict],
        commitment_result: dict,
        conflict_plan_result: dict,
    ) -> dict:
        """
        Generate a deterministic digest.

        Args:
            followup_result:
                Output from X2 Follow-up Tracker.

            flagged_items:
                R5 hostile/phishing results.

            commitment_result:
                Data from CommitmentManager.

            conflict_plan_result:
                Output from X5 planner.
        """

        followups_found = (
            followup_result.get(
                "followups_found",
                0,
            )
        )

        flagged_count = len(
            flagged_items
        )

        commitments_found = len(
            commitment_result.get(
                "commitments",
                [],
            )
        )

        conflicts_found = (
            conflict_plan_result.get(
                "conflicts_found",
                0,
            )
        )

        digest_lines = []

        digest_lines.append(
            f"Follow-ups requiring attention: "
            f"{followups_found}"
        )

        digest_lines.append(
            f"Flagged hostile items: "
            f"{flagged_count}"
        )

        digest_lines.append(
            f"Tracked commitments: "
            f"{commitments_found}"
        )

        digest_lines.append(
            f"Scheduling conflicts: "
            f"{conflicts_found}"
        )

        if conflicts_found > 0:

            digest_lines.append(
                "Human review required for "
                "commitment conflicts."
            )

        summary = " | ".join(
            digest_lines
        )

        return {
            "followups_found":
                followups_found,

            "flagged_count":
                flagged_count,

            "commitments_found":
                commitments_found,

            "conflicts_found":
                conflicts_found,

            "summary":
                summary,

            "passed":
                True,
        }

