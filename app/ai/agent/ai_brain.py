from langchain_groq import ChatGroq
from app.ai.core.ai_interface import LLM
from app.config import settings
from typing import List


class GrokModel(LLM):
    def __init__(
        self,
        model: str = "openai/gpt-oss-120b",
        temperature: float = 0.5,
    ):
        self.model = ChatGroq(
            model=model, temperature=temperature, api_key=settings.GROQ_API_KEY
        )

    def invoke(self, prompt: str):
        return self.model.invoke(prompt)

    def llm_with_tool(self, prompt, tools: List):
        tool_llm = self.model.bind_tools(tools=tools)
        return tool_llm.invoke(prompt)


class AIBrainModal:
    def __init__(self, llm: LLM):
        self._llm = llm

    def invoke(self, prompt: str) -> str:
        return self._llm.invoke(prompt=prompt)

    def llm_with_tools_invoke(self, prompt, tools: List):
        return self._llm.llm_with_tool(prompt=prompt, tools=tools)
