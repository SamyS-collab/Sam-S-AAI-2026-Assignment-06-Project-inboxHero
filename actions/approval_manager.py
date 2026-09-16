# Approval Manager

"""
Responsibilities:
- Record approval decisions
- Record rejection decisions
- Persist approval history
- Retrieve approval status
- Audit approval activity

Non-responsibilities:
- Evaluate action safety
- Write files to outbox
- Generate replies
- Send email
- Call LLMs
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from actions.gatekeeper import GateDecision
from core.audit_logger import AuditLogger


class ApprovalManager:
    """
    Manages human approval decisions for R3.
    """

    DEFAULT_DATA = {
        "approvals": []
    }

    def __init__(
        self,
        approval_log_path: str = "logs/approval_log.json",
        logger: AuditLogger | None = None,
    ) -> None:

        project_root = Path(__file__).resolve().parent.parent

        self.approval_log_path = (
            project_root / approval_log_path
        )

        self.approval_log_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.logger = logger or AuditLogger()

        self._initialize_file()

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------

    def _initialize_file(self) -> None:
        """
        Ensure approval_log.json exists and
        contains a valid structure.
        """

        if not self.approval_log_path.exists():
            self._save(self.DEFAULT_DATA)
            return

        try:
            data = self._load()

            if "approvals" not in data:
                self._save(self.DEFAULT_DATA)

        except (
            json.JSONDecodeError,
            ValueError,
        ):
            self._save(self.DEFAULT_DATA)

    # --------------------------------------------------
    # Private Helpers
    # --------------------------------------------------

    def _load(self) -> dict:
        with open(
            self.approval_log_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def _save(
        self,
        data: dict,
    ) -> None:
        with open(
            self.approval_log_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    # --------------------------------------------------
    # Approval Operations
    # --------------------------------------------------

    def approve(
        self,
        decision: GateDecision,
        approved_by: str = "user",
    ) -> None:
        """
        Record approval.
        """

        self._record(
            decision=decision,
            approved=True,
            approved_by=approved_by,
        )

    def reject(
        self,
        decision: GateDecision,
        approved_by: str = "user",
    ) -> None:
        """
        Record rejection.
        """

        self._record(
            decision=decision,
            approved=False,
            approved_by=approved_by,
        )

    def _record(
        self,
        decision: GateDecision,
        approved: bool,
        approved_by: str,
    ) -> None:

        if not isinstance(
            decision,
            GateDecision,
        ):
            raise TypeError(
                "ApprovalManager expects "
                "a GateDecision"
            )

        data = self._load()

        record = {
            "message_id": decision.message_id,
            "disposition": (
                decision.disposition.value
            ),
            "approved": approved,
            "approved_by": approved_by,
            "timestamp": (
                datetime.utcnow().isoformat()
            ),
        }

        data["approvals"].append(record)

        self._save(data)

        self.logger.log(
            "APPROVAL_RECORDED",
            message_id=decision.message_id,
            disposition=decision.disposition.value,
            approved=approved,
            approved_by=approved_by,
        )

    # --------------------------------------------------
    # Lookup
    # --------------------------------------------------

    def get_approval(
        self,
        message_id: str,
    ) -> dict | None:
        """
        Return latest approval record
        for a message.
        """

        data = self._load()

        matches = [
            record
            for record in data["approvals"]
            if record["message_id"] == message_id
        ]

        if not matches:
            return None

        return matches[-1]

    def get_all_approvals(
        self,
    ) -> list[dict]:
        """
        Return all approval records.
        """

        data = self._load()

        return data["approvals"]

