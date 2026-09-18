# Grounded Reply Generator

"""
Responsibilities:
- Retrieve grounded inbox context
- Build the appropriate reply prompt
- Generate draft text through LLMService
- Validate generated content with PolicyValidator
- Block sensitive generated output
- Track all source message IDs used
- Return a structured ReplyDraft

Non-responsibilities:
- Sending email
- Writing files to outbox
- Approving actions
- Assigning dispositions
- Detecting hostile inbox messages
- Summarizing threads
"""

from __future__ import annotations

from dataclasses import dataclass

from llm.llm_service import LLMService
from llm.prompt_templates import PromptTemplates
from retrieval.retrieval_engine import RetrievalEngine
from security.policy_validator import PolicyValidator


@dataclass(frozen=True, slots=True)
class ReplyDraft:
    """
    Canonical grounded reply draft.

    source_message_ids records every inbox
    message supplied to the LLM as grounding.

    policy_allowed indicates whether the original
    generated content passed output validation.
    """

    message_id: str
    draft_type: str
    content: str
    source_message_ids: list[str]
    policy_allowed: bool
    policy_reason: str

    def to_dict(self):
        """
        Return a JSON-serializable representation.
        """

        return {
            "message_id": self.message_id,
            "draft_type": self.draft_type,
            "content": self.content,
            "source_message_ids": list(
                self.source_message_ids
            ),
            "policy_allowed": self.policy_allowed,
            "policy_reason": self.policy_reason,
        }


