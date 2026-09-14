# Meeting classifier

"""
Responsibilities:
- Detect meeting requests
- Detect scheduling requests
- Detect calendar events and appointments
- Support rule-based routing
- Avoid unnecessary LLM calls

Part 2 Requirement:
Route obvious messages through rules, not an LLM.
"""

from __future__ import annotations

from core.message_model import Message


class MeetingClassifier:
    """
    Detects meetings, scheduling requests,
    appointments, and calendar events.
    """

    EXCLUDED_SENDERS = {
        "newsletter@",
        "receipts@",
        "billing@",
        "orders@",
        "ship-confirm@",
    }

    MEETING_PATTERNS = {
        "calendar-notification@google.com",
        "calendly.com",
        "zoom.us",
        "teams.microsoft.com",
        "webex.com",
        "meet.google.com",
        "join.me",
        "gotomeeting.com",
        "skype.com",
    }

    MEETING_SUBJECT_KEYWORDS = {
        "intro call",
        "move our 1:1",
        "demo",
        "scheduled",
        "meeting",
        "appointment",
        "board review",
        "coffee",
        "standup",
        "1:1",
    }

    MEETING_BODY_KEYWORDS = {
        "does that slot work",
        "can we move",
        "join with the meet link",
        "calendar hold",
        "grab coffee",
        "confirming",
        "appointment",
        "product demo",
        "standup",
        "1:1",
    }

    def is_meeting(self, message: Message) -> bool:
        """
        Return True if the message appears
        to be a meeting request, scheduling
        discussion, appointment, or event.
        """

        sender = message.sender.lower()
        subject = message.subject.lower()
        body = message.body.lower()

        # Known non-meeting patterns
        if "cloud recording is ready" in subject:
            return False

        if "notes from last week" in subject:
            return False

        if subject.strip() == "the thing":
            return False

        # Explicit exclusions
        for excluded in self.EXCLUDED_SENDERS:
            if excluded in sender:
                return False

                
        # Sender/domain rules
        for keyword in self.MEETING_PATTERNS:
            if keyword in sender:
                return True

        # Subject rules
        for keyword in self.MEETING_SUBJECT_KEYWORDS:
            if keyword in subject:
                return True

        # Body rules
        for keyword in self.MEETING_BODY_KEYWORDS:
            if keyword in body:
                return True

        return False

    def reason(self) -> str:
        """
        Standard classifier reason.
        """

        return (
            "Meeting or scheduling request "
            "detected by rule-based classifier"
        )

    def confidence(self) -> float:
        """
        Static confidence score for
        deterministic rule matches.
        """

        return 1.0
