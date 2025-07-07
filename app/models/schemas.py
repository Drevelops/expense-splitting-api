from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from typing import List
from __future__ import annotations
from enum import Enum

class SplitMethod(str, Enum):
    EQUAL = "equal"
    PERCENTAGE = "percentage"
    EXACT = "exact"
    
class UserBase(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=28)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(min_length=3, default=None)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(min_length=8, max_length=28, default=None)


class UserResponse(UserBase):
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True


class UserResponseWithRelations(UserResponse):
    bills: List[BillResponse] = []  # Bills they participate in
    created_bills: List[BillResponse] = []  # Bills they created
    
    class Config:
        from_attributes = True

class BillBase(BaseModel):
    title: str = Field(min_length=3)
    total_amount: float = Field(gt=0)


class BillCreate(BillBase):
    created_by: int
    participant_ids: Optional[List[int]] = []  


class BillUpdate(BaseModel):
    title: Optional[str] = Field(min_length=3, default=None)
    total_amount: Optional[float] = Field(gt=0, default=None)


class BillResponse(BillBase):
    id: int
    created_by: int
    created_by_user: Optional[UserResponse] = None  
    participants: List[UserResponse] = []
    expenses: List[ExpenseResponse] = []  
    
    class Config:
        from_attributes = True

class ExpenseBase(BaseModel):
    amount_owed: float = Field(ge=0)
    amount_paid: float = Field(ge=0, default=0.0)
    split_method: SplitMethod


class ExpenseCreate(ExpenseBase):
    bill_id: int
    user_id: int


class ExpenseUpdate(BaseModel):
    amount_owed: Optional[float] = Field(ge=0, default=None)
    amount_paid: Optional[float] = Field(ge=0, default=None)
    split_method: Optional[SplitMethod] = None


class ExpenseResponse(ExpenseBase):
    id: int
    bill_id: int
    user_id: int
    
    class Config:
        from_attributes = True


class ExpenseResponseWithRelations(ExpenseResponse):
    bill: Optional[BillResponse] = None
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True