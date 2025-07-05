from app.core.database import Base
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    amount_owed = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False)
    split_method = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bill = relationship("Bill", back_populates="expenses")
    user = relationship("User")