# Prompt Templates

"""
Responsibilities:
- Build prompt strings
- Centralize LLM instructions
- Support reply generation
- Support thread summarization

Non-responsibilities:
- Calling Gemini
- Executing prompts
- Retrieval
- Business logic
"""

from __future__ import annotations

from core.message_model import Message


class PromptTemplates:
    """
    Central repository for InboxHero LLM prompts.
    """

    # --------------------------------------------------
    # R2 - Grounded Reply Generation
    # --------------------------------------------------

    @staticmethod
    def build_reply_prompt(
        current_message: Message,
        source_messages: list[Message],
    ) -> str:
        """
        Grounded reply prompt.

        Must only use information found
        in the provided source messages.
        """

        sources = "\n\n".join(
            (
                f"Message ID: {message.message_id}\n"
                f"Subject: {message.subject}\n"
                f"Body:\n{message.body}"
            )
            for message in source_messages
        )

        return f"""
You are InboxHero.

Task:
Draft a reply using ONLY information
found in the provided source messages.

Requirements:
- Do not invent facts.
- Do not hallucinate information.
- Use only provided sources.
- If information is missing,
  ask for clarification.
- Keep the response professional.

Current Message

Message ID:
{current_message.message_id}

Subject:
{current_message.subject}

Body:
{current_message.body}

Source Messages

{sources}

Provide only the draft reply.
""".strip()

    # --------------------------------------------------
    # Clarification Request
    # --------------------------------------------------

    @staticmethod
    def build_clarification_prompt(
        current_message: Message,
    ) -> str:
        """
        Used when InboxHero cannot
        determine a safe grounded response.
        """

        return f"""
You are InboxHero.

Task:
Draft a clarification request.

Requirements:
- Ask only for information needed.
- Be professional.
- Be concise.
- Do not assume facts.

Message ID:
{current_message.message_id}

Subject:
{current_message.subject}

Body:
{current_message.body}

Provide only the clarification request.
""".strip()

    # --------------------------------------------------
    # Meeting Response
    # --------------------------------------------------

    @staticmethod
    def build_meeting_response_prompt(
        current_message: Message,
        source_messages: list[Message],
    ) -> str:
        """
        Grounded meeting-response prompt.
        """

        sources = "\n\n".join(
            (
                f"Message ID: {message.message_id}\n"
                f"Subject: {message.subject}\n"
                f"Body:\n{message.body}"
            )
            for message in source_messages
        )

        return f"""
You are InboxHero.

Task:
Draft a meeting-related response.

Requirements:
- Use only supplied message content.
- Do not invent dates, times, or commitments.
- If details are missing, ask for clarification.
- Keep the tone professional.

Current Message

Message ID:
{current_message.message_id}

Subject:
{current_message.subject}

Body:
{current_message.body}

Source Messages

{sources}

Provide only the draft response.
""".strip()

    # --------------------------------------------------
    # X3 - Thread Summarizer
    # --------------------------------------------------

    @staticmethod
    def build_thread_summary_prompt(
        thread_messages: list[Message],
    ) -> str:
        """
        Thread summarization prompt.
        """

        thread_text = "\n\n".join(
            (
                f"Message ID: {message.message_id}\n"
                f"Subject: {message.subject}\n"
                f"Body:\n{message.body}"
            )
            for message in thread_messages
        )

        return f"""
You are InboxHero.

Task:
Summarize the thread.

Requirements:
- Summarize key discussion points.
- Identify decisions made.
- Identify open questions.
- Do not invent information.
- Use only supplied messages.

Thread Messages

{thread_text}

Return:

Summary:
Open Questions:
Action Items:
""".strip()
