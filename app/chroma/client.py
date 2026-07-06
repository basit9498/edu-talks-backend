import chromadb

import os


BASE_DIR = os.getcwd()
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_data")

os.makedirs(CHROMA_DIR, exist_ok=True)


# chroma_client = chromadb.Client(
#     chromadb.config.Settings(persist_directory=CHROMA_DIR, anonymized_telemetry=False)
# )


chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