class ReplyGenerator:
    """
    LLM #2 implementation for InboxHero.

    Allowed uses:
    - Grounded replies
    - Clarification requests
    - Meeting responses

    Generated content is validated before it
    becomes a ReplyDraft.
    """

    DRAFT_TYPE_REPLY = "reply"
    DRAFT_TYPE_CLARIFICATION = "clarification"
    DRAFT_TYPE_MEETING_RESPONSE = "meeting_response"

    SAFE_BLOCKED_CONTENT = (
        "I found sensitive authentication or connection "
        "information in the earlier messages, but I cannot "
        "include that information in a reply draft. Please "
        "confirm an approved secure method for sharing it."
    )

    def __init__(
        self,
        retrieval_engine=None,
        llm_service=None,
        policy_validator=None,
    ):
        """
        Initialize the grounded reply generator.
        """

        self.retrieval_engine = (
            retrieval_engine
            or RetrievalEngine()
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
    # Grounded Reply
    # --------------------------------------------------

    def generate_reply(
        self,
        message_id,
    ):
        """
        Generate a grounded reply using the complete
        retrieved thread as source context.

        Unsafe generated content is replaced with a
        safe clarification draft.
        """

        current_message = self._get_message(
            message_id
        )

        source_messages = self._get_sources(
            message_id
        )

        prompt = PromptTemplates.build_reply_prompt(
            current_message=current_message,
            source_messages=source_messages,
        )

        generated_content = self._generate_content(
            prompt
        )

        return self._build_validated_draft(
            message_id=message_id,
            requested_draft_type=(
                self.DRAFT_TYPE_REPLY
            ),
            generated_content=generated_content,
            source_messages=source_messages,
        )

    # --------------------------------------------------
    # Clarification Request
    # --------------------------------------------------

    def generate_clarification(
        self,
        message_id,
    ):
        """
        Generate a deterministic clarification request.

        This prevents the model from inventing
        missing context for ambiguous messages.
        """

        current_message = self._get_message(
            message_id
        )

        subject = (
            current_message.subject.strip()
            or "your message"
        )

        content = (
            f"Subject: Re: {subject}\n\n"
            "Hi,\n\n"
            "Could you please clarify what you are "
            "referring to and what action you need "
            "from me?\n\n"
            "Thank you."
        )

        validation = (
            self.policy_validator.validate(
                content
            )
        )

        if not validation.allowed:
            raise ValueError(
                "Deterministic clarification failed "
                f"policy validation: {validation.reason}"
            )
        return ReplyDraft(
                message_id=message_id,
                draft_type=(
                    self.DRAFT_TYPE_CLARIFICATION
                ),
                content=content,
                source_message_ids=[
                    current_message.message_id
                ],
                policy_allowed=True,
                policy_reason=validation.reason,
            )
    
    # --------------------------------------------------
    # Meeting Response
    # --------------------------------------------------

    def generate_meeting_response(
        self,
        message_id,
    ):
        """
        Generate a grounded meeting response using
        the retrieved thread as source context.

        The prompt forbids invented dates, times,
        and commitments.
        """

        current_message = self._get_message(
            message_id
        )

        source_messages = self._get_sources(
            message_id
        )

        prompt = (
            PromptTemplates
            .build_meeting_response_prompt(
                current_message=current_message,
                source_messages=source_messages,
            )
        )

        generated_content = self._generate_content(
            prompt
        )

        return self._build_validated_draft(
            message_id=message_id,
            requested_draft_type=(
                self.DRAFT_TYPE_MEETING_RESPONSE
            ),
            generated_content=generated_content,
            source_messages=source_messages,
        )

    # --------------------------------------------------
    # Retrieval Helpers
    # --------------------------------------------------

    def _get_message(
        self,
        message_id,
    ):
        """
        Retrieve and validate the target message.
        """

        if (
            not isinstance(message_id, str)
            or not message_id.strip()
        ):
            raise ValueError(
                "message_id must be a "
                "non-empty string."
            )

        message = (
            self.retrieval_engine.get_message(
                message_id
            )
        )

        if message is None:
            raise ValueError(
                "Cannot generate a reply because "
                f"message {message_id!r} was not found."
            )

        return message

    def _get_sources(
        self,
        message_id,
    ):
        """
        Retrieve and validate grounding sources.
        """

        source_messages = (
            self.retrieval_engine
            .get_source_messages(
                message_id
            )
        )

        if not source_messages:
            raise ValueError(
                "Cannot generate a grounded reply "
                f"for {message_id!r} because no "
                "source messages were retrieved."
            )

        return source_messages

    # --------------------------------------------------
    # LLM Helper
    # --------------------------------------------------

    def _generate_content(
        self,
        prompt,
    ):
        """
        Execute a prompt and require non-empty text.
        """

        content = self.llm_service.generate(
            prompt
        )

        if (
            not isinstance(content, str)
            or not content.strip()
        ):
            raise ValueError(
                "The LLM returned an empty reply."
            )

        return content.strip()

    # --------------------------------------------------
    # Policy Validation
    # --------------------------------------------------

    def _build_validated_draft(
        self,
        message_id,
        requested_draft_type,
        generated_content,
        source_messages,
    ):
        """
        Validate generated content and return a safe
        ReplyDraft.

        If sensitive output is detected:
        - the unsafe content is discarded
        - a deterministic safe clarification is returned
        - the source message IDs are preserved
        - the original policy failure is recorded
        """

        validation = (
            self.policy_validator.validate(
                generated_content
            )
        )

        source_message_ids = (
            self._source_message_ids(
                source_messages
            )
        )

        if validation.allowed:
            return ReplyDraft(
                message_id=message_id,
                draft_type=requested_draft_type,
                content=generated_content,
                source_message_ids=(
                    source_message_ids
                ),
                policy_allowed=True,
                policy_reason=validation.reason,
            )

        return ReplyDraft(
            message_id=message_id,
            draft_type=(
                self.DRAFT_TYPE_CLARIFICATION
            ),
            content=self.SAFE_BLOCKED_CONTENT,
            source_message_ids=(
                source_message_ids
            ),
            policy_allowed=False,
            policy_reason=validation.reason,
        )

    @staticmethod
    def _source_message_ids(
        source_messages,
    ):
        """
        Return ordered, deduplicated source IDs.
        """

        source_message_ids = list(
            dict.fromkeys(
                message.message_id
                for message in source_messages
            )
        )

        if not source_message_ids:
            raise ValueError(
                "A grounded reply must contain "
                "at least one source message ID."
            )

        return source_message_ids
