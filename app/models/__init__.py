from app.core.database import Base
from sqlalchemy import Column, Integer,ForeignKey, Table


bill_participants = Table(
    "bill_participants",
    Base.metadata,
    Column("bill_id", Integer, ForeignKey("bills.id")),
    Column("user_id", Integer, ForeignKey("users.id"))
)

from app.models.user import User
from app.models.bill import Bill
from app.models.expense import Expense

__all__ = ["User", "Bill", "Expense", "bill_participants", "Base"]