# Message Lookup

"""
Responsibilities:
- Retrieve messages by message_id
- Retrieve multiple messages
- Check message existence
- Provide access to all messages

Non-responsibilities:
- Thread reconstruction
- Retrieval reasoning
- Reply generation
- Security analysis
- Classification
"""

from __future__ import annotations

from core.inbox_loader import InboxLoader
from core.message_model import Message


class MessageLookup:
    """
    Deterministic message lookup service.

    Loads messages once and builds an in-memory
    index for fast retrieval.
    """

    def __init__(
        self,
        loader: InboxLoader | None = None,
    ) -> None:

        self.loader = loader or InboxLoader()

        self.messages = self.loader.load()

        self.message_index: dict[str, Message] = {
            message.message_id: message
            for message in self.messages
        }

    # --------------------------------------------------
    # Single Message Retrieval
    # --------------------------------------------------

    def get_message(
        self,
        message_id: str,
    ) -> Message | None:
        """
        Return a message by ID.

        Returns:
            Message | None
        """

        return self.message_index.get(message_id)

    # --------------------------------------------------
    # Multiple Message Retrieval
    # --------------------------------------------------

    def get_messages(
        self,
        message_ids: list[str],
    ) -> list[Message]:
        """
        Retrieve multiple messages.

        Missing message IDs are ignored.
        """

        return [
            self.message_index[msg_id]
            for msg_id in message_ids
            if msg_id in self.message_index
        ]

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

        return message_id in self.message_index

    # --------------------------------------------------
    # All Messages
    # --------------------------------------------------

    def all_messages(
        self,
    ) -> list[Message]:
        """
        Return all loaded messages.
        """

        return list(self.messages)

    # --------------------------------------------------
    # Count
    # --------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Total number of loaded messages.
        """

        return len(self.messages)