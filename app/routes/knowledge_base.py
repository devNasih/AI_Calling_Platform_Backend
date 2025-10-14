from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session
from app.models.db import get_session
from app.models.knowledge_base import KnowledgeBaseFile
import os
import shutil
from datetime import datetime

router = APIRouter()

# Allowed file types
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "csv"}
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "knowledge_base")


@router.post("/upload")
def upload_knowledge_doc(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save file to local disk
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save metadata in DB
    record = KnowledgeBaseFile(
        file_name=file.filename,
        file_path=save_path,
        uploaded_at=datetime.utcnow()
    )
    session.add(record)
    session.commit()

    return {
        "status": "success",
        "file_id": record.id,
        "filename": file.filename
    }
