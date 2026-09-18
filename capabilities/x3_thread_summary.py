# X3 - Thread Summary Capability

"""
Responsibilities:
- Summarize message threads
- Expose summary provenance
- Expose policy validation results
- Produce an inspectable capability report

Non-responsibilities:
- Retrieving messages directly
- Building prompts
- Calling Gemini directly
- Policy validation
- Dashboard rendering
"""

from __future__ import annotations

from llm.thread_summarizer import (
    ThreadSummarizer,
)


class X3ThreadSummary:
    """
    Capability wrapper for X3.

    Uses the frozen ThreadSummarizer
    implementation and returns a
    grader-friendly report.
    """

    def __init__(
        self,
        thread_summarizer=None,
    ):

        self.thread_summarizer = (
            thread_summarizer
            or ThreadSummarizer()
        )

    def summarize(
        self,
        message_id,
    ):
        """
        Summarize the thread containing
        the supplied message.
        """

        summary = (
            self.thread_summarizer
            .summarize_thread(
                message_id
            )
        )

        return {
            "thread_id":
                summary.thread_id,

            "source_message_ids":
                list(
                    summary.source_message_ids
                ),

            "policy_allowed":
                summary.policy_allowed,

            "policy_reason":
                summary.policy_reason,

            "summary":
                summary.summary,

            "passed":
                True,
        }
