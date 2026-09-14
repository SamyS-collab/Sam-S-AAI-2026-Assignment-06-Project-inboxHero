# Notification Classifier

"""
Responsibilities:
- Detect notifications, alerts, reminders, digests and activity updates
- Support rule-based routing
- Avoid unnecessary LLM calls

Part 2 Requirement:
Route obvious messages through rules, not an LLM.
"""

from __future__ import annotations

from core.message_model import Message


class NotificationClassifier:
    """
    Detects notifications and informational alerts using rules.
    """

    NOTIFICATION_PATTERNS = {
        "notifications@",
        "noreply@github.com",
        "calendar-notification@google.com",
        "alerts@",
        "security@",
        "accounts.google.com",
        "pagerduty.com",
        "sentry.io",
        "datadoghq.com",
        "cloudflare.com",
        "notion.so",
        "slack.com",
        "linkedin.com",
        "google.com",
        "twitter.com",
        "mailchimp.com",
        "zoom.us",
        "postmarkapp.com",
        "figma.com",
        "todoist.com",
        "grammarly.com",
        "calendly.com",
    }

    NOTIFICATION_SUBJECT_KEYWORDS = {
        "unread messages",
        "new comments",
        "new login",
        "new sign-in",
        "verification code",
        "security digest",
        "incident resolved",
        "monitor ok again",
        "new activity",
        "analytics",
        "daily digest",
        "weekly activity",
        "weekly analytics",
        "cloud recording is ready",
        "notifications",
        "appeared in",
        "reminder",
        "check-in is open",
    }

    EXCLUDED_SENDERS = {
                "receipts@",
                "billing@",
                "orders@",
                "ship-confirm@",
                "newsletter@",
           }

    def is_notification(self, message: Message) -> bool:
        """
        Return True if the message is likely a
        notification, status update, reminder,
        security alert, or activity update.
        """


        sender = message.sender.lower()
        subject = message.subject.lower()

        # Explicit exclusions
        for excluded in self.EXCLUDED_SENDERS:
            if excluded in sender:
                return False

        # Sender-based rules
        for keyword in self.NOTIFICATION_PATTERNS:
            if keyword in sender:
                return True

        # Subject-based rules
        for keyword in self.NOTIFICATION_SUBJECT_KEYWORDS:
            if keyword in subject:
                return True

        return False

    def reason(self) -> str:
        """
        Standard classifier reason.
        """

        return (
            "Notification detected by "
            "rule-based classifier"
        )

    def confidence(self) -> float:
        return 1.0