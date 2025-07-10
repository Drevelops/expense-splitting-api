from app.core.database import Base
from app.models import bill_participants
from sqlalchemy import Boolean, Column, Integer, String,Boolean
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  
    is_active = Column(Boolean, default=True)

    bills = relationship("Bill", secondary="bill_participants", back_populates="participants")
    created_bills = relationship("Bill", back_populates="created_by_user")