from langchain_text_splitters import RecursiveCharacterTextSplitter


def doc_splitter(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    return chunks
