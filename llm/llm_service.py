# LLM Service

"""
Responsibilities:
- Execute prompts against the configured LLM
- Return generated text
- Handle provider errors consistently

Non-responsibilities:
- Prompt construction
- Reply generation
- Thread summarization
- Classification logic
"""

from __future__ import annotations

from config import (
    client,
    MODEL_NAME,
)


class LLMService:
    """
    Thin wrapper around the configured
    Gemini model.

    Prompt in.
    Text out.
    """

    def __init__(
        self,
        model_name: str | None = None,
    ) -> None:

        self.model_name = (
            model_name
            or MODEL_NAME
        )

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Execute a prompt and return text.

        Returns:
            Generated text response.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "Prompt must be a string."
            )

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        try:

            response = (
                client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
            )

            text = getattr(
                response,
                "text",
                "",
            )

            if not isinstance(text, str):
                return ""

            return text.strip()

        except Exception as error:

            raise RuntimeError(
                "LLM generation failed."
            ) from error

