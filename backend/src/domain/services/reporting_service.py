from datetime import date
from sqlalchemy.orm import Session
from infrastructure.db.models import Transaction as TransactionModel, Category
from fastapi import HTTPException

class ReportingService:
    def __init__(self, db: Session):
        self.db = db

    def summary_report(self, start_date: date | None = None, end_date: date | None = None):
        query = self.db.query(TransactionModel)
        if start_date:
            query = query.filter(TransactionModel.tx_date >= start_date)
        if end_date:
            query = query.filter(TransactionModel.tx_date <= end_date)

        total_income = sum(t.amount for t in query.filter(TransactionModel.transaction_type == "income"))
        total_expense = sum(t.amount for t in query.filter(TransactionModel.transaction_type == "expense"))
        net_balance = total_income - total_expense

        return {
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "net_balance": float(net_balance),
        }

    def category_breakdown(self, start_date: date | None = None, end_date: date | None = None):
        query = self.db.query(TransactionModel, Category).join(Category, Category.id == TransactionModel.category_id)
        if start_date:
            query = query.filter(TransactionModel.tx_date >= start_date)
        if end_date:
            query = query.filter(TransactionModel.tx_date <= end_date)

        category_totals = {}
        for tx, cat in query:
            key = cat.name if cat else "Uncategorized"
            category_totals[key] = category_totals.get(key, 0) + float(tx.amount)

        return category_totals
