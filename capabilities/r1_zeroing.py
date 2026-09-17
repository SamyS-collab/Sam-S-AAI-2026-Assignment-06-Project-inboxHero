# R1 - Zeroing It

"""
Responsibilities:
- Verify every message has exactly one disposition
- Verify every message has a disposition reason
- Report disposition breakdown
- Report processing source breakdown
- Produce a pass/fail R1 report

Non-responsibilities:
- Classification
- Routing
- Disposition assignment
- Security analysis
- LLM interactions
"""

from __future__ import annotations

from collections import Counter

from core.dispositions import Disposition
from core.message_model import Message


class R1Zeroing:
    """
    Part 2 capability wrapper.

    Validates that InboxHero satisfies
    the Zeroing It requirement.
    """

    def validate(
        self,
        messages: list[Message],
    ) -> dict[str, object]:

        total_messages = len(messages)

        disposition_count = 0
        missing_dispositions = 0
        missing_reasons = 0

        disposition_breakdown: Counter[str] = Counter()
        processing_sources: Counter[str] = Counter()

        valid_dispositions = set(
            Disposition.values()
        )

        for message in messages:

            disposition = message.metadata.get(
                "disposition"
            )

            reason = message.metadata.get(
                "disposition_reason"
            )

            handled_by = message.metadata.get(
                "handled_by"
            )

            if disposition:

                disposition_count += 1

                if disposition in valid_dispositions:
                    disposition_breakdown[
                        disposition
                    ] += 1

            else:

                missing_dispositions += 1

            if (
                not isinstance(reason, str)
                or not reason.strip()
            ):
                missing_reasons += 1

            if (
                isinstance(handled_by, str)
                and handled_by.strip()
            ):
                processing_sources[
                    handled_by
                ] += 1

        return {
            "messages_processed":
                total_messages,

            "decisions_produced":
                disposition_count,

            "missing_dispositions":
                missing_dispositions,

            "missing_reasons":
                missing_reasons,

            "disposition_breakdown":
                dict(disposition_breakdown),

            "processing_sources":
                dict(processing_sources),

            "passed": (
                missing_dispositions == 0
                and
                missing_reasons == 0
                and
                disposition_count
                == total_messages
            ),
        }

