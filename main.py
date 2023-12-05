from fastapi import FastAPI, Depends, HTTPException, Request, Form
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import model

app = FastAPI()


origins = ['*']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)


class TransactionBase(BaseModel):
    amount: float
    category: str
    description: str
    is_income: bool
    date: str
    
    
class TransactionModel(TransactionBase):
    id: int
    
    class Config:
        orm_mode = True
        
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    
db_dependency = Annotated[Session, Depends(get_db)]

model.Base.metadata.create_all(bind=engine)



@app.post("/transaction/", response_model=TransactionModel)
async def create_transaction(transaction: TransactionBase, db: db_dependency):
    db_transaction = model.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
    
@app.get("/transaction/", response_model=List[TransactionModel])
async def get_transaction( db: db_dependency, skip: int = 0, limit: int = 100):
    transactions = db.query(model.Transaction).offset(skip).limit(limit).all()
    return transactions
