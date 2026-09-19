# InboxHero Capabilities

**Student:** SAMIR SARDAL, cert-aai-2026-06-0051  
**Repository:** https://github.com/SamyS-collab/Sam-S-AAI-2026-Assignment-06-Project-inboxHero

## System Overview

InboxHero is a local Python-based agentic inbox management system that processes a JSON inbox, assigns dispositions, retrieves supporting context, drafts grounded replies, protects against hostile content, records user preferences, tracks commitments, and produces dashboard and planning outputs.

| Item | Value |
|---|---|
| Framework | none |
| Model | Gemini 3.5 Flash Lite / Gemini 3.5 Flash / Gemini 3.6 Flash depending on availability. Developed and verified through Google GenAI. |
| Messages processed | 100 |
| Rule handled | 60 |
| Retrieval method | thread-walk |
| Gate type | approval |
| Irreversible actions | send |
| Reversible actions | draft, archive, defer, flag, escalate |
| Preference demonstration | m041: No meetings before 11:00 AM |

## Framework Choice

**Framework:** None

InboxHero was intentionally implemented without CrewAI, Google ADK, LangGraph, AutoGen, or another agent framework.

Analysis of the inbox showed that most messages belonged to deterministic categories such as newsletters, receipts, notifications, and scheduling updates. These messages are handled through rule-based classifiers to reduce latency, improve traceability, and avoid unnecessary model calls.

Language models are reserved only for tasks that genuinely require reasoning, retrieval, ambiguity handling, grounded reply generation, or thread summarization. Instead of relying on a framework, InboxHero implements its own modular architecture consisting of a Router, Disposition Engine, Security Engine, Retrieval Engine, Commitment Manager, Dashboard Builder, and Capability Layer. 

This approach keeps behavior deterministic, makes security boundaries explicit, and allows every requirement and capability to be tested independently.

## Inbox Assumptions

InboxHero assumes inbox.json contains:

- id
- thread_id
- from
- to
- subject
- timestamp
- body
- unread

for every message.

The verified inbox contains approximately 100 messages.



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

# Execution Instructions

Windows users may need to run: py demo.py --cap R1

instead of: python demo.py --cap R1

depending on local Python installation and PATH configuration.

# Required Capabilities

## R1 - Zeroing It

**Tier:** B  
**Claim:** Processes all inbox messages and assigns exactly one disposition and one reason to every message, leaving none undecided.

**Command**

```bash
python demo.py --cap R1
```

**Observable result**

- `messages_processed=100`
- `decisions_produced=100`
- `missing_dispositions=0`
- `missing_reasons=0`
- `passed=true`

**Evidence**

- `trace.jsonl`
- R1 capability output

## R2 - Grounded Reply Generation

**Tier:** B  
**Claim:** Generates grounded replies using retrieved inbox messages, records source message IDs, and blocks unsafe credential disclosure.

**Command**

```bash
python demo.py --cap R2 --msg m008
```

Verified Grounding Example

m008 depends on m003.

The retrieval layer returned:

m001
m003
m005
m008

The generated draft preserved source_message_ids
for all grounding messages.


**Observable result**

The capability returns a clarification draft for m008 and records these source message IDs:

- m001
- m003
- m005
- m008

The generated credential-bearing AMQP connection string is blocked. The result reports `policy_allowed=false`, preserves provenance, and writes only the safe clarification artifact to `outbox/`.

**Evidence**

- R2 capability output
- `outbox/` artifact
- `trace.jsonl`

## R3 - Gate the Irreversible

**Tier:** C  
**Claim:** Evaluates actions through a safety gate, records approval decisions, and enforces outbox-only behavior.

**Command**

```bash
python demo.py --cap R3
```

**Observable result**

The capability returns:

- `reversible`
- `approval_required`
- `approved`
- `reason`
- `outbox_only=true`
- `real_email_sending=false`
- `passed`

**Evidence**

- `logs/approval_log.json`
- `logs/trace.jsonl`
- R3 capability output

## R4 - Standing Instructions

**Tier:** C  
**Claim:** Persists user preferences across process restarts and demonstrates successful reload of stored instructions.

**Command**

```bash
python demo.py --cap R4
```

**Observable result**

The capability returns:

- `preference_count=2`
- `restart_persistence_verified=true`
- `passed=true`

Verified stored preferences:

- m041: No meetings before 11:00 AM
- m015: CC Priya on legal correspondence from Hartwell &amp; Cho

### Verified Preference Demonstration

Stored Preference

m041
No meetings before 11:00 AM
s
Effect

Any future meeting response proposed before
11:00 AM must be reviewed against this
standing preference before commitment.


**Evidence**

- `data/preferences.json`
- `logs/trace.jsonl`
- R4 capability output

## R5 - Hostile Inbox Protection

**Tier:** C  
**Claim:** Detects prompt injections and phishing attempts, refuses them, flags them, and reports them to the user.

**Command**

```bash
python demo.py --cap R5
```

**Observable result**

The capability reports hostile findings including:

- m017 as `PROMPT_INJECTION`
- m023 as `PHISHING`

