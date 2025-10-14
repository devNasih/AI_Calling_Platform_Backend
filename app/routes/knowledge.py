from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from sqlmodel import Session, select
from datetime import datetime
import os
from typing import List

from app.models.db import engine
from app.models.knowledge import KnowledgeBaseFile, KnowledgeBaseChunk
from app.services.vectorizer import (
    process_and_vectorize_file,
    get_embedding,
    cosine_similarity
)

router = APIRouter()
UPLOAD_DIR = "uploads/knowledge_base"


# ---------------------------
# 📥 Upload Knowledge File
# ---------------------------
@router.post("/upload")
async def upload_knowledge_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    db_file = KnowledgeBaseFile(
        file_name=file.filename,
        file_path=file_path,
        uploaded_at=datetime.utcnow()
    )

    with Session(engine) as session:
        session.add(db_file)
        session.commit()
        session.refresh(db_file)

    return {
        "message": "File uploaded successfully.",
        "file_id": db_file.id
    }


# ---------------------------
# 🔄 Trigger Vectorization
# ---------------------------
@router.post("/vectorize/{file_id}")
def vectorize_file(file_id: int):
    try:
        process_and_vectorize_file(file_id)
        return {"status": "success", "message": f"File {file_id} processed and embedded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# 🔍 Semantic Search
# ---------------------------
@router.get("/search")
def search_knowledge(query: str = Query(..., min_length=3), top_k: int = 5):
    query_embedding = get_embedding(query)

    with Session(engine) as session:
        chunks = session.exec(select(KnowledgeBaseChunk)).all()

        results = []
        for chunk in chunks:
            similarity = cosine_similarity(query_embedding, chunk.embedding)
            results.append({
                "text": chunk.chunk_text,
                "similarity": similarity,
                "file_id": chunk.file_id
            })

    top_results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]
    return {
        "query": query,
        "matches": top_results
    }
