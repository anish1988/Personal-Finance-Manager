from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.transaction import Transaction
from datetime import date

class TransactionRepositoryInterface(ABC):
    @abstractmethod
    def create(self, tx: Transaction) -> Transaction:
        pass

    @abstractmethod
    def list_for_user(
        self, user_id: int, from_date: Optional[date]=None, to_date: Optional[date]=None,
        tx_type: Optional[str]=None, category_id: Optional[int]=None, offset: int=0, limit: int=20
    ) -> List[Transaction]:
        pass
