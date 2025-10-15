"""
LLM Client for contract data extraction
Supports both OpenAI and Anthropic APIs
"""

from typing import Optional
from app.config import settings


class LLMClient:
    def __init__(self):
        self.use_openai = bool(settings.OPENAI_API_KEY)
        self.use_anthropic = bool(settings.ANTHROPIC_API_KEY)
        self.use_gemini = bool(settings.GEMINI_API_KEY)

        if self.use_openai:
            from openai import OpenAI

            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        elif self.use_anthropic:
            from anthropic import Anthropic

            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        elif self.use_gemini:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_client = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            raise ValueError(
                "Either OPENAI_API_KEY or ANTHROPIC_API_KEY or GEMINI_API_KEY must be set"
            )

    def extract_data(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Send extraction prompt to LLM and get structured response
        """
        if self.use_openai:
            return self._extract_with_openai(prompt, max_tokens)
        elif self.use_anthropic:
            return self._extract_with_anthropic(prompt, max_tokens)
        elif self.use_gemini:
            return self._extract_with_gemini(prompt, max_tokens)
        else:
            raise ValueError(
                "Either OPENAI_API_KEY or ANTHROPIC_API_KEY or GEMINI_API_KEY must be set"
            )

    def _extract_with_openai(self, prompt: str, max_tokens: int) -> str:
        """Use OpenAI API for extraction"""
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a contract analysis expert. Extract structured data from contracts and return only valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.1,  # Low temperature for consistent extraction
                response_format={"type": "json_object"},  # Ensure JSON response
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _extract_with_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Use Anthropic Claude API for extraction"""
        try:
            response = self.anthropic_client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def _extract_with_gemini(self, prompt: str, max_tokens: int) -> str:
        try:
            response = self.gemini_client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": max_tokens,
                },
            )
            print("LLM raw response:\n", response)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
