# backend/src/domain/entities/transaction.py
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class Transaction:
    id: Optional[int]
    user_id: int
    tx_date: date
    amount: float
    currency: str
    transaction_type: str  # 'income' or 'expense'
    description: Optional[str] = None
    category_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
