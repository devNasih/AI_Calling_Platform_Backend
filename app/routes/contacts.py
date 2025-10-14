from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import csv
from io import StringIO

from app.models.schemas import ContactUpload, SuccessResponse
from app.jwt_auth import get_current_user

router = APIRouter()

# In-memory storage for MVP (to be replaced by DB later)
contact_store: List[ContactUpload] = []

@router.post("/upload", response_model=SuccessResponse)
async def upload_contacts(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    decoded = content.decode("utf-8")

    if not decoded.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    reader = csv.DictReader(StringIO(decoded))

    count = 0
    for row in reader:
        if "name" not in row or "phone_number" not in row:
            raise HTTPException(status_code=400, detail="CSV must have 'name' and 'phone_number' columns.")

        name = row["name"].strip()
        phone_number = row["phone_number"].strip()

        if not name or not phone_number:
            continue  # skip empty rows

        # Avoid duplicates
        if any(c.phone_number == phone_number for c in contact_store):
            continue

        contact_store.append(ContactUpload(name=name, phone_number=phone_number))
        count += 1

    if count == 0:
        raise HTTPException(status_code=400, detail="No valid contacts found in file.")

    return {"message": f"{count} contacts uploaded successfully."}


@router.get("/all", response_model=List[ContactUpload])
async def get_all_contacts(user: dict = Depends(get_current_user)):
    return contact_store
