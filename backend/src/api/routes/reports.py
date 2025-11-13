from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from src.domain.services.reporting_service import ReportingService
from api.dependencies import get_db

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/summary")
def get_summary_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    service = ReportingService(db)
    return service.summary_report(start_date, end_date)

@router.get("/categories")
def get_category_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    service = ReportingService(db)
    return service.category_breakdown(start_date, end_date)
