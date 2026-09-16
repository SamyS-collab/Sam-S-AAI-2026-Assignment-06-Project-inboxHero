# Outbox Writer

"""
Responsibilities:
- Write draft artifacts to outbox/
- Persist draft replies
- Persist draft actions

Non-responsibilities:
- Send email
- Generate replies
- Collect approvals
- Evaluate action safety
- Call LLMs
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from core.audit_logger import AuditLogger


class OutboxWriter:
    """
    R3-safe output writer.

    InboxHero never sends email directly.

    All outbound actions are written to
    outbox/ as JSON files.
    """

    def __init__(
        self,
        outbox_dir: str = "outbox",
        logger: AuditLogger | None = None,
    ) -> None:

        project_root = Path(__file__).resolve().parent.parent

        self.outbox_dir = project_root / outbox_dir

        self.outbox_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.logger = logger or AuditLogger()

    # --------------------------------------------------
    # Generic Draft Writer
    # --------------------------------------------------

    def write_draft(
        self,
        message_id: str,
        content: str,
        source_message_ids: list[str] | None = None,
        draft_type: str = "reply",
    ) -> Path:
        """
        Write a draft artifact to outbox/.

        Returns:
            Path to generated file.
        """

        payload: dict[str, Any] = {
            "message_id": message_id,
            "draft_type": draft_type,
            "content": content,
            "source_message_ids": (
                source_message_ids or []
            ),
            "created_at": (
                datetime.utcnow().isoformat()
            ),
        }

        file_path = (
            self.outbox_dir
            / f"{message_id}_{draft_type}.json"
        )

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                payload,
                file,
                indent=4,
                ensure_ascii=False,
            )

        self.logger.log(
            "DRAFT_WRITTEN",
            message_id=message_id,
            draft_type=draft_type,
            file_path=str(file_path),
        )

        return file_path
