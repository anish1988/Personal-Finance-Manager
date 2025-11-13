from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, func, Text, Numeric, Boolean
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


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    bank_name = Column(String(128), nullable=True)
    account_type = Column(String(64), nullable=True)  # saving / credit etc
    statement_month = Column(String(20), nullable=True)  # YYYY-MM or user provided
    status = Column(String(32), nullable=False, default="uploaded")  # uploaded|processing|needs_review|done|failed
    original_filename = Column(String(512), nullable=True)
    storage_path = Column(String(1024), nullable=True)  # base folder for files
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    files = relationship("UploadFile", back_populates="upload", cascade="all, delete-orphan")


class UploadFile(Base):
    __tablename__ = "upload_files"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False, index=True)
    filename = Column(String(512), nullable=False)
    size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(128), nullable=True)
    storage_path = Column(String(1024), nullable=True)  # full path to stored file
    parsed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    upload = relationship("Upload", back_populates="files")


class UploadTransactionPreview(Base):
    __tablename__ = "upload_transactions_preview"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    tx_date = Column(Date, nullable=True)
    raw_description = Column(Text, nullable=True)
    raw_amount = Column(Numeric(12,2), nullable=True)
    currency = Column(String(16), nullable=True)
    raw_credit_debit = Column(String(32), nullable=True)
    suggested_category = Column(String(128), nullable=True)
    suggested_transaction_type = Column(String(16), nullable=True)
    suggested_upi_id = Column(String(256), nullable=True)
    user_comment = Column(Text, nullable=True)
    llm_result = Column(JSON, nullable=True)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())