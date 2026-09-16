# Thread Retriever
"""
Responsibilities:
- Retrieve all messages belonging to a thread
- Retrieve thread by thread_id
- Retrieve thread from a message_id
- Return messages in chronological order

Non-responsibilities:
- Thread summarization
- Reply generation
- Security analysis
- Grounding decisions
- LLM interactions
"""

from __future__ import annotations

from core.message_model import Message
from retrieval.message_lookup import MessageLookup


class ThreadRetriever:
    """
    Deterministic thread retrieval service.

    Builds an in-memory thread index from messages
    loaded through MessageLookup.
    """

    def __init__(
        self,
        message_lookup: MessageLookup | None = None,
    ) -> None:

        self.message_lookup = (
            message_lookup or MessageLookup()
        )

        self.thread_index: dict[str, list[Message]] = {}

        for message in self.message_lookup.all_messages():

            thread_id = message.metadata.get(
                "thread_id"
            )

            if not thread_id:
                continue

            self.thread_index.setdefault(
                thread_id,
                []
            ).append(message)

        for messages in self.thread_index.values():
            messages.sort(
                key=lambda msg: msg.timestamp or ""
            )

    # --------------------------------------------------
    # Thread By Thread ID
    # --------------------------------------------------

    def get_thread(
        self,
        thread_id: str,
    ) -> list[Message]:
        """
        Return all messages in a thread.

        Returns empty list if not found.
        """

        return list(
            self.thread_index.get(
                thread_id,
                []
            )
        )

    # --------------------------------------------------
    # Thread By Message ID
    # --------------------------------------------------

    def get_thread_by_message(
        self,
        message_id: str,
    ) -> list[Message]:
        """
        Retrieve thread using a message ID.
        """

        message = self.message_lookup.get_message(
            message_id
        )

        if not message:
            return []

        thread_id = message.metadata.get(
            "thread_id"
        )

        if not thread_id:
            return []

        return self.get_thread(thread_id)

    # --------------------------------------------------
    # Thread ID Lookup
    # --------------------------------------------------

    def get_thread_id(
        self,
        message_id: str,
    ) -> str | None:
        """
        Return thread_id for a message.
        """

        message = self.message_lookup.get_message(
            message_id
        )

        if not message:
            return None

        return message.metadata.get(
            "thread_id"
        )

    # --------------------------------------------------
    # Thread Exists
    # --------------------------------------------------

    def thread_exists(
        self,
        thread_id: str,
    ) -> bool:
        """
        True if thread exists.
        """

        return thread_id in self.thread_index

    # --------------------------------------------------
    # Thread Count
    # --------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Total threads loaded.
        """

        return len(self.thread_index)
