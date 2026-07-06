from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from typing import AsyncGenerator
from app.config import settings


class ChatModel:

    def __init__(
        self,
        repo_id: str,
        task: str = "text-generation",
        temperature: float = 0.7,
        # max_new_tokens: int = 1024,
    ):
        self.repo_id = repo_id
        self.task = task
        self.temperature = temperature
        # self.max_new_tokens = max_new_tokens

        self._initialize_model()

    def _initialize_model(self):
        self._llm = HuggingFaceEndpoint(
            repo_id=self.repo_id,
            task=self.task,
            temperature=self.temperature,
            # max_new_tokens=self.max_new_tokens,
            huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN,
        )
        self._chat_model = ChatHuggingFace(llm=self._llm)

    def reinitialize(
        self,
        repo_id: str = None,
        task: str = None,
        temperature: float = None,
        # max_new_tokens: int = None,
    ):
        if repo_id:
            self.repo_id = repo_id
        if task:
            self.task = task
        if temperature:
            self.temperature = temperature
        # if max_new_tokens:
        #     self.max_new_tokens = max_new_tokens

        self._initialize_model()

    def invoke(self, prompt):
        return self._chat_model.invoke(prompt)

        # 🔹 NEW: Streaming (THIS IS THE KEY)

    async def astream(self, prompt) -> AsyncGenerator[str, None]:
        async for chunk in self._chat_model.astream(prompt):
            if chunk.content:
                yield chunk.content
