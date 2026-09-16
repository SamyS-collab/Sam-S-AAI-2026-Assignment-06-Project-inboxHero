# Retrieval Engine
"""
Responsibilities:
- Orchestrate retrieval operations
- Build grounded message context
- Provide source messages for downstream consumers

Non-responsibilities:
- Reply generation
- LLM calls
- Thread summarization
- Security analysis
- Classification
- Disposition decisions
"""

from __future__ import annotations

from core.message_model import Message
from retrieval.message_lookup import MessageLookup
from retrieval.thread_retriever import ThreadRetriever


class RetrievalEngine:
    """
    Central retrieval orchestration layer.

    Provides grounded context for future
    reply generation and thread reasoning.
    """

    def __init__(
        self,
        message_lookup: MessageLookup | None = None,
        thread_retriever: ThreadRetriever | None = None,
    ) -> None:

        self.message_lookup = (
            message_lookup or MessageLookup()
        )

        self.thread_retriever = (
            thread_retriever
            or ThreadRetriever(
                self.message_lookup
            )
        )

    # --------------------------------------------------
    # Message Context
    # --------------------------------------------------

    def get_message_context(
        self,
        message_id: str,
    ) -> dict[str, object] | None:
        """
        Return grounded context for a message.

        Returns:
            {
                "message": Message,
                "thread": list[Message]
            }

        Returns None if message not found.
        """

        message = (
            self.message_lookup.get_message(
                message_id
            )
        )

        if not message:
            return None

        thread = (
            self.thread_retriever
            .get_thread_by_message(
                message_id
            )
        )

        return {
            "message": message,
            "thread": thread,
        }

    # --------------------------------------------------
    # Source Messages
    # --------------------------------------------------

    def get_source_messages(
        self,
        message_id: str,
    ) -> list[Message]:
        """
        Return messages that can serve as
        grounding sources.

        Current implementation uses the
        complete thread as source context.
        """

        return (
            self.thread_retriever
            .get_thread_by_message(
                message_id
            )
        )

    # --------------------------------------------------
    # Existence Check
    # --------------------------------------------------

    def exists(
        self,
        message_id: str,
    ) -> bool:
        """
        True if message exists.
        """

        return self.message_lookup.exists(
            message_id
        )

    # --------------------------------------------------
    # Message Retrieval
    # --------------------------------------------------

    def get_message(
        self,
        message_id: str,
    ) -> Message | None:
        """
        Convenience wrapper around
        MessageLookup.
        """

        return (
            self.message_lookup.get_message(
                message_id
            )
        )


