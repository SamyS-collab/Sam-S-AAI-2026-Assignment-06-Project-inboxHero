# InboxHero Final Report

**Student:** SAMIR SARDAL, cert-aai-2026-06-0051  
**Repository:** https://github.com/SamyS-collab/Sam-S-AAI-2026-Assignment-06-Project-inboxHero

## System Overview

InboxHero is a local Python-based agentic inbox management system that processes a JSON inbox, assigns dispositions, retrieves supporting context, drafts grounded replies, protects against hostile content, records user preferences, tracks commitments, and produces dashboard and planning outputs. It uses LLM onlu for 2 capabliites

## Framework Choice

**Framework: None**s

InboxHero was intentionally implemented without CrewAI, Google ADK, LangGraph, AutoGen, or another agent framework.

Analysis of the inbox showed that most messages belonged to deterministic categories such as newsletters, receipts, notifications, and scheduling updates. These messages are handled through rule-based classifiers to reduce latency, improve traceability, and avoid unnecessary model calls.

Language models are reserved only for tasks that genuinely require reasoning, retrieval, ambiguity handling, grounded reply generation, or thread summarization. Instead of relying on a framework, InboxHero implements its own modular architecture consisting of a Router, Disposition Engine, Security Engine, Retrieval Engine, Commitment Manager, Dashboard Builder, and Capability Layer. 

This approach keeps behavior deterministic, makes security boundaries explicit, and allows every requirement and capability to be tested independently.

## Retrieval Approach

InboxHero uses thread-walk retrieval. The retrieval pipeline consists of MessageLookup, ThreadRetriever, and RetrievalEngine. This approach reconstructs the relevant conversation in chronological order and preserves the source message IDs used for grounding.

The verified grounding example is message m008. Its relevant thread contains m001, m003, m005, and m008. The system records these source IDs in generated reply and summary artifacts.

## Disposition Vocabulary

InboxHero uses the following dispositions consistently:

- `ARCHIVE`: Informational message requiring no further action.
- `REPLY`: A response may be drafted. This does not mean the reply is sent.
- `DEFER`: Action is needed later, or the message safely awaits further analysis.
- `ESCALATE`: Human review or a human decision is required.
- `FLAG`: A security, trust, grounding, compliance, or policy concern was detected.

## Reversible and Irreversible Boundary

### Irreversible

- `send`

A sent message cannot be unsent. InboxHero never sends real email. Drafts are written only to `outbox/`.

### Reversible

- `draft`
- `archive`
- `defer`
- `flag`
- `escalate`

These actions can be reviewed, changed, or reversed later.

## Escalation Boundary and Trade-off

InboxHero does not ask for human approval on every routine action. Human attention is reserved for clarification, conflicts, hostile requests, policy blocks, and future irreversible actions. This reduces approval fatigue. The trade-off is that uncertain messages are safely deferred instead of being aggressively automated.


## 1. What did you refuse to automate? Name one message your system deliberately does not handle on its own, and explain why you drew the line there.

InboxHero deliberately refuses to automate hostile or suspicious requests. A concrete example is message **m023**, which was identified as a phishing attempt requesting an immediate confidential wire transfer while explicitly asking that finance not be involved. The system classified the message as hostile, refused to act on it, flagged it, logged the refusal, and notified the user instead of executing the request. 

Another example is message **m017** PROMPT_INJECTION refused to act on it, flagged it, logged the refusal, and notified the user instead of executing the request

I drew this boundary because financial transfers, credential sharing, and other irreversible actions create disproportionate risk if the message is malicious. Even when an action appears urgent, InboxHero prefers refusal and human review over autonomous execution.

## 2. Where does untrusted text enter your system? Describe the boundary between text your system reads and instructions it follows, as a property of your architecture rather than a line in a prompt. Name what an attacker would have to defeat to make your system act on their behalf.

Untrusted text enters the system through inbox messages loaded from `inbox.json`. The architectural boundary is not a prompt instruction but a system design boundary: email content is treated as untrusted data, while actions are only available through controlled components. 

Messages first pass through the Security Engine, which includes the Prompt Injection Detector and Phishing Detector. For an attacker to make InboxHero act on their behalf, the attacker would have to bypass hostile-content detection, survive disposition processing, pass policy validation, and reach the action layer through the Gatekeeper and approval workflow. This layered architecture ensures that reading a message is not the same thing as obeying it.

## 3. Who is accountable when it sends the wrong thing? If a message sent in the owner’s name is badly worded, factually wrong, or sent to the wrong person, who is answerable, and how does your system help trace back the failure?

The human owner remains accountable for any communication sent in their name. InboxHero reduces risk by preserving a complete audit trail from retrieval through generation and storage. Every generated draft records the `source_message_ids` used for grounding, and draft content is validated before being written to `outbox/`. 

If a draft is factually incorrect, poorly worded, or based on the wrong context, the stored provenance and logs make it possible to trace the decision back through the Retrieval Engine, Reply Generator, Policy Validator, and Outbox Writer. The system improves traceability and accountability, but it does not replace human responsibility.

## 4. Name your own machinery. Point to the parts of your code that play the roles of a framework’s Agents, Tasks, Crew and router. Name one thing a framework would have given you that you built yourself, and say whether using one here would have helped or hurt, and why.

InboxHero was implemented without an agent framework, so its machinery is explicit and visible in code. The **Capability wrappers** does orecheratraion. The **Router** plays the routing role by categorizing messages before disposition. The **Disposition Engine**, **Security Engine**, **Retrieval Engine**, **Commitment Manager**, and **Dashboard Builder** collectively perform responsibilities that a framework might label as agents, tasks, crews, memory, and orchestration. 

One capability a framework would have provided automatically is workflow orchestration between components, including execution planning and dependency management. 

In this project, I built those orchestration paths myself, which increased implementation effort but made behavior easier to verify, debug, audit, and map directly to the assignment requirements.
