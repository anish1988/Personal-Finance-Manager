from infrastructure.db.models import Transaction as TransactionModel  # ORM model
from domain.entities.transaction import Transaction as DomainTransaction  # domain entity
from domain.repositories.transaction_repository import TransactionRepositoryInterface
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

class TransactionPostgresRepository(TransactionRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(self, tx: DomainTransaction) -> DomainTransaction:
        """
        Create DB record from domain Transaction and return a fully populated DomainTransaction.
        Note: we expect tx.user_id already set from the authenticated user in the route/service.
        """
        # Build ORM model without id (DB will assign it). Map fields from domain tx.
        db_tx = TransactionModel(
            user_id=getattr(tx, "user_id", None),
            tx_date=getattr(tx, "tx_date", None),
            amount=getattr(tx, "amount", None),
            currency=getattr(tx, "currency", "INR"),
            transaction_type=getattr(tx, "transaction_type", None),
            description=getattr(tx, "description", None),
            category_id=getattr(tx, "category_id", None),
        )

        # Persist
        self.db.add(db_tx)
        self.db.commit()
        self.db.refresh(db_tx)  # now db_tx.id, created_at, etc. are populated

        # Build and return a DomainTransaction with all required fields from the DB model
        created = DomainTransaction(
            id=db_tx.id,
            user_id=db_tx.user_id,
            tx_date=db_tx.tx_date,
            amount=float(db_tx.amount) if db_tx.amount is not None else None,
            currency=db_tx.currency,
            transaction_type=db_tx.transaction_type,
            description=db_tx.description,
            category_id=db_tx.category_id,
            created_at=getattr(db_tx, "created_at", None)
        )
        return created

    def list_all(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        tx_type: Optional[str] = None,
        category_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 20,
    ):
        q = self.db.query(TransactionModel)

        if from_date is not None:
            q = q.filter(TransactionModel.tx_date >= from_date)
        if to_date is not None:
            q = q.filter(TransactionModel.tx_date <= to_date)
        if tx_type:
            q = q.filter(TransactionModel.transaction_type == tx_type)
        if category_id is not None:
            q = q.filter(TransactionModel.category_id == category_id)

        q = q.order_by(TransactionModel.tx_date.desc()).offset(offset).limit(limit)
        models = q.all()

        return [
            DomainTransaction(
                id=m.id,
                user_id=m.user_id,
                tx_date=m.tx_date,
                amount=float(m.amount),
                currency=m.currency,
                transaction_type=m.transaction_type,
                description=m.description,
                category_id=m.category_id,
                created_at=getattr(m, "created_at", None),
            )
            for m in models
        ]

    def get_by_id(self, tx_id: int) -> Optional[DomainTransaction]:
        m = self.db.query(TransactionModel).filter(TransactionModel.id == tx_id).first()
        if not m:
            return None
        return DomainTransaction(
            id=m.id,
            amount=m.amount,
            description=m.description,
            category_id=m.category_id,
            created_at=getattr(m, "created_at", None)
        )
    
    def list_for_user(self, user_id: int) -> List[DomainTransaction]:
        """
        Return transactions for a given user. Adjust filter if your TransactionModel
        uses a different column name for user relation (e.g., owner_id).
        """
        models = self.db.query(TransactionModel).filter(getattr(TransactionModel, "user_id") == user_id).all()

        return [
            DomainTransaction(
                id=m.id,
                amount=m.amount,
                description=m.description,
                category_id=m.category_id,
                created_at=getattr(m, "created_at", None),
                # include user_id if your DomainTransaction expects it:
                user_id=getattr(m, "user_id", None)
            )
            for m in models
        ]