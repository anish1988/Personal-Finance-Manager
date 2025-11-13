from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.dependencies import get_db
from src.domain.services.ai_insight_service import AIInsightService

router = APIRouter(prefix="/ai", tags=["AI Insights"])

@router.get("/insights")
def get_ai_insights(db: Session = Depends(get_db)):
    service = AIInsightService(db)
    return service.generate_insights()
