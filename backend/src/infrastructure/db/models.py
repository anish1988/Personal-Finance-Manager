from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, func, Text, Numeric
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime


Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tx_date = Column(Date, nullable=True)
    amount = Column(Numeric(12,2), nullable=False)
    currency = Column(String(10), nullable=False, default="INR")
    transaction_type = Column(String(32), nullable=True)   # maps to old `type`
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # relationships
    user = relationship("User", back_populates="transactions", foreign_keys=[user_id])
    category = relationship("Category", back_populates="transactions", foreign_keys=[category_id])


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, nullable=True)

    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)   # canonical name
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # optional relationship: user.transactions if you want bi-directional nav
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")



