# Inbox Loader - Load and Validate Inbox Messages

"""
Responsibilities:
- Read inbox.json
- Validate message structure
- Convert JSON records into Message objects
"""

import json
from datetime import datetime
from pathlib import Path

from core.message_model import Message


class InboxLoader:
    REQUIRED_FIELDS = {
        "id",
        "thread_id",
        "from",
        "to",
        "subject",
        "timestamp",
        "body",
        "unread",
    }

    def __init__(self, inbox_path: str = "inbox/inbox.json"):
        project_root = Path(__file__).resolve().parent.parent
        self.inbox_path = project_root / inbox_path

    
    def load(self) -> list[Message]:
        """
        Load .json.

        Returns:
            list[Message]
        """
        if not self.inbox_path.exists():
            raise FileNotFoundError(
                f"Inbox file not found: {self.inbox_path}"
            )

        with open(self.inbox_path, "r", encoding="utf-8") as file:
            raw_messages = json.load(file)

        messages = []

        for raw_message in raw_messages:
            self._validate(raw_message)

            message = Message.from_dict(raw_message)

            messages.append(message)

        return messages

    def _validate(self, message: dict) -> None:
        """
        Validate required fields exist.
        """
        missing = self.REQUIRED_FIELDS - message.keys()

        if missing:
            raise ValueError(
                f"Message {message.get('id')} "
                f"is missing fields: {sorted(missing)}"
            )
