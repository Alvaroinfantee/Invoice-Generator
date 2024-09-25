from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, Base
from models import Invoice, User
from schemas import InvoiceCreate, InvoiceRead, UserCreate, UserRead, ItemCreate, ItemRead
from auth import get_current_user, authenticate_user, create_access_token
from utils import get_db
from invoice_generator import generate_invoice_pdf

app = FastAPI(title="Invoice Generation API")

Base.metadata.create_all(bind=engine)

# Authentication Endpoints

@app.post("/signup", response_model=UserRead)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user_model = User(username=user.username, hashed_password=user.hashed_password)
    user_model.set_password(user.password)
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return user_model

@app.post("/login")
def login(form_data: dict, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data["username"], form_data["password"])
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Invoice Endpoints

@app.post("/invoices", response_model=InvoiceRead)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice_model = Invoice(
        client_name=invoice.client_name,
        client_address=invoice.client_address,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        items=invoice.items,
        user_id=current_user.id
    )
    db.add(invoice_model)
    db.commit()
    db.refresh(invoice_model)
    # Generate PDF
    generate_invoice_pdf(invoice_model)
    return invoice_model

@app.get("/invoices", response_model=List[InvoiceRead])
def read_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).offset(skip).limit(limit).all()
    return invoices

@app.get("/invoices/{invoice_id}", response_model=InvoiceRead)
def read_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.put("/invoices/{invoice_id}", response_model=InvoiceRead)
def update_invoice(invoice_id: int, invoice: InvoiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice_model = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id).first()
    if not invoice_model:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice_model.client_name = invoice.client_name
    invoice_model.client_address = invoice.client_address
    invoice_model.invoice_date = invoice.invoice_date
    invoice_model.due_date = invoice.due_date
    invoice_model.items = invoice.items
    db.commit()
    db.refresh(invoice_model)
    # Regenerate PDF
    generate_invoice_pdf(invoice_model)
    return invoice_model

@app.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(invoice)
    db.commit()
    return {"detail": "Invoice deleted"}

@app.get("/invoices/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    file_path = f"invoices/invoice_{invoice_id}.pdf"
    try:
        return FileResponse(file_path, media_type='application/pdf', filename=f'invoice_{invoice_id}.pdf')
    except Exception:
        raise HTTPException(status_code=404, detail="PDF not found")
