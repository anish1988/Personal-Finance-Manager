from sqlalchemy.orm import Session
from infrastructure.db.models import Transaction as TransactionModel
from src.infrastructure.ai.insight_analyzer import InsightAnalyzer

class AIInsightService:
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = InsightAnalyzer()

    def generate_insights(self, user_id: int | None = None):
        query = self.db.query(TransactionModel)
        if user_id:
            query = query.filter(TransactionModel.user_id == user_id)
        transactions = [
            {
                "tx_date": t.tx_date,
                "description": t.description or "",
                "amount": float(t.amount),
                "currency": t.currency,
                "transaction_type": t.transaction_type,
            }
            for t in query.all()
        ]
        if not transactions:
            return {"insight": "No transactions available for analysis."}
        insights = self.analyzer.analyze(transactions)
        return {"insight": insights}
