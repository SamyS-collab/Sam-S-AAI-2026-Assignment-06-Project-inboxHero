# X2 - Follow-up Tracker

"""
Responsibilities:
- Track messages requiring future action
- Report follow-up workload
- Produce an inspectable capability result

Non-responsibilities:
- Sending reminders
- Modifying messages
- Dashboard rendering
- Commitment management
- LLM interactions
"""

from __future__ import annotations

from core.message_model import Message


class X2FollowupTracker:
    """
    Capability wrapper for X2.

    Tracks messages requiring future action.

    Follow-up candidates:

    - REPLY
    - DEFER
    - ESCALATE
    """

    FOLLOWUP_DISPOSITIONS = {
        "REPLY",
        "DEFER",
        "ESCALATE",
    }

    def analyze(
        self,
        messages: list[Message],
    ) -> dict:
        """
        Inspect messages and identify
        follow-up candidates.
        """

        followups = []

        for message in messages:

            disposition = (
                message.metadata.get(
                    "disposition"
                )
            )

            handled_by = (
                message.metadata.get(
                    "handled_by"
                )
            )

            model_required = (
                message.metadata.get(
                    "model_required"
                )
            )

            if disposition == "ARCHIVE":
                continue

            if disposition == "FLAG":
                continue

            # REPLY and ESCALATE are always follow-ups

            if disposition in {
                "REPLY",
                "ESCALATE",
            }:
                pass

            # DEFER is only a follow-up if it came
            # from a rule-based actionable item

            elif disposition == "DEFER":

                if (
                    handled_by == "fallback_pending"
                    and
                    model_required is True
                ):
                    continue

            else:
                continue


            
            followups.append(
                {
                    "message_id":
                        message.message_id,

                    "subject":
                        message.subject,

                    "disposition":
                        disposition,

                    "reason":
                        message.metadata.get(
                            "disposition_reason"
                        ),

                    "handled_by":
                        message.metadata.get(
                            "handled_by"
                        ),

                    "model_required":
                        message.metadata.get(
                            "model_required"
                        ),
                }
            )

        return {
            "followups_found":
                len(followups),

            "items":
                followups,

            "passed":
                True,
        }

