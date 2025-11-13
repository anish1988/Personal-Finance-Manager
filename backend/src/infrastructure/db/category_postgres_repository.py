from src.domain.repositories.category_repository import CategoryRepository
from src.domain.entities.category import Category
from infrastructure.db.models import Category as CategoryModel, Transaction as TransactionModel
from sqlalchemy.orm import Session

class PostgresCategoryRepository(CategoryRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, category: Category) -> Category:
        db_cat = CategoryModel(name=category.name)
        self.db.add(db_cat)
        self.db.commit()
        self.db.refresh(db_cat)
        return Category(id=db_cat.id, name=db_cat.name)

    def list_all(self, user_id: int | None = None):
        result = self.db.query(CategoryModel).all()
        return [Category(id=c.id, name=c.name) for c in result]

    def get_by_name(self, name: str, user_id: int | None = None):
        cat = self.db.query(CategoryModel).filter(CategoryModel.name == name).first()
        if cat:
            return Category(id=cat.id, name=cat.name)
        return None

    def delete(self, category_id: int) -> bool:
        # Prevent delete if linked to transactions
        linked = self.db.query(TransactionModel).filter(TransactionModel.category_id == category_id).first()
        if linked:
            return False
        category = self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category:
            return False
        self.db.delete(category)
        self.db.commit()
        return True
