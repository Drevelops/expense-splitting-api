from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models import User, Bill
from app.models.schemas import BillCreate, BillUpdate, BillResponse

router = APIRouter(prefix="/bills", tags=["bills"])

@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    # Verify creator exists
    creator = db.query(User).filter(User.id == bill.created_by).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator user not found"
        )
    
    # Create the bill
    db_bill = Bill(
        title=bill.title,
        total_amount=bill.total_amount,
        created_by=bill.created_by
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    
    # Add participants if provided
    if bill.participant_ids:
        # Verify all participants exist
        participants = db.query(User).filter(User.id.in_(bill.participant_ids)).all()
        if len(participants) != len(bill.participant_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more participant users not found"
            )
        
        # Add participants to the bill
        db_bill.participants.extend(participants)
        db.commit()
        db.refresh(db_bill)
    
    return db_bill

@router.get("/", response_model=List[BillResponse])
def get_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all bills with pagination"""
    bills = db.query(Bill).offset(skip).limit(limit).all()
    return bills

@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """Get a specific bill by ID"""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    return bill

@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(bill_id: int, bill_update: BillUpdate, db: Session = Depends(get_db)):
    """Update a bill's basic information"""
    db_bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not db_bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    # Update only provided fields
    update_data = bill_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_bill, field, value)
    
    db.commit()
    db.refresh(db_bill)
    return db_bill

@router.post("/{bill_id}/participants", response_model=BillResponse)
def add_participants_to_bill(bill_id: int, participant_ids: List[int], db: Session = Depends(get_db)):
    """Add participants to an existing bill"""
    # Get the bill
    db_bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not db_bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    # Verify all participants exist
    participants = db.query(User).filter(User.id.in_(participant_ids)).all()
    if len(participants) != len(participant_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more participant users not found"
        )
    
    # Check for duplicates (users already participating)
    existing_participant_ids = {p.id for p in db_bill.participants}
    new_participants = [p for p in participants if p.id not in existing_participant_ids]
    
    if not new_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All users are already participants in this bill"
        )
    
    # Add new participants
    db_bill.participants.extend(new_participants)
    db.commit()
    db.refresh(db_bill)
    
    return db_bill

@router.delete("/{bill_id}/participants/{user_id}", response_model=BillResponse)
def remove_participant_from_bill(bill_id: int, user_id: int, db: Session = Depends(get_db)):
    """Remove a participant from a bill"""
    db_bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not db_bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    # Find the participant
    participant = next((p for p in db_bill.participants if p.id == user_id), None)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a participant in this bill"
        )
    
    # Remove the participant
    db_bill.participants.remove(participant)
    db.commit()
    db.refresh(db_bill)
    
    return db_bill

@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    """Delete a bill"""
    db_bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not db_bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    db.delete(db_bill)
    db.commit()
    return None