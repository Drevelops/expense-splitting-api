from app.core.database import Base
from app.models import bill_participants
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    total_amount = Column(Float)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    created_by_user = relationship("User", foreign_keys=[created_by])
    expenses = relationship("Expense", back_populates="bill")
    participants = relationship("User", secondary="bill_participants", back_populates="bills")
