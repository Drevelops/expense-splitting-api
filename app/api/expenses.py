from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models import User, Bill, Expense
from app.models.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseResponseWithRelations, SplitMethod

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense entry"""
    # Verify bill exists
    bill = db.query(Bill).filter(Bill.id == expense.bill_id).first()
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    # Verify user exists
    user = db.query(User).filter(User.id == expense.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify user is a participant in the bill
    if user not in bill.participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a participant in this bill"
        )
    
    # Create expense
    db_expense = Expense(
        bill_id=expense.bill_id,
        user_id=expense.user_id,
        amount_owed=expense.amount_owed,
        amount_paid=expense.amount_paid,
        split_method=expense.split_method
    )
    
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.get("/bill/{bill_id}", response_model=List[ExpenseResponseWithRelations])
def get_expenses_by_bill(bill_id: int, db: Session = Depends(get_db)):
    """Get all expenses for a specific bill"""
    # Verify bill exists
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    expenses = db.query(Expense).filter(Expense.bill_id == bill_id).all()
    return expenses

@router.get("/{expense_id}", response_model=ExpenseResponseWithRelations)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get a specific expense by ID"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, expense_update: ExpenseUpdate, db: Session = Depends(get_db)):
    """Update an expense"""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Update only provided fields
    update_data = expense_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_expense, field, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.post("/bill/{bill_id}/split", response_model=List[ExpenseResponse])
def split_bill_expenses(
    bill_id: int, 
    split_method: SplitMethod = SplitMethod.EQUAL,
    custom_amounts: dict = None,
    db: Session = Depends(get_db)
):
    """
    Split a bill among participants and create expense entries
    
    - equal: Split total amount equally among all participants
    - exact: Use custom_amounts dict {user_id: amount}
    - percentage: Use custom_amounts dict {user_id: percentage} (must sum to 100)
    """
    # Get bill with participants
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    if not bill.participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bill has no participants to split among"
        )
    
    # Delete existing expenses for this bill
    db.query(Expense).filter(Expense.bill_id == bill_id).delete()
    
    expenses = []
    
    if split_method == SplitMethod.EQUAL:
        # Equal split
        amount_per_person = bill.total_amount / len(bill.participants)
        for participant in bill.participants:
            expense = Expense(
                bill_id=bill_id,
                user_id=participant.id,
                amount_owed=round(amount_per_person, 2),
                amount_paid=0.0,
                split_method=split_method
            )
            db.add(expense)
            expenses.append(expense)
    
    elif split_method == SplitMethod.EXACT:
        # Exact amounts
        if not custom_amounts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_amounts required for exact split method"
            )
        
        # Verify all participants have amounts and sum equals total
        participant_ids = {p.id for p in bill.participants}
        provided_ids = set(map(int, custom_amounts.keys()))
        
        if participant_ids != provided_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide exact amounts for all participants"
            )
        
        total_custom = sum(custom_amounts.values())
        if abs(total_custom - bill.total_amount) > 0.01:  # Allow small rounding differences
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Custom amounts sum ({total_custom}) must equal bill total ({bill.total_amount})"
            )
        
        for participant in bill.participants:
            amount = custom_amounts[str(participant.id)]
            expense = Expense(
                bill_id=bill_id,
                user_id=participant.id,
                amount_owed=round(amount, 2),
                amount_paid=0.0,
                split_method=split_method
            )
            db.add(expense)
            expenses.append(expense)
    
    elif split_method == SplitMethod.PERCENTAGE:
        # Percentage split
        if not custom_amounts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_amounts required for percentage split method"
            )
        
        # Verify percentages sum to 100
        total_percentage = sum(custom_amounts.values())
        if abs(total_percentage - 100) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Percentages must sum to 100, got {total_percentage}"
            )
        
        participant_ids = {p.id for p in bill.participants}
        provided_ids = set(map(int, custom_amounts.keys()))
        
        if participant_ids != provided_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide percentages for all participants"
            )
        
        for participant in bill.participants:
            percentage = custom_amounts[str(participant.id)]
            amount = (percentage / 100) * bill.total_amount
            expense = Expense(
                bill_id=bill_id,
                user_id=participant.id,
                amount_owed=round(amount, 2),
                amount_paid=0.0,
                split_method=split_method
            )
            db.add(expense)
            expenses.append(expense)
    
    db.commit()
    for expense in expenses:
        db.refresh(expense)
    
    return expenses

@router.put("/{expense_id}/payment", response_model=ExpenseResponse)
def record_payment(expense_id: int, amount_paid: float, db: Session = Depends(get_db)):
    """Record a payment towards an expense"""
    if amount_paid < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be positive"
        )
    
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Update payment amount
    expense.amount_paid = amount_paid
    
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    db.delete(expense)
    db.commit()
    return None