# Recipet Classifier

"""
Responsibilities:
- Detect receipts, invoices, billing confirmations
- Support rule-based routing
- Avoid unnecessary LLM calls

Part 2 Requirement:
Route obvious messages through rules, not an LLM.
"""

from __future__ import annotations

from core.message_model import Message


class ReceiptClassifier:
    """
    Detects receipts and invoices using lightweight rules.
    """

    RECEIPT_SENDERS = {
        "receipts@",
        "billing@",
        "invoice",
        "ship-confirm",
        "orders@",
        "uber.com",
        "lyft.com",
        "swiggy.in",
        "amazon.com",
        "openai.com",
        "digitalocean.com",
        "doordash.com",
        "spotify.com",
        "instacart.com",
        "ramp.com",
    }

    RECEIPT_SUBJECT_KEYWORDS = {
        "receipt",
        "invoice paid",
        "monthly invoice",
        "bill",
        "charged",
        "order confirmed",
        "order has shipped",
        "order is delivered",
        "payment received",
        "your monthly invoice",
        "your invoice",
        "your bill",
    }

    def is_receipt(self, message: Message) -> bool:
        """
        Return True if the message is likely
        a receipt, invoice, bill, or purchase confirmation.
        """

        sender = message.sender.lower()
        subject = message.subject.lower()

        # Sender-based rules
        for keyword in self.RECEIPT_SENDERS:
            if keyword in sender:
                return True

        # Subject-based rules
        for keyword in self.RECEIPT_SUBJECT_KEYWORDS:
            if keyword in subject:
                return True

        return False

    def reason(self) -> str:
        """
        Standard classifier reason.
        """

        return "Receipt or invoice detected by rule-based classifier"