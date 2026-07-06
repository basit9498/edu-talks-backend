from langchain_core.messages import HumanMessage, AIMessage


class MessageMapper:
    @staticmethod
    def to_langchain(messages):
        if messages is None or len(messages) < 1:
            return []
        result = []
        for msg in messages:
            if msg.role == "user":
                result.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                result.append(AIMessage(content=msg.content))
        return result
