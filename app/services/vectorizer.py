import openai
import numpy as np
from sqlmodel import select
from datetime import datetime
from app.config import settings
from app.models.db import Session, engine
from app.models.knowledge import KnowledgeBaseFile
from app.models.knowledge_chunk import KnowledgeChunk

openai.api_key = settings.OPENAI_API_KEY

# ----------------------------
# Text Chunking Parameters
# ----------------------------
CHUNK_SIZE = 500  # character-based chunking (can convert to token-based later)

def chunk_text(text: str, size: int = CHUNK_SIZE):
    """
    Split raw text into fixed-size chunks for vectorization.
    """
    return [text[i:i+size] for i in range(0, len(text), size)]


# ----------------------------
# Embedding Generation
# ----------------------------
def embed_text(text: str) -> list[float]:
    """
    Get OpenAI embedding vector for the given chunk of text.
    """
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response["data"][0]["embedding"]


# ----------------------------
# File Vectorization Logic
# ----------------------------
def process_and_vectorize_file(file_id: int):
    """
    Given a file ID, read and chunk the file,
    generate embeddings for each chunk, and store them in DB.
    """
    with Session(engine) as session:
        file = session.exec(
            select(KnowledgeBaseFile).where(KnowledgeBaseFile.id == file_id)
        ).first()

        if not file:
            print(f"[❌] File ID {file_id} not found.")
            return

        try:
            with open(file.file_path, "r", encoding="utf-8") as f:
                full_text = f.read()
        except Exception as e:
            print(f"[❌] Failed to read file: {e}")
            return

        chunks = chunk_text(full_text)

        for chunk in chunks:
            try:
                vector = embed_text(chunk)
                record = KnowledgeChunk(
                    file_id=file_id,
                    chunk_text=chunk,
                    embedding=vector,  # list[float] stored as JSON (thanks to SQLModel)
                    created_at=datetime.utcnow()
                )
                session.add(record)
            except Exception as e:
                print(f"[❌] Embedding failed: {e}")

        session.commit()
        print(f"[✅] Vectorization complete for File ID {file_id}")


# ----------------------------
# Semantic Search Support
# ----------------------------
def get_embedding(text: str) -> list:
    """
    Embed a user query string using OpenAI.
    """
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']


def cosine_similarity(a: list, b: list) -> float:
    """
    Compute cosine similarity between two embedding vectors.
    """
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
