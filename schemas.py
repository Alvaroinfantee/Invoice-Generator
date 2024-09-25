from pydantic import BaseModel
from typing import List, Optional

class ItemCreate(BaseModel):
    description: str
    quantity: int
    unit_price: float

class ItemRead(ItemCreate):
    total_price: float

class InvoiceBase(BaseModel):
    client_name: str
    client_address: str
    invoice_date: str
    due_date: str
    items: List[ItemCreate]

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceRead(InvoiceBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True
