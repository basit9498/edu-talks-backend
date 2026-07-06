from abc import ABC, abstractmethod
from typing import List, Optional


class LLM(ABC):

    @abstractmethod
    def invoke(self, prompt: str) -> str:
        pass

    @abstractmethod
    def llm_with_tool(self, prompt, tools: List):
        """
        Attach tools/functions to the LLM.
        Should return self or a new configured LLM instance.
        """
        pass
