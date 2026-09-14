# disposition engine test

from collections import Counter

from core.disposition_engine import DispositionEngine
from core.inbox_loader import InboxLoader
from core.router import Router


def main() -> None:
    loader = InboxLoader()
    router = Router()
    engine = DispositionEngine()

    messages = loader.load()

    disposition_counts = Counter()
    handled_by_counts = Counter()

    decisions = []

    print("\n=== DISPOSITION ENGINE TEST ===\n")

    for message in messages:
        router.route(message)
        decision = engine.assign(message)

        decisions.append(decision)

        disposition_counts[decision.disposition.value] += 1
        handled_by_counts[decision.handled_by] += 1

        print(
            f"{decision.message_id} | "
            f"{decision.category:<12} | "
            f"{decision.disposition.value:<8} | "
            f"model_required={str(decision.model_required):<5} | "
            f"{decision.reason}"
        )

    missing_dispositions = [
        message.message_id
        for message in messages
        if not message.metadata.get("disposition")
    ]

    missing_reasons = [
        message.message_id
        for message in messages
        if not message.metadata.get("disposition_reason")
    ]

    print("\n=== DISPOSITION TOTALS ===")

    for disposition, count in sorted(disposition_counts.items()):
        print(f"{disposition:<10}: {count}")

    print("\n=== PROCESSING SOURCE TOTALS ===")

    for source, count in sorted(handled_by_counts.items()):
        print(f"{source:<20}: {count}")

    print("\n=== PART 2 VALIDATION ===")

    print(f"Messages processed       : {len(messages)}")
    print(f"Decisions produced       : {len(decisions)}")
    print(f"Missing dispositions     : {len(missing_dispositions)}")
    print(f"Missing reasons          : {len(missing_reasons)}")

    assert len(decisions) == len(messages), (
        "Not every message received a disposition decision"
    )

    assert not missing_dispositions, (
        f"Messages without dispositions: {missing_dispositions}"
    )

    assert not missing_reasons, (
        f"Messages without reasons: {missing_reasons}"
    )

    print("\nPart 2 structural validation passed.")


if __name__ == "__main__":
    main()


# # Router test

# from collections import Counter

# from core.inbox_loader import InboxLoader
# from core.router import Router


# def main():
#     loader = InboxLoader()
#     messages = loader.load()

#     router = Router()

#     category_counts = Counter()

#     print("\n=== ROUTER TEST ===\n")

#     for message in messages:
#         category = router.route(message)

#         category_counts[category] += 1

#         print(
#             f"{message.message_id} | "
#             f"{category:<12} | "
#             f"{message.subject}"
#         )

#     print("\n=== CATEGORY TOTALS ===")

#     for category, count in sorted(category_counts.items()):
#         print(f"{category:<12} : {count}")


# if __name__ == "__main__":
#     main()







# # Meeting classifier test

# from classifiers.meeting_classifier import MeetingClassifier
# from core.inbox_loader import InboxLoader


# def main():
#     loader = InboxLoader()

#     messages = loader.load()

#     classifier = MeetingClassifier()

#     meeting_count = 0

#     print("\n=== MEETING CLASSIFIER TEST ===\n")

#     for message in messages:
#         if classifier.is_meeting(message):
#             meeting_count += 1

#             print(
#                 f"{message.message_id} | "
#                 f"{message.subject}"
#             )

#     print("\n==============================")
#     print(f"Total Meeting Messages: {meeting_count}")


# if __name__ == "__main__":
#     main()



# # Notification classifier test
# from classifiers.notification_classifier import NotificationClassifier
# from core.inbox_loader import InboxLoader

# loader = InboxLoader()
# messages = loader.load()

# classifier = NotificationClassifier()

# for message in messages:
#     if classifier.is_notification(message):
#         print(
#             f"{message.message_id} | "
#             f"{message.subject}"
#         )


# # reciept classifier test

# from classifiers.receipt_classifier import ReceiptClassifier
# from core.inbox_loader import InboxLoader

# loader = InboxLoader()
# messages = loader.load()

# classifier = ReceiptClassifier()

# for message in messages:
#     if classifier.is_receipt(message):
#         print(
#             f"{message.message_id} | "
#             f"{message.subject}"
#         )


# newsletter classifier test

# from classifiers.newsletter_classifier import NewsletterClassifier
# from core.inbox_loader import InboxLoader

# loader = InboxLoader()
# messages = loader.load()

# classifier = NewsletterClassifier()

# for message in messages:
#     if classifier.is_newsletter(message):
#         print(
#             f"{message.message_id} | "
#             f"{message.subject}"
#         )


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