from langchain_community.embeddings import HuggingFaceEmbeddings
from .collection import user_collection

# embedding_model = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

embedding_model = None


# def ingest_document(*, user_id: str, document_id: str, text: str):
#     collection = user_collection(user_id)

#     existing = collection.get(ids=[document_id])

#     if existing["ids"]:
#         return

#     embedding = embedding_model.embed_documents([text])[0]

#     collection.add(
#         ids=[document_id],
#         documents=[text],
#         metadatas=[{"document_id": document_id}],
#         embeddings=[embedding],
#     )


def ingest_documents(user_id: str, document_id: str, langchain_docs: list):

    collection = user_collection(user_id)

    for idx, doc in enumerate(langchain_docs):
        chunk_id = f"{document_id}_chunk_{idx}"

        # Avoid duplicates
        existing = collection.get(ids=[chunk_id])
        if existing["ids"]:
            continue

        embedding = embedding_model.embed_documents([doc.page_content])[0]

        collection.add(
            ids=[chunk_id],
            documents=[doc.page_content],
            embeddings=[embedding],
            metadatas=[
                {"document_id": document_id, "chunk_index": idx, "user_id": user_id}
            ],
        )


def query_user_documents(user_id: str, document_ids: list, query: str, top_k=5):
    collection = user_collection(user_id)
    query_embedding = embedding_model.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"document_id": {"$in": document_ids}},
    )

    return results["documents"][0] if results["documents"] else []
