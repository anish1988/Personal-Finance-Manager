from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.infrastructure.db.category_postgres_repository import PostgresCategoryRepository
from src.domain.services.category_service import CategoryService
from api.dependencies import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/")
def create_category(name: str, db: Session = Depends(get_db)):
    repo = PostgresCategoryRepository(db)
    service = CategoryService(repo)
    return service.create_category(name=name)

@router.get("/")
def list_categories(db: Session = Depends(get_db)):
    repo = PostgresCategoryRepository(db)
    service = CategoryService(repo)
    return service.list_categories()

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    repo = PostgresCategoryRepository(db)
    service = CategoryService(repo)
    return service.delete_category(category_id)
