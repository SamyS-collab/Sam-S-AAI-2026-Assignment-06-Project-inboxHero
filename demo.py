# classifier test

from classifiers.newsletter_classifier import NewsletterClassifier
from core.inbox_loader import InboxLoader

loader = InboxLoader()
messages = loader.load()

classifier = NewsletterClassifier()

for message in messages:
    if classifier.is_newsletter(message):
        print(
            f"{message.message_id} | "
            f"{message.subject}"
        )


# Auditlogger test
# from core.audit_logger import AuditLogger
# from core.inbox_loader import InboxLoader

# loader = InboxLoader()
# messages = loader.load()

# logger = AuditLogger()

# logger.log(
#     "INBOX_LOADED",
#     message_count=len(messages)
# )

# print(f"Messages Loaded: {len(messages)}")
# print("Audit event written.")








# # Inbox loder test

# from core.inbox_loader import InboxLoader

# loader = InboxLoader()

# messages = loader.load()

# print(f"Messages Loaded: {len(messages)}")
# print(messages[0])