import os
import re
from typing import Generic, Type, TypeVar

from langchain_groq import ChatGroq
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def cleaned_excerpt(text: str, max_chars: int) -> str:
    normalized = re.sub(r"\s+", " ", (text or "")).strip()
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[:max_chars]}..."


class StructuredGroqClient(Generic[T]):
    def __init__(self, output_model: Type[T], temperature: float):
        api_key = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL", "qwen-2.5-32b")

        self._chain = None
        if api_key:
            llm = ChatGroq(model=model, api_key=api_key, temperature=temperature)
            self._chain = llm.with_structured_output(output_model)

    async def invoke(self, prompt: str) -> T:
        if self._chain is None:
            raise RuntimeError("GROQ_API_KEY is not configured.")
        return await self._chain.ainvoke(prompt)
