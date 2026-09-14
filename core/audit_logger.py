# InboxHero Audit Logger

"""
Responsibilities:
- Append structured audit events to trace.jsonl
- Provide a single logging interface for all modules
- Preserve an audit trail for debugging and evaluation

Non-responsibilities:
- Business logic
- Message classification
- Security decisions

"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class AuditLogger:
    """
    Writes structured audit events to logs/trace.jsonl
    """

    def __init__(
        self,
        log_path: str = "logs/trace.jsonl",
    ) -> None:

        project_root = Path(__file__).resolve().parent.parent

        self.log_path = project_root / log_path

        self.log_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(
        self,
        event: str,
        **details: Any,
    ) -> None:
        """
        Write one structured event.

        Example:

        logger.log(
            "MESSAGE_LOADED",
            message_id="m001"
        )
        """

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **details,
        }

        with open(
            self.log_path,
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(record)
                + "\n"
            )
