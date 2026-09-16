# Commitment Extractor

"""
Responsibilities:
- Detect future commitment candidates in messages
- Extract and normalize commitment date/time information
- Classify basic commitment types
- Return canonical Commitment objects

Non-responsibilities:
- Conflict detection
- Commitment persistence
- Security analysis
- Dashboard generation
- LLM interactions
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from core.message_model import Message


@dataclass(frozen=True, slots=True)
class Commitment:
    """
    Canonical commitment representation.
    """

    message_id: str
    title: str
    commitment_type: str
    event_time: str
    source_message_id: str

    def to_dict(self) -> dict[str, str]:
        """
        Return a JSON-serializable representation.
        """

        return {
            "message_id": self.message_id,
            "title": self.title,
            "commitment_type": self.commitment_type,
            "event_time": self.event_time,
            "source_message_id": self.source_message_id,
        }


class CommitmentExtractor:
    """
    Deterministic commitment extractor.

    A message is considered a commitment only when it has:

    1. Event or scheduling intent
    2. Specific date or clock-time evidence

    This prevents ordinary messages containing words such as
    "call" or "meeting" from becoming false commitments.
    """

    COMMITMENT_TYPE_MEETING = "MEETING"
    COMMITMENT_TYPE_APPOINTMENT = "APPOINTMENT"
    COMMITMENT_TYPE_EVENT = "EVENT"

    # --------------------------------------------------
    # Event Intent Patterns
    # --------------------------------------------------

    APPOINTMENT_PATTERN = re.compile(
        r"\bappointment\b"
        r"|\bdental\s+cleaning\b",
        re.IGNORECASE,
    )

    MEETING_PATTERN = re.compile(
        r"\bmeeting\b"
        r"|\bcall\b"
        r"|\bstandup\b"
        r"|\bcalendar\s+hold\b"
        r"|\bcalendar\s+invite\b"
        r"|\bcalendar\s+event\b"
        r"|\bintro\s+call\b"
        r"|\bpartner\s+meeting\b",
        re.IGNORECASE,
    )

    EVENT_PATTERN = re.compile(
        r"\bscheduled\b"
        r"|\bevent\b"
        r"|\bstarts?\s+at\b",
        re.IGNORECASE,
    )

    CALENDAR_SUBJECT_PATTERN = re.compile(
        r"\bcalendar\s*:",
        re.IGNORECASE,
    )

    # --------------------------------------------------
    # Date and Time Patterns
    # --------------------------------------------------

    MONTH_DATE_PATTERN = re.compile(
        r"\b("
        r"January|February|March|April|May|June|"
        r"July|August|September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
        r")\s+"
        r"(\d{1,2})"
        r"(?:st|nd|rd|th)?"
        r"(?:,\s*(\d{4}))?"
        r"\b",
        re.IGNORECASE,
    )

    WEEKDAY_ORDINAL_PATTERN = re.compile(
        r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|"
        r"Saturday|Sunday)"
        r"(?:\s+the)?\s+"
        r"(\d{1,2})"
        r"(?:st|nd|rd|th)?"
        r"\b",
        re.IGNORECASE,
    )

    ISO_DATE_PATTERN = re.compile(
        r"\b(\d{4})-(\d{2})-(\d{2})\b"
    )

    NUMERIC_DATE_PATTERN = re.compile(
        r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"
    )

    TIME_PATTERN = re.compile(
        r"\b(?:at\s+|starts?\s+at\s+)?"
        r"(\d{1,2})"
        r"(?::(\d{2}))?"
        r"\s*"
        r"(a\.?m\.?|p\.?m\.?)"
        r"\b",
        re.IGNORECASE,
    )

    MONTH_NUMBERS = {
        "january": 1,
        "jan": 1,
        "february": 2,
        "feb": 2,
        "march": 3,
        "mar": 3,
        "april": 4,
        "apr": 4,
        "may": 5,
        "june": 6,
        "jun": 6,
        "july": 7,
        "jul": 7,
        "august": 8,
        "aug": 8,
        "september": 9,
        "sep": 9,
        "october": 10,
        "oct": 10,
        "november": 11,
        "nov": 11,
        "december": 12,
        "dec": 12,
    }

    def extract(
        self,
        message: Message,
    ) -> Commitment | None:
        """
        Extract a commitment candidate from a message.

        Returns:
            Commitment when event intent and temporal evidence
            are both present.

            None when the message does not represent a
            sufficiently grounded commitment.
        """

        if not isinstance(message, Message):
            raise TypeError(
                "CommitmentExtractor.extract() expects a Message"
            )

        text = message.text

        commitment_type = self._get_commitment_type(
            subject=message.subject,
            text=text,
        )

        if commitment_type is None:
            return None

        event_time = self._extract_event_time(
            text=text,
            message_timestamp=message.timestamp,
        )

        if event_time is None:
            return None

        return Commitment(
            message_id=message.message_id,
            title=message.subject,
            commitment_type=commitment_type,
            event_time=event_time,
            source_message_id=message.message_id,
        )

    # --------------------------------------------------
    # Commitment Intent
    # --------------------------------------------------

    def _get_commitment_type(
        self,
        subject: str,
        text: str,
    ) -> str | None:
        """
        Determine whether the message contains
        appointment, meeting, or event intent.
        """

        if self.APPOINTMENT_PATTERN.search(text):
            return self.COMMITMENT_TYPE_APPOINTMENT

        if (
            self.CALENDAR_SUBJECT_PATTERN.search(subject)
            or self.MEETING_PATTERN.search(text)
        ):
            return self.COMMITMENT_TYPE_MEETING

        if self.EVENT_PATTERN.search(text):
            return self.COMMITMENT_TYPE_EVENT

        return None

    # --------------------------------------------------
    # Date and Time Extraction
    # --------------------------------------------------

    def _extract_event_time(
        self,
        text: str,
        message_timestamp: str | None,
    ) -> str | None:
        """
        Extract and normalize an event timestamp.

        Rules:
        - Explicit month and day use that date.
        - Weekday plus ordinal day uses the message month/year.
        - Time-only reminders use the date of the message timestamp.
        - A clock time is required for the current assignment's
          conflict-planning use case.

        Returns:
            ISO timestamp or None.
        """

        time_parts = self._extract_clock_time(text)

        if time_parts is None:
            return None

        hour, minute = time_parts

        reference_time = self._parse_reference_timestamp(
            message_timestamp
        )

        date_parts = self._extract_explicit_date(
            text=text,
            reference_time=reference_time,
        )

        if date_parts is None:
            if reference_time is None:
                return None

            year = reference_time.year
            month = reference_time.month
            day = reference_time.day
        else:
            year, month, day = date_parts

        try:
            event_datetime = datetime(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                second=0,
            )
        except ValueError:
            return None

        return event_datetime.isoformat()

    def _extract_explicit_date(
        self,
        text: str,
        reference_time: datetime | None,
    ) -> tuple[int, int, int] | None:
        """
        Extract year, month, and day from supported
        deterministic date patterns.
        """

        iso_match = self.ISO_DATE_PATTERN.search(text)

        if iso_match:
            return (
                int(iso_match.group(1)),
                int(iso_match.group(2)),
                int(iso_match.group(3)),
            )

        numeric_match = self.NUMERIC_DATE_PATTERN.search(text)

        if numeric_match:
            return (
                int(numeric_match.group(3)),
                int(numeric_match.group(1)),
                int(numeric_match.group(2)),
            )

        month_match = self.MONTH_DATE_PATTERN.search(text)

        if month_match:
            month_name = month_match.group(1).casefold()
            month = self.MONTH_NUMBERS[month_name]
            day = int(month_match.group(2))

            if month_match.group(3):
                year = int(month_match.group(3))
            elif reference_time is not None:
                year = reference_time.year
            else:
                return None

            return year, month, day

        ordinal_match = self.WEEKDAY_ORDINAL_PATTERN.search(text)

        if ordinal_match and reference_time is not None:
            return (
                reference_time.year,
                reference_time.month,
                int(ordinal_match.group(1)),
            )

        return None

    def _extract_clock_time(
        self,
        text: str,
    ) -> tuple[int, int] | None:
        """
        Extract and normalize a 12-hour clock time.
        """

        match = self.TIME_PATTERN.search(text)

        if not match:
            return None

        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        meridiem = (
            match.group(3)
            .replace(".", "")
            .casefold()
        )

        if hour < 1 or hour > 12:
            return None

        if minute < 0 or minute > 59:
            return None

        if meridiem == "pm" and hour != 12:
            hour += 12

        if meridiem == "am" and hour == 12:
            hour = 0

        return hour, minute

    @staticmethod
    def _parse_reference_timestamp(
        timestamp: str | None,
    ) -> datetime | None:
        """
        Parse the source message timestamp for use as
        the reference year/month/date.

        No current-system date is assumed.
        """

        if not timestamp:
            return None

        try:
            return datetime.fromisoformat(timestamp)
        except ValueError:
            return None