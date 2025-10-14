from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List

from app.models.contact import Contact
from app.models.db import get_session
from app.jwt_auth import get_current_user

router = APIRouter()

# ✅ Create Contact
@router.post("/", response_model=Contact)
def create_contact(contact: Contact, session: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact

# ✅ Get All Contacts (or filter by region/tag)
@router.get("/", response_model=List[Contact])
def get_contacts(
    region: str = None,
    tag: str = None,
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    query = select(Contact)

    if region:
        query = query.where(Contact.region == region)

    if tag:
        query = query.where(Contact.tag == tag)

    contacts = session.exec(query).all()
    return contacts

# ✅ Update Contact
@router.put("/{contact_id}", response_model=Contact)
def update_contact(
    contact_id: int,
    updated_data: Contact,
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(contact, key, value)

    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact

# ✅ Delete Contact
@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    session: Session = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    session.delete(contact)
    session.commit()
    return {"message": "Contact deleted successfully"}