Both are refused and flagged. The messages remain in the mailbox and no attacker-requested action is written to the outbox.

**Evidence**

- `logs/trace.jsonl`
- `logs/security_log.json`
- R5 capability output

## R6 - Dashboard

**Tier:** C  
**Claim:** Generates a reproducible three-pane dashboard containing pending actions, flagged items, and commitments with conflicts surfaced.

**Command**

```bash
python demo.py --cap R6
```

**Observable result**

The command writes `dashboard/dashboard.html` with exactly three panes:

1. Pending Actions
2. Flagged
3. Commitments

The Commitments pane includes a Launch Week Release commitment derived from source messages m026 and m036. Message m026 establishes the launch target as the 20th, and m036 confirms that the 20th remains a hard date.

The dashboard also surfaces the scheduling conflict between:

- m010: Intro call this week?
- m061: Reminder: your appointment on Sep 15
- Conflict time: `2026-09-15T15:00:00`

**Evidence**

- `dashboard/dashboard.html`
- R6 capability output

# Custom Capabilities

## X1 - Daily Digest

**Tier:** A  
**Claim:** Produces a deterministic digest summarizing follow-ups, flagged items, commitments, and conflicts.

**Command**

```bash
python demo.py --cap X1
```

**Observable result**

- `followups_found=9`
- `flagged_count=2`
- `commitments_found=5`
- `conflicts_found=1`

The output also includes a concise deterministic summary and calls out that human review is required for commitment conflicts.

**Evidence**

- X1 capability output

## X2 - Follow-up Tracker

**Tier:** B  
**Claim:** Tracks actionable follow-up work using disposition metadata and excludes unresolved `fallback_pending` items.

**Command**

```bash
python demo.py --cap X2
```

**Observable result**

The capability returns nine meaningful follow-up items. It includes rule-based `REPLY`, `ESCALATE`, and actionable `DEFER` messages while excluding messages that only await fallback model classification.

Verified examples include:

- m038: Board review scheduled
- m010: Intro call this week?
- m061: Reminder: your appointment on Sep 15
- m086: Your Calendly event was scheduled
- m095: Your flight check-in is open
- m117: Reminder: submit your timesheet

**Evidence**

- X2 capability output

## X3 - Thread Summarizer

**Tier:** B  
**Claim:** Summarizes message threads, identifies open questions and action items, preserves source message IDs, and validates summary safety.

**Command**

```bash
python demo.py --cap X3 --msg m008
```

**Observable result**

The capability returns:

- `thread_id=t-api`
- source message IDs m001, m003, m005, and m008
- policy validation status
- a safe replacement summary

Because the thread contains a credential-bearing connection string, the unsafe generated summary is discarded and `policy_allowed=false` is reported.

**Evidence**

- X3 capability output

## X4 - Explain Decision

**Tier:** C  
**Claim:** Explains why a disposition was assigned using the stored category, disposition reason, processing source, and model requirement metadata.

**Command**

```bash
python demo.py --cap X4 --msg m010
```

**Observable result**

The capability returns:

- `category=meeting`
- `disposition=REPLY`
- `handled_by=rule`
- `model_required=false`
- the original stored explanation
- `passed=true`

**Evidence**

- X4 capability output

## X5 - Commitment Conflict Planner

**Tier:** C  
**Claim:** Detects commitment conflicts and produces deterministic planning guidance requiring human review.

**Command**

```bash
python demo.py --cap X5
```

**Observable result**

The capability returns one conflict:

- m010: Intro call this week?
- m061: Reminder: your appointment on Sep 15
- Conflict time: `2026-09-15T15:00:00`
- Recommendation: Human review required. Two commitments occur at the same time.

The planner does not automatically choose a winner or modify any calendar data.

**Evidence**

- X5 capability output
- `data/commitments.json`

# Capability Tier Coverage

InboxHero includes at least one custom capability at every required tier:

- Tier A: X1 Daily Digest
- Tier B: X2 Follow-up Tracker and X3 Thread Summarizer
- Tier C: X4 Explain Decision and X5 Commitment Conflict Planner

# Multi-Message Commitment Evidence

The Launch Week Release commitment derives from multiple messages in the `t-launch` thread:

- m026 establishes the launch target as the 20th.
- m036 confirms that the 20th remains a hard date and that press has been briefed.

The commitment is resolved to a single Launch Week Release entry and cites both source message IDs: m026 and m036.

# Security and Grounding Guarantees

InboxHero applies these constraints across capabilities:

- Inbox content is treated as untrusted data.
- Prompt injection and phishing detection occur before hostile content can influence actions.
- Generated replies and summaries retain source message IDs.
- Generated content passes deterministic policy validation.
- Credential-bearing URLs, passwords, tokens, API keys, and secrets are blocked.
- Unsafe LLM output is discarded and replaced with a safe deterministic fallback.
- Real email is never sent.
- Drafts are written only to `outbox/`.
- Irreversible sending remains behind the approval boundary.

# Reproducibility

Every capability listed above runs independently through the command shown in its section. The commands were validated through the final `demo.py` dispatcher. The machine-readable source of truth is `capabilities.json`.
