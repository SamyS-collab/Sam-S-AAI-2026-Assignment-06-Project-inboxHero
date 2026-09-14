# Newsletter Classifier

"""
Responsibilities:
- Detect newsletter-style messages
- Support rule-based routing
- Avoid unnecessary LLM calls

Part 2 Requirement:
Route obvious messages through rules, not an LLM.
"""

from __future__ import annotations

from core.message_model import Message

class NewsletterClassifier:
    """
    Detects newsletters using lightweight rules.
    """

    NEWSLETTER_SENDERS = {
        "newsletter",
        "digest",
        "substack",
        "producthunt",
        "pragmaticengineer",
        "medium.com",
        "coursera.org",
        "hackernewsletter",
    }

    EXCLUDED_SENDERS = {
        "cloudflare.com",
        "figma.com",
        "todoist.com",
    }

    NEWSLETTER_SUBJECT_KEYWORDS = {
        "daily digest",
        "weekly digest",
        "weekly report",
        "weekly screen time report",
        "today's top",
        "top stories",
        "weekly analytics",
        "weekly activity",
        "course recommendations",
        "welcome back",
        "subscription",
    }

    def is_newsletter(self, message: Message) -> bool:
        """
        Return True if message is likely a newsletter.
        """

        sender = message.sender.lower()
        subject = message.subject.lower()

        # Explicit exclusions
        for excluded in self.EXCLUDED_SENDERS:
            if excluded in sender:
                return False

        # Sender-based rules
        for keyword in self.NEWSLETTER_SENDERS:
            if keyword in sender:
                return True
            
        # Subject-based rules
        for keyword in self.NEWSLETTER_SUBJECT_KEYWORDS:
            if keyword in subject:
                return True

        return False

    def reason(self) -> str:
        """
        Standard classifier reason.
        """

        return "Newsletter detected by rule-based classifier"

