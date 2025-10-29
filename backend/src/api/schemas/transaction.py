from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

class TransactionCreateRequest(BaseModel):
    tx_date: date
    amount: float
    currency: Optional[str] = "INR"
    transaction_type: str  # income/expense
    description: Optional[str] = None
    category_id: Optional[int] = None

class TransactionResponse(BaseModel):
    id: int
    tx_date: Optional[date] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    transaction_type: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    created_at: Optional[datetime] = None
