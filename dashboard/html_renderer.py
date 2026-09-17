# HTML Renderer

"""
Responsibilities:
- Render the Dashboard model as static HTML
- Render exactly three dashboard panes
- Show all rubric-required row details
- Save rendered HTML to a reproducible file
- Escape inbox-derived content before inserting it into HTML

Non-responsibilities:
- Build dashboard data
- Analyze messages
- Detect security threats
- Extract commitments
- Detect conflicts
- Call LLMs
"""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from dashboard.dashboard_builder import Dashboard


class HtmlRenderer:
    """
    Render an InboxHero Dashboard as static HTML.

    Part 7 requires exactly three panes:

    1. Pending Actions
    2. Flagged
    3. Commitments
    """

    def render(
        self,
        dashboard: Dashboard,
    ) -> str:
        """
        Render the dashboard as a complete HTML document.
        """

        if not isinstance(dashboard, Dashboard):
            raise TypeError(
                "HtmlRenderer.render() expects a Dashboard"
            )

        data = dashboard.to_dict()

        pending_actions_html = (
            self._render_pending_actions(
                data.get("pending_actions", [])
            )
        )

        flagged_items_html = (
            self._render_flagged_items(
                data.get("flagged_items", [])
            )
        )

        commitments_html = (
            self._render_commitments(
                data.get("commitments", {})
            )
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >
    <title>InboxHero Dashboard</title>

    <style>
        body {{
            margin: 0;
            padding: 24px;
            background: #f4f6f8;
            color: #1f2933;
            font-family: Arial, Helvetica, sans-serif;
        }}

        h1 {{
            margin-top: 0;
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: repeat(
                3,
                minmax(0, 1fr)
            );
            gap: 18px;
            align-items: start;
        }}

        .pane {{
            background: #ffffff;
            border: 1px solid #d8dee4;
            border-radius: 8px;
            padding: 16px;
        }}

        .pane h2 {{
            margin-top: 0;
            border-bottom: 2px solid #d8dee4;
            padding-bottom: 8px;
        }}

        .item {{
            margin-bottom: 12px;
            padding: 12px;
            border: 1px solid #e5e9ed;
            border-radius: 6px;
            background: #fafbfc;
        }}

        .item:last-child {{
            margin-bottom: 0;
        }}

        .field {{
            margin: 5px 0;
            overflow-wrap: anywhere;
        }}

        .label {{
            font-weight: bold;
        }}

        .pending {{
            border-left: 5px solid #b7791f;
        }}

        .flagged {{
            border-left: 5px solid #b42318;
        }}

        .commitment {{
            border-left: 5px solid #2563eb;
        }}

        .conflict {{
            border: 2px solid #b42318;
            background: #fff1f0;
        }}

        .conflict-heading {{
            margin-top: 20px;
            color: #b42318;
        }}

        .empty {{
            color: #52606d;
            font-style: italic;
        }}

        @media (max-width: 900px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>

<body>
    <h1>InboxHero Dashboard</h1>

    <main class="dashboard">
        <section
            id="pending-actions"
            class="pane"
        >
            <h2>Pending Actions</h2>
            {pending_actions_html}
        </section>

        <section
            id="flagged-items"
            class="pane"
        >
            <h2>Flagged</h2>
            {flagged_items_html}
        </section>

        <section
            id="commitments"
            class="pane"
        >
            <h2>Commitments</h2>
            {commitments_html}
        </section>
    </main>
</body>
</html>"""

    def save(
        self,
        dashboard: Dashboard,
        output_path: str = "dashboard/dashboard.html",
    ) -> Path:
        """
        Render and save the dashboard as a static HTML file.

        Args:
            dashboard:
                Dashboard model produced by DashboardBuilder.

            output_path:
                Path relative to the project root.

        Returns:
            Path to the generated HTML file.
        """

        html_output = self.render(dashboard)

        project_root = (
            Path(__file__).resolve().parent.parent
        )

        output_file = project_root / output_path

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file.write_text(
            html_output,
            encoding="utf-8",
        )

        return output_file

    # --------------------------------------------------
    # Pending Actions Pane
    # --------------------------------------------------

    def _render_pending_actions(
        self,
        pending_actions: list[dict[str, Any]],
    ) -> str:
        """
        Render actions requiring human involvement.

        Every row shows:
        - Message ID
        - Proposed action
        - Why human involvement is required
        """

        if not pending_actions:
            return (
                '<p class="empty">'
                "No pending actions."
                "</p>"
            )

        rendered_items: list[str] = []

        for item in pending_actions:
            message_id = self._safe_value(
                item.get("message_id")
            )

            action = self._safe_value(
                item.get("action")
            )

            human_reason = self._safe_value(
                item.get("human_reason")
            )

            rendered_items.append(
                f"""
<div class="item pending">
    <div class="field">
        <span class="label">Message:</span>
        {message_id}
    </div>

    <div class="field">
        <span class="label">Proposed action:</span>
        {action}
    </div>

    <div class="field">
        <span class="label">Why human review is needed:</span>
        {human_reason}
    </div>
</div>""".strip()
            )

        return "\n".join(rendered_items)

    # --------------------------------------------------
    # Flagged Pane
    # --------------------------------------------------

    def _render_flagged_items(
        self,
        flagged_items: list[dict[str, Any]],
    ) -> str:
        """
        Render messages on which the system refused to act.

        Every row shows:
        - Message ID
        - Threat or refusal type
        - What was attempted
        - What the system did instead
        """

        if not flagged_items:
            return (
                '<p class="empty">'
                "No flagged items."
                "</p>"
            )

        rendered_items: list[str] = []

        for item in flagged_items:
            message_id = self._safe_value(
                item.get("message_id")
            )

            threat_type = self._safe_value(
                item.get("threat_type")
            )

            attempted_action = self._safe_value(
                item.get("attempted_action")
            )

            system_response = self._safe_value(
                item.get("system_response")
            )

            rendered_items.append(
                f"""
<div class="item flagged">
    <div class="field">
        <span class="label">Message:</span>
        {message_id}
    </div>

    <div class="field">
        <span class="label">Flag type:</span>
        {threat_type}
    </div>

    <div class="field">
        <span class="label">Attempted:</span>
        {attempted_action}
    </div>

    <div class="field">
        <span class="label">System response:</span>
        {system_response}
    </div>
</div>""".strip()
            )

        return "\n".join(rendered_items)

    # --------------------------------------------------
    # Commitments Pane
    # --------------------------------------------------

    def _render_commitments(
        self,
        commitments: dict[str, Any],
    ) -> str:
        """
        Render commitments and scheduling conflicts.

        Conflicts are rendered inside the Commitments pane,
        so the dashboard still has exactly three panes.
        """

        if not isinstance(commitments, dict):
            raise TypeError(
                "commitments pane data must be a dictionary"
            )

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
            sorted_commitments = sorted(
                commitment_items,
                key=lambda item: str(
                    item.get("event_time", "")
                ),
            )

            for item in sorted_commitments:
                parts.append(
                    self._render_commitment_item(
                        item
                    )
                )
        else:
            parts.append(
                '<p class="empty">'
                "No commitments."
                "</p>"
            )

        if conflict_items:
            parts.append(
                '<h3 class="conflict-heading">'
                "Scheduling Conflicts"
                "</h3>"
            )

            for conflict in conflict_items:
                parts.append(
                    self._render_conflict_item(
                        conflict
                    )
                )
        else:
            parts.append(
                '<p class="empty">'
                "No scheduling conflicts detected."
                "</p>"
            )

        return "\n".join(parts)

    def _render_commitment_item(
        self,
        item: dict[str, Any],
    ) -> str:
        """
        Render one commitment entry.

        Every commitment cites its source message IDs.
        """

        message_id = self._safe_value(
            item.get("message_id")
        )

        title = self._safe_value(
            item.get("title")
        )

        commitment_type = self._safe_value(
            item.get("commitment_type")
        )

        event_time = self._safe_value(
            item.get("event_time")
        )

        source_message_ids = (
            self._get_source_message_ids(
                item
            )
        )

        if source_message_ids:
            source_ids_text = ", ".join(
                self._safe_value(source_id)
                for source_id in source_message_ids
            )
        else:
            source_ids_text = "Not provided"

        return f"""
<div class="item commitment">
    <div class="field">
        <span class="label">Date and time:</span>
        {event_time}
    </div>

    <div class="field">
        <span class="label">Commitment:</span>
        {title}
    </div>

    <div class="field">
        <span class="label">Type:</span>
        {commitment_type}
    </div>

    <div class="field">
        <span class="label">Message:</span>
        {message_id}
    </div>

    <div class="field">
        <span class="label">Source message IDs:</span>
        {source_ids_text}
    </div>
</div>""".strip()

    def _render_conflict_item(
        self,
        item: dict[str, Any],
    ) -> str:
        """
        Render one surfaced scheduling conflict.
        """

        commitment_a = item.get(
            "commitment_a",
            {},
        )

        commitment_b = item.get(
            "commitment_b",
            {},
        )

        first_message_id = self._safe_value(
            commitment_a.get(
                "message_id",
                item.get(
                    "commitment_a_id",
                    "Unknown",
                ),
            )
        )

        second_message_id = self._safe_value(
            commitment_b.get(
                "message_id",
                item.get(
                    "commitment_b_id",
                    "Unknown",
                ),
            )
        )

        first_title = self._safe_value(
            commitment_a.get(
                "title",
                "First commitment",
            )
        )

        second_title = self._safe_value(
            commitment_b.get(
                "title",
                "Second commitment",
            )
        )

        conflict_time = self._safe_value(
            item.get(
                "conflict_time",
                "Unknown",
            )
        )

        return f"""
<div class="item conflict">
    <div class="field">
        <span class="label">Conflict detected:</span>
        Two commitments occur at the same time.
    </div>

    <div class="field">
        <span class="label">Conflict time:</span>
        {conflict_time}
    </div>

    <div class="field">
        <span class="label">First commitment:</span>
        {first_message_id} - {first_title}
    </div>

    <div class="field">
        <span class="label">Second commitment:</span>
        {second_message_id} - {second_title}
    </div>
</div>""".strip()

    # --------------------------------------------------
    # Shared Helpers
    # --------------------------------------------------

    @staticmethod
    def _get_source_message_ids(
        item: dict[str, Any],
    ) -> list[str]:
        """
        Read either the plural or singular source field.

        Current commitments use:
            source_message_id

        Future multi-message commitments may use:
            source_message_ids
        """

        plural_source_ids = item.get(
            "source_message_ids"
        )

        if isinstance(plural_source_ids, list):
            return [
                str(source_id)
                for source_id in plural_source_ids
                if source_id is not None
                and str(source_id).strip()
            ]

        singular_source_id = item.get(
            "source_message_id"
        )

        if singular_source_id is None:
            return []

        if not str(singular_source_id).strip():
            return []

        return [
            str(singular_source_id)
        ]

    @staticmethod
    def _safe_value(
        value: Any,
    ) -> str:
        """
        Escape a value before inserting it into HTML.

        Inbox content is untrusted input.
        """

        if value is None:
            return ""

        return escape(
            str(value),
            quote=True,
        )
