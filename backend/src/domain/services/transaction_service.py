from domain.repositories.transaction_repository import TransactionRepositoryInterface
from domain.entities.transaction import Transaction
from datetime import date
from typing import List, Optional

class TransactionService:
    def __init__(self, repo: TransactionRepositoryInterface):
        self.repo = repo

    def create_transaction(self, tx: Transaction) -> Transaction:
        # validations
        if tx.amount <= 0:
            raise ValueError("Amount must be positive")
        if tx.transaction_type not in ("income", "expense"):
            raise ValueError("transaction_type must be 'income' or 'expense'")
        return self.repo.create(tx)

    def list_transactions(
        self, user_id: int, from_date: Optional[date]=None, to_date: Optional[date]=None,
        tx_type: Optional[str]=None, category_id: Optional[int]=None, page: int=1, page_size: int=20
    ) -> List[Transaction]:
        offset = (page - 1) * page_size
        return self.repo.list_all(from_date, to_date, tx_type, category_id, offset, page_size)
