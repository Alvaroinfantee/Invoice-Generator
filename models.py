from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    invoices = relationship("Invoice", back_populates="owner")

    def set_password(self, password):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String)
    client_address = Column(String)
    invoice_date = Column(String)
    due_date = Column(String)
    items = Column(JSON)  # List of items
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="invoices")
