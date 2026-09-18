# R6 - Dashboard

"""
Responsibilities:
- Build the R6 dashboard
- Render dashboard output
- Save dashboard HTML
- Produce an inspectable capability result

Non-responsibilities:
- Commitment extraction
- Conflict detection
- Security analysis
- HTML generation logic
- LLM interactions
"""

from __future__ import annotations

from dashboard.dashboard_builder import (
    DashboardBuilder,
)

from dashboard.html_renderer import (
    HtmlRenderer,
)


class R6Dashboard:
    """
    Capability wrapper for R6.

    Produces the InboxHero dashboard using
    the already-frozen dashboard components.
    """

    REQUIRED_PANES = {
        "pending_actions",
        "flagged_items",
        "commitments",
    }

    def __init__(
        self,
        builder=None,
        renderer=None,
    ):

        self.builder = (
            builder or DashboardBuilder()
        )

        self.renderer = (
            renderer or HtmlRenderer()
        )

    def generate(
        self,
        pending_actions,
        flagged_items,
        commitments,
        conflicts,
    ):
        """
        Generate dashboard and save HTML.

        Returns an inspectable capability
        report suitable for grading.
        """

        dashboard = self.builder.build(
            pending_actions=pending_actions,
            flagged_items=flagged_items,
            commitments=commitments,
            conflicts=conflicts,
        )

        dashboard_data = dashboard.to_dict()

        html_file = self.renderer.save(
            dashboard
        )

        pane_names = set(
            dashboard_data.keys()
        )

        has_exactly_three_panes = (
            pane_names
            == self.REQUIRED_PANES
        )

        return {
            "dashboard_created": True,
            "dashboard_file": str(
                html_file
            ),
            "pane_count": len(
                dashboard_data
            ),
            "pane_names": list(
                dashboard_data.keys()
            ),
            "passed": (
                has_exactly_three_panes
            ),
        }

