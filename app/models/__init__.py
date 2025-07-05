from app.core.database import Base
from sqlalchemy import Column, Integer,ForeignKey, Table

bill_participants = Table(
    "bill_participants",
    Base.metadata,
    Column("bill_id", Integer, ForeignKey("bills.id")),
    Column("user_id", Integer, ForeignKey("users.id"))
)