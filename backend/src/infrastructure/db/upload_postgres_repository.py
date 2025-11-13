# backend/src/infrastructure/db/upload_postgres_repository.py
from infrastructure.db.models import UploadTransactionPreview, Transaction as TransactionModel, Upload, UploadFile #import Upload, UploadFile
from infrastructure.db.models import UploadTransactionPreview, Category as CategoryModel, Transaction as TransactionModel
from domain.entities.transaction import Transaction as DomainTransaction
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import Session

class UploadPostgresRepository:
    def __init__(self, db: Session):
        self.db = db

    # transactional: create object and flush (does not commit)
    def create_upload_obj(self, user_id: int, bank_name: str | None, account_type: str | None,
                          statement_month: str | None, original_filename: str | None, storage_path: str | None) -> Upload:
        upload = Upload(
            user_id=user_id,
            bank_name=bank_name,
            account_type=account_type,
            statement_month=statement_month,
            status="uploaded",
            original_filename=original_filename,
            storage_path=storage_path
        )
        self.db.add(upload)
        self.db.flush()   # assigns upload.id in this transaction/session
        return upload

    # convenience wrapper that commits immediately (keeps old API)
    def create_upload(self, *args, **kwargs) -> Upload:
        upload = self.create_upload_obj(*args, **kwargs)
        self.db.commit()
        self.db.refresh(upload)
        return upload

    # transactional: add file record without commit (defensive: ensure parent exists)
    def add_file_record_obj(self, upload_id: int, filename: str, storage_path: str,
                            size_bytes: int | None = None, mime_type: str | None = None) -> UploadFile:
        parent = self.db.query(Upload).filter(Upload.id == upload_id).first()
        if not parent:
            raise ValueError(f"Parent upload id={upload_id} not found")
        f = UploadFile(
            upload_id=upload_id,
            filename=filename,
            size_bytes=size_bytes,
            mime_type=mime_type,
            storage_path=storage_path
        )
        self.db.add(f)
        self.db.flush()
        return f

    # convenience wrapper that commits immediately (keeps old API)
    def add_file_record(self, *args, **kwargs) -> UploadFile:
        f = self.add_file_record_obj(*args, **kwargs)
        self.db.commit()
        self.db.refresh(f)
        return f

    def set_upload_status(self, upload_id: int, status: str):
        u = self.db.query(Upload).filter(Upload.id == upload_id).first()
        if not u:
            return None
        u.status = status
        self.db.commit()
        self.db.refresh(u)
        return u

    def get_upload_files(self, upload_id: int):
        return self.db.query(UploadFile).filter(UploadFile.upload_id == upload_id).all()
    

    def save_preview_row(self, upload_id:int, row: dict) -> UploadTransactionPreview:
        """
        row dict contains: tx_date (date or str), raw_description, raw_amount, currency, raw_credit_debit
        """
        p = UploadTransactionPreview(
            upload_id=upload_id,
            tx_date=row.get("tx_date"),
            raw_description=row.get("raw_description"),
            raw_amount=row.get("raw_amount"),
            currency=row.get("currency"),
            raw_credit_debit=row.get("raw_credit_debit"),
            suggested_category=row.get("suggested_category"),
            suggested_transaction_type=row.get("suggested_transaction_type"),
            suggested_upi_id=row.get("suggested_upi_id")
        )
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def list_preview_rows(self, upload_id:int):
        return self.db.query(UploadTransactionPreview).filter(UploadTransactionPreview.upload_id==upload_id).all()

    def update_preview_row(self, preview_id:int, updates:dict):
        p = self.db.query(UploadTransactionPreview).filter(UploadTransactionPreview.id==preview_id).first()
        if not p:
            return None
        for k,v in updates.items():
            setattr(p,k,v)
        self.db.commit()
        self.db.refresh(p)
        return p

    def mark_preview_processed(self, preview_id:int, llm_result:dict):
        p = self.db.query(UploadTransactionPreview).filter(UploadTransactionPreview.id==preview_id).first()
        if not p:
            return None
        p.processed = True
        p.processed_at = datetime.utcnow()
        p.llm_result = llm_result
        self.db.commit()
        self.db.refresh(p)
        return p

    def insert_transaction_from_preview(self, preview: UploadTransactionPreview, user_id:int):
        """
        convert preview -> TransactionModel (your canonical model) and insert
        """
        tx = TransactionModel(
            user_id = user_id,
            tx_date = preview.tx_date,
            amount = preview.raw_amount if preview.raw_amount is not None else 0,
            currency = preview.currency or "INR",
            transaction_type = preview.suggested_transaction_type or "expense",
            description = preview.raw_description or "",
            category_id = None,  # you can map LLM category to category_id if exists
            created_at = func.now(),
            source_upload_id = preview.upload_id
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def list_unprocessed_preview_rows(self, upload_id:int):
        return self.db.query(UploadTransactionPreview).filter(UploadTransactionPreview.upload_id==upload_id, UploadTransactionPreview.processed==False).order_by(UploadTransactionPreview.id).all()

    def get_or_create_category_id(self, category_name: str, user_id: int = None):
        if not category_name:
            return None
        # try case-insensitive match
        cat = self.db.query(CategoryModel).filter(func.lower(CategoryModel.name) == category_name.lower()).first()
        if cat:
            return cat.id
        # create a new global category
        new = CategoryModel(name=category_name)
        self.db.add(new)
        self.db.commit()
        self.db.refresh(new)
        return new.id

    def insert_transaction_from_preview(self, preview: UploadTransactionPreview, user_id:int, category_id:int = None):
        tx = TransactionModel(
            user_id = user_id,
            tx_date = preview.tx_date or func.current_date(),
            amount = preview.raw_amount or 0.0,
            currency = preview.currency or "INR",
            transaction_type = preview.suggested_transaction_type or "expense",
            description = preview.raw_description or preview.user_comment or "",
            category_id = category_id,
            created_at = func.now(),
            source_upload_id = preview.upload_id
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx