# HTML Renderer

"""
Responsibilities:
- Render dashboard HTML
- Render exactly three dashboard panes
- Save rendered dashboard to file

Non-responsibilities:
- Dashboard data generation
- Security analysis
- Commitment extraction
- Conflict detection
- LLM interactions
"""

from __future__ import annotations

from pathlib import Path

from dashboard.dashboard_builder import Dashboard


class HtmlRenderer:
    """
    Renders InboxHero dashboard HTML.

    Produces exactly three panes:

    1. Pending Actions
    2. Flagged Items
    3. Commitments
    """

    def render(
        self,
        dashboard: Dashboard,
    ) -> str:
        """
        Render dashboard to HTML string.
        """

        data = dashboard.to_dict()

        pending_actions_html = self._render_pending_actions(
            data["pending_actions"]
        )

        flagged_items_html = self._render_flagged_items(
            data["flagged_items"]
        )

        commitments_html = self._render_commitments(
            data["commitments"]
        )

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>InboxHero Dashboard</title>
</head>
<body>

    <h1>InboxHero Dashboard</h1>

    <h2>Pending Actions</h2>
    {pending_actions_html}

    <h2>Flagged Items</h2>
    {flagged_items_html}

    <h2>Commitments</h2>
    {commitments_html}

</body>
</html>
""".strip()

    def save(
        self,
        dashboard: Dashboard,
        output_path: str = "dashboard/dashboard.html",
    ) -> Path:
        """
        Render and save dashboard HTML.
        """

        html = self.render(dashboard)

        project_root = Path(__file__).resolve().parent.parent

        output_file = project_root / output_path

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file.write_text(
            html,
            encoding="utf-8",
        )

        return output_file

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _render_pending_actions(
        self,
        pending_actions: list[dict],
    ) -> str:

        if not pending_actions:
            return "<p>No pending actions.</p>"

        items = "\n".join(
            (
                f"<li>"
                f"{item.get('message_id')} - "
                f"{item.get('action')}"
                f"</li>"
            )
            for item in pending_actions
        )

        return f"<ul>{items}</ul>"

    def _render_flagged_items(
        self,
        flagged_items: list[dict],
    ) -> str:

        if not flagged_items:
            return "<p>No flagged items.</p>"

        items = "\n".join(
            (
                f"<li>"
                f"{item.get('message_id')} - "
                f"{item.get('threat_type')}"
                f"</li>"
            )
            for item in flagged_items
        )

        return f"<ul>{items}</ul>"

    def _render_commitments(
        self,
        commitments: dict,
    ) -> str:

        commitment_items = commitments.get(
            "items",
            [],
        )

        conflict_items = commitments.get(
            "conflicts",
            [],
        )

        parts: list[str] = []

        if commitment_items:

            items_html = "\n".join(
                (
                    f"<li>"
                    f"{item['message_id']} - "
                    f"{item['title']} - "
                    f"{item['event_time']}"
                    f"</li>"
                )
                for item in commitment_items
            )

            parts.append(
                f"<h3>Commitments</h3>"
                f"<ul>{items_html}</ul>"
            )

        else:

            parts.append(
                "<p>No commitments.</p>"
            )

        if conflict_items:

            conflict_html = "\n".join(
                (
                    f"<li>"
                    f"{item['commitment_a']['message_id']} "
                    f"vs "
                    f"{item['commitment_b']['message_id']} "
                    f"({item['conflict_time']})"
                    f"</li>"
                )
                for item in conflict_items
            )

            parts.append(
                f"<h3>Conflicts</h3>"
                f"<ul>{conflict_html}</ul>"
            )

        return "\n".join(parts)

