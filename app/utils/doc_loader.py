from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "public", "doc")


def doc_loader(file_name: str):
    file_ext = file_name.split(".")[-1].lower()

    file_path = os.path.join(UPLOAD_DIR, file_name)

    loader = None

    if file_ext == "pdf":
        loader = PyPDFLoader(file_path=file_path)

    elif file_ext == "docx":
        loader = UnstructuredWordDocumentLoader(file_path=file_path)

    elif file_ext == "txt":
        loader = TextLoader(file_path=file_path)

    else:
        raise ValueError("Format not founded")

    return loader.load()
