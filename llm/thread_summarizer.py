# Thread Summarizer

"""
Responsibilities:
- Retrieve a complete message thread
- Build a grounded thread-summary prompt
- Generate a structured thread summary
- Validate generated summary content
- Block unsafe generated summaries
- Preserve source message IDs

Non-responsibilities:
- Reply generation
- Outbox writing
- Dashboard rendering
- Disposition assignment
- Hostile inbox detection
- Message modification
"""

from dataclasses import dataclass

from llm.llm_service import LLMService
from llm.prompt_templates import PromptTemplates
from retrieval.thread_retriever import ThreadRetriever
from security.policy_validator import PolicyValidator


@dataclass(frozen=True)
class ThreadSummary:
    """
    Canonical thread summary.

    source_message_ids contains every inbox
    message supplied to the LLM.

    policy_allowed indicates whether the
    original LLM summary passed output policy.
    """

    thread_id: str
    summary: str
    source_message_ids: list
    policy_allowed: bool
    policy_reason: str

    def to_dict(self):
        """
        Return a JSON-serializable representation.
        """

        return {
            "thread_id": self.thread_id,
            "summary": self.summary,
            "source_message_ids": list(
                self.source_message_ids
            ),
            "policy_allowed": self.policy_allowed,
            "policy_reason": self.policy_reason,
        }


class ThreadSummarizer:
    """
    LLM #3 implementation for InboxHero.

    Allowed uses:
    - Long thread summaries
    - Open questions
    - Multi-message reasoning

    Generated summaries are validated before
    they are returned to downstream components.
    """

    SAFE_BLOCKED_SUMMARY = (
        "Summary:\n"
        "The thread contains sensitive authentication "
        "or connection information that cannot be "
        "included in the generated summary.\n\n"
        "Open Questions:\n"
        "- Confirm an approved secure method for "
        "handling the sensitive information.\n\n"
        "Action Items:\n"
        "- Do not copy credentials or connection "
        "secrets into email, dashboard, or outbox "
        "artifacts.\n"
        "- Use an approved secure channel if the "
        "information must be shared."
    )

    def __init__(
        self,
        thread_retriever=None,
        llm_service=None,
        policy_validator=None,
    ):
        """
        Initialize the thread summarizer.

        Dependencies may be injected for testing.
        """

        self.thread_retriever = (
            thread_retriever
            or ThreadRetriever()
        )

        self.llm_service = (
            llm_service
            or LLMService()
        )

        self.policy_validator = (
            policy_validator
            or PolicyValidator()
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def summarize_thread(
        self,
        message_id,
    ):
        """
        Summarize the thread containing message_id.

        The complete thread is retrieved through
        ThreadRetriever and supplied to the LLM.

        Generated content is validated before being
        returned as a ThreadSummary.
        """

        self._validate_message_id(
            message_id
        )

        thread_messages = (
            self.thread_retriever
            .get_thread_by_message(
                message_id
            )
        )

        if not thread_messages:
            raise ValueError(
                "Cannot summarize thread because "
                f"no thread was found for {message_id!r}."
            )

        thread_id = self._get_thread_id(
            thread_messages
        )

        source_message_ids = (
            self._get_source_message_ids(
                thread_messages
            )
        )

        prompt = (
            PromptTemplates
            .build_thread_summary_prompt(
                thread_messages
            )
        )

        generated_summary = (
            self._generate_summary(
                prompt
            )
        )

        validation = (
            self.policy_validator.validate(
                generated_summary
            )
        )

        if validation.allowed:
            return ThreadSummary(
                thread_id=thread_id,
                summary=generated_summary,
                source_message_ids=(
                    source_message_ids
                ),
                policy_allowed=True,
                policy_reason=validation.reason,
            )

        return ThreadSummary(
            thread_id=thread_id,
            summary=self.SAFE_BLOCKED_SUMMARY,
            source_message_ids=(
                source_message_ids
            ),
            policy_allowed=False,
            policy_reason=validation.reason,
        )

    # --------------------------------------------------
    # Validation Helpers
    # --------------------------------------------------

    @staticmethod
    def _validate_message_id(
        message_id,
    ):
        """
        Require a non-empty message ID.
        """

        if (
            not isinstance(message_id, str)
            or not message_id.strip()
        ):
            raise ValueError(
                "message_id must be a "
                "non-empty string."
            )

    @staticmethod
    def _get_thread_id(
        thread_messages,
    ):
        """
        Read and validate the thread ID.
        """

        thread_id = (
            thread_messages[0]
            .metadata.get(
                "thread_id"
            )
        )

        if (
            not isinstance(thread_id, str)
            or not thread_id.strip()
        ):
            raise ValueError(
                "Retrieved thread does not "
                "contain a valid thread_id."
            )

        return thread_id

    @staticmethod
    def _get_source_message_ids(
        thread_messages,
    ):
        """
        Return ordered, deduplicated source IDs.
        """

        source_message_ids = list(
            dict.fromkeys(
                message.message_id
                for message in thread_messages
            )
        )

        if not source_message_ids:
            raise ValueError(
                "Thread summary requires at least "
                "one source message ID."
            )

        return source_message_ids

    # --------------------------------------------------
    # LLM Helper
    # --------------------------------------------------

    def _generate_summary(
        self,
        prompt,
    ):
        """
        Execute the summary prompt and require
        non-empty generated content.
        """

        summary = self.llm_service.generate(
            prompt
        )

        if (
            not isinstance(summary, str)
            or not summary.strip()
        ):
            raise ValueError(
                "The LLM returned an empty "
                "thread summary."
            )

        return summary.strip()
