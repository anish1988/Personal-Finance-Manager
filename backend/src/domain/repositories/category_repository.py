from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.category import Category

class CategoryRepository(ABC):
    @abstractmethod
    def create(self, category: Category) -> Category:
        pass

    @abstractmethod
    def list_all(self, user_id: int | None = None) -> List[Category]:
        pass

    @abstractmethod
    def delete(self, category_id: int) -> bool:
        pass

    @abstractmethod
    def get_by_name(self, name: str, user_id: int | None = None) -> Optional[Category]:
        pass
