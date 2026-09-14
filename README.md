Framework: None

Reason:

Analysis of inbox.json showed that most messages belonged to
deterministic categories such as newsletters, receipts,
notifications, and scheduling updates. These were handled using
rule-based classifiers to reduce latency, improve traceability,
and avoid unnecessary model calls.

Language models were reserved only for tasks requiring reasoning,
retrieval, ambiguity resolution, or response generation.

