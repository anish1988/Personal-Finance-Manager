from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from api.dependencies import get_db, get_current_user
from domain.services.transaction_service import TransactionService
from infrastructure.db.transacrion_postgres_repository import TransactionPostgresRepository
from api.schemas.transaction import TransactionCreateRequest, TransactionResponse
from domain.entities.transaction import Transaction as DomainTransaction

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreateRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    repo = TransactionPostgresRepository(db)
    svc = TransactionService(repo)
    tx = DomainTransaction(
        id=None,
        user_id=current_user.id,
        tx_date=payload.tx_date,
        amount=payload.amount,
        currency=payload.currency,
        transaction_type=payload.transaction_type,
        description=payload.description,
        category_id=payload.category_id
    )
    try:
        created = svc.create_transaction(tx)
        return TransactionResponse(
            id=created.id,
            tx_date=created.tx_date,
            amount=created.amount,
            currency=created.currency,
            transaction_type=created.transaction_type,
            description=created.description,
            category_id=created.category_id,
            created_at=created.created_at.isoformat() if created.created_at else None
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None, alias="type"),
    category_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user = Depends(get_current_user)
):
    repo = TransactionPostgresRepository(db)
    svc = TransactionService(repo)

    # convert dates if present
    from datetime import datetime
    fd = datetime.strptime(from_date, "%Y-%m-%d").date() if from_date else None
    td = datetime.strptime(to_date, "%Y-%m-%d").date() if to_date else None

    results = svc.list_transactions(current_user.id, fd, td, transaction_type, category_id, page, page_size)
    out = []
    for m in results:

        tx_date = getattr(m, "tx_date", None) or getattr(m, "date", None)
        tx_type = getattr(m, "transaction_type", None) or getattr(m, "type", None)
        created_at = getattr(m, "created_at", None)

        out.append(TransactionResponse(
            id=m.id,
            tx_date=tx_date,
            amount=float(m.amount) if m.amount is not None else None,
            currency=getattr(m, "currency", None),
            transaction_type=tx_type,
            description=getattr(m, "description", None),
            category_id=getattr(m, "category_id", None),
            created_at=created_at,
        ))
    return out
