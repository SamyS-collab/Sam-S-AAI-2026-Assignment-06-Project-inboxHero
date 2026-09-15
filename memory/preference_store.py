# Prference Store

"""
Responsibilities:
- Persist preferences to disk
- Load preferences from disk
- Manage preferences.json file lifecycle

Non-responsibilities:
- Preference extraction
- Preference validation
- Preference application
- Audit logging
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PreferenceStore:
    """
    Thin persistence layer for preference storage.

    Preferences are stored in:

        data/preferences.json
    """

    DEFAULT_DATA = {
        "preferences": []
    }

    def __init__(
        self,
        file_path: str = "data/preferences.json",
    ) -> None:
        project_root = Path(__file__).resolve().parent.parent

        self.file_path = project_root / file_path

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def load(self) -> dict[str, Any]:
        """
        Load preferences from disk.

        Returns:
            dict containing preferences data
        """

        if not self.file_path.exists():
            self.save(self.DEFAULT_DATA)

        with open(
            self.file_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def save(
        self,
        data: dict[str, Any],
    ) -> None:
        """
        Persist preferences to disk.
        """

        with open(
            self.file_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )
