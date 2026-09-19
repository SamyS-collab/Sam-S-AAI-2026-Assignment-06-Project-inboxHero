# Command structure for the manifest all capablities execution one by one

from __future__ import annotations

import argparse
import json

from core.inbox_loader import InboxLoader
from core.router import Router
from core.disposition_engine import (
    DispositionEngine,
)

from capabilities.r1_zeroing import (
    R1Zeroing,
)

from capabilities.r2_grounded_reply import (
    R2GroundedReply,
)

from capabilities.r3_safety_gate import (
    R3SafetyGate,
)

from capabilities.r4_preference_memory import (
    R4PreferenceMemory,
)

from capabilities.r5_hostile_inbox import (
    HostileInboxProtection,
)

from capabilities.r6_dashboard import (
    R6Dashboard,
)

from capabilities.x1_daily_digest import (
    X1DailyDigest,
)

from capabilities.x2_followup_tracker import (
    X2FollowupTracker,
)

from capabilities.x3_thread_summary import (
    X3ThreadSummary,
)

from capabilities.x4_explain_decision import (
    X4ExplainDecision,
)

from capabilities.x5_commitment_planner import (
    X5CommitmentPlanner,
)

from commitments.commitment_manager import (
    CommitmentManager,
)

from dashboard.dashboard_builder import (
    DashboardBuilder,
)

from security.prompt_injection_detector import (
    PromptInjectionDetector,
)

from security.phishing_detector import (
    PhishingDetector,
)

from security.security_engine import (
    SecurityEngine,
)

from core.audit_logger import (
    AuditLogger,
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def build_message_state():
    loader = InboxLoader()

    messages = loader.load()

    router = Router()
    engine = DispositionEngine()

    for message in messages:
        router.route(message)
        engine.assign(message)

    return messages


def get_message_by_id(
    messages,
    message_id,
):
    for message in messages:
        if message.message_id == message_id:
            return message

    raise ValueError(
        f"Message {message_id!r} not found."
    )


def print_result(result):
    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False,
        )
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--cap",
        required=True,
    )

    parser.add_argument(
        "--msg",
        required=False,
    )

    args = parser.parse_args()

    cap = args.cap.upper()

    messages = build_message_state()

    # ------------------------------------------
    # R1
    # ------------------------------------------

    if cap == "R1":

        result = (
            R1Zeroing()
            .validate(messages)
        )

        print_result(result)

        return

    # ------------------------------------------
    # R2
    # ------------------------------------------

    if cap == "R2":

        if not args.msg:
            raise ValueError(
                "--msg required for R2"
            )

        result = (
            R2GroundedReply()
            .generate_reply(
                args.msg
            )
        )

        print_result(result)

        return

    # ------------------------------------------
    # R3
    # ------------------------------------------

    if cap == "R3":

        message = messages[0]

        decision = (
            DispositionEngine()
            .assign(message)
        )

        result = (
            R3SafetyGate()
            .evaluate(decision)
        )

        print_result(result)

        return

    # ------------------------------------------
    # R4
    # ------------------------------------------

    if cap == "R4":

        result = (
            R4PreferenceMemory()
            .report()
        )

        print_result(result)

        return

    # ------------------------------------------
    # R5
    # ------------------------------------------

    if cap == "R5":

        prompt_detector = (
            PromptInjectionDetector()
        )

        phishing_detector = (
            PhishingDetector()
        )

        logger = AuditLogger()

        security_engine = SecurityEngine(
            prompt_injection_detector=(
                prompt_detector
            ),
            phishing_detector=(
                phishing_detector
            ),
            audit_logger=logger,
        )

        capability = (
            HostileInboxProtection(
                security_engine=
                    security_engine,
                logger=logger,
            )
        )

        findings = []

        for message in messages:

            result = capability.evaluate(
                message
            )

            if result is not None:
                findings.append(
                    result.to_dict()
                )

        print_result(findings)

        return

    # ------------------------------------------
    # R6
    # ------------------------------------------

    if cap == "R6":

        manager = CommitmentManager()

        manager.build(messages)

        builder = DashboardBuilder()

        pending_actions = [
            builder.build_pending_action(
                message_id="m012",
                action="REPLY",
                human_reason=(
                    "Clarification required "
                    "before response."
                ),
            )
        ]

        flagged_items = [
            builder.build_flagged_item(
                message_id="m023",
                threat_type="PHISHING",
                attempted_action=(
                    "Requested immediate "
                    "wire transfer."
                ),
                system_response=(
                    "REFUSED_AND_FLAGGED"
                ),
            )
        ]

        result = (
            R6Dashboard()
            .generate(
                pending_actions=
                    pending_actions,
                flagged_items=
                    flagged_items,
                commitments=
                    manager.get_commitments(),
                conflicts=
                    manager.get_conflicts(),
            )
        )

        print_result(result)

        return

    # ------------------------------------------
    # X1
    # ------------------------------------------

    if cap == "X1":

        tracker = X2FollowupTracker()

        followup_result = (
            tracker.analyze(messages)
        )

        manager = CommitmentManager()

        manager.build(messages)

        planner = X5CommitmentPlanner(
            manager
        )

        digest = (
            X1DailyDigest()
            .generate(
                followup_result=
                    followup_result,

                flagged_items=[],

                commitment_result={
                    "commitments":
                        manager
                        .get_commitments(),
                    "conflicts":
                        manager
                        .get_conflicts(),
                },

                conflict_plan_result=
                    planner.analyze(),
            )
        )

        print_result(digest)

        return

    # ------------------------------------------
    # X2
    # ------------------------------------------

    if cap == "X2":

        result = (
            X2FollowupTracker()
            .analyze(messages)
        )

        print_result(result)

        return

    # ------------------------------------------
    # X3
    # ------------------------------------------

    if cap == "X3":

        if not args.msg:
            raise ValueError(
                "--msg required for X3"
            )

        result = (
            X3ThreadSummary()
            .summarize(
                args.msg
            )
        )

        print_result(result)

        return

    # ------------------------------------------
    # X4
    # ------------------------------------------

    if cap == "X4":

        if not args.msg:
            raise ValueError(
                "--msg required for X4"
            )

        message = get_message_by_id(
            messages,
            args.msg,
        )

        result = (
            X4ExplainDecision()
            .explain(message)
        )

        print_result(result)

        return

    # ------------------------------------------
    # X5
    # ------------------------------------------

    if cap == "X5":

        manager = CommitmentManager()

        manager.build(messages)

        result = (
            X5CommitmentPlanner(
                manager
            )
            .analyze()
        )

        print_result(result)

        return

    raise ValueError(
        f"Unknown capability: {cap}"
    )


if __name__ == "__main__":
    main()
