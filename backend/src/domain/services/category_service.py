from src.domain.entities.category import Category
from src.domain.repositories.category_repository import CategoryRepository
from fastapi import HTTPException, status

class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    def create_category(self, name: str, user_id: int | None = None) -> Category:
        existing = self.repo.get_by_name(name, user_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
        return self.repo.create(Category(id=None, name=name, user_id=user_id))

    def list_categories(self, user_id: int | None = None):
        return self.repo.list_all(user_id)

    def delete_category(self, category_id: int):
        deleted = self.repo.delete(category_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or linked to transactions")
        return {"message": "Category deleted successfully"}
