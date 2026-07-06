from .client import chroma_client


def user_collection(user_id: str):
    return chroma_client.get_or_create_collection(name=f"user_docs_{user_id}")
