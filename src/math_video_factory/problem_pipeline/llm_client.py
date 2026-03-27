from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI


class LLMClient:
    def __init__(self, model: str = "gpt-5.4-mini") -> None:
        self.client = OpenAI()
        self.model = model

    def generate_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
        text = self._response_text(response)
        return self.extract_json(text)

    @staticmethod
    def _response_text(response: Any) -> str:
        text = getattr(response, "output_text", None)
        if isinstance(text, str) and text.strip():
            return text
        return str(response)

    @staticmethod
    def extract_json(raw: str) -> dict[str, Any]:
        raw = raw.strip()

        if raw.startswith("```"):
            fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
            if fenced:
                raw = fenced.group(1)

        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("JSON 객체를 찾지 못했습니다.")

        candidate = raw[start : end + 1]
        return json.loads(candidate)
