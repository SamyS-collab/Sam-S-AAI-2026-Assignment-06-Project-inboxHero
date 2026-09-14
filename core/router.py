# InboxHero Router

"""
Responsibilities:
- Route messages through rule-based classifiers
- Assign an initial category
- Identify messages requiring further processing

Non-responsibilities:
- Assign dispositions
- Security analysis
- LLM calls
- Reply generation
"""

from __future__ import annotations

from classifiers.newsletter_classifier import NewsletterClassifier
from classifiers.receipt_classifier import ReceiptClassifier
from classifiers.notification_classifier import NotificationClassifier
from classifiers.meeting_classifier import MeetingClassifier

from core.message_model import Message


class Router:
    """
    Initial routing layer.

    Determines the category of a message using
    rule-based classifiers.
    """

    NEWSLETTER = "newsletter"
    RECEIPT = "receipt"
    NOTIFICATION = "notification"
    MEETING = "meeting"
    UNKNOWN = "unknown"

    def __init__(self) -> None:
        self.newsletter_classifier = NewsletterClassifier()
        self.receipt_classifier = ReceiptClassifier()
        self.notification_classifier = NotificationClassifier()
        self.meeting_classifier = MeetingClassifier()
    
    def route(self, message: Message) -> str:
        """
        Determine message category.

        Order matters.

        Returns:
            newsletter
            receipt
            notification
            meeting
            unknown
        """

        if self.newsletter_classifier.is_newsletter(message):
            message.metadata["category"] = self.NEWSLETTER
            return self.NEWSLETTER

        if self.receipt_classifier.is_receipt(message):
            message.metadata["category"] = self.RECEIPT
            return self.RECEIPT

        if self.notification_classifier.is_notification(message):
            message.metadata["category"] = self.NOTIFICATION
            return self.NOTIFICATION

        if self.meeting_classifier.is_meeting(message):
            message.metadata["category"] = self.MEETING
            return self.MEETING

        message.metadata["category"] = self.UNKNOWN
        return self.UNKNOWN