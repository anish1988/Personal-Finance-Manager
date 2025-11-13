# backend/src/api/routes/uploads_preview.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from api.dependencies import get_db, get_current_user, SessionLocal
from infrastructure.db.postgres_repository import UploadPostgresRepository
from infrastructure.ingest.processor_llm import process_preview_rows_llm_batched
from infrastructure.db.models import Upload, UploadTransactionPreview
from pydantic import BaseModel

router = APIRouter(prefix="/uploads", tags=["uploads"])

class PreviewOut(BaseModel):
    id: int
    tx_date: str | None
    raw_description: str | None
    raw_amount: float | None
    suggested_category: str | None
    suggested_transaction_type: str | None
    suggested_upi_id: str | None
    user_comment: str | None
    processed: bool

@router.get("/{upload_id}/preview", response_model=List[PreviewOut])
def get_preview(upload_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    repo = UploadPostgresRepository(db)
    upload = db.query(Upload).filter(Upload.id==upload_id, Upload.user_id==current_user.id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    rows = repo.list_preview_rows(upload_id)
    # convert date -> iso string
    out = []
    for r in rows:
        out.append(PreviewOut(
            id=r.id,
            tx_date=r.tx_date.isoformat() if r.tx_date else None,
            raw_description=r.raw_description,
            raw_amount=float(r.raw_amount) if r.raw_amount is not None else None,
            suggested_category=r.suggested_category,
            suggested_transaction_type=r.suggested_transaction_type,
            suggested_upi_id=r.suggested_upi_id,
            user_comment=r.user_comment,
            processed=r.processed
        ))
    return out

class EditPreviewIn(BaseModel):
    user_comment: str | None = None
    suggested_category: str | None = None

@router.patch("/{upload_id}/preview/{preview_id}", response_model=PreviewOut)
def edit_preview(upload_id:int, preview_id:int, payload: EditPreviewIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    repo = UploadPostgresRepository(db)
    # ensure ownership
    preview = db.query(UploadTransactionPreview).join(Upload).filter(Upload.id==upload_id, Upload.user_id==current_user.id, UploadTransactionPreview.id==preview_id).first()
    if not preview:
        raise HTTPException(status_code=404, detail="Preview row not found")
    updates = {}
    if payload.user_comment is not None:
        updates['user_comment'] = payload.user_comment
    if payload.suggested_category is not None:
        updates['suggested_category'] = payload.suggested_category
    updated = repo.update_preview_row(preview_id, updates)
    return PreviewOut(
        id=updated.id,
        tx_date=updated.tx_date.isoformat() if updated.tx_date else None,
        raw_description=updated.raw_description,
        raw_amount=float(updated.raw_amount) if updated.raw_amount is not None else None,
        suggested_category=updated.suggested_category,
        suggested_transaction_type=updated.suggested_transaction_type,
        suggested_upi_id=updated.suggested_upi_id,
        user_comment=updated.user_comment,
        processed=updated.processed
    )

@router.post("/{upload_id}/process", status_code=202)
def process_now(upload_id:int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    repo = UploadPostgresRepository(db)
    upload = db.query(Upload).filter(Upload.id==upload_id, Upload.user_id==current_user.id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    # add background task that creates its own DB session
    def _bg(u_id:int, user_id:int):
        db_sess = SessionLocal()
        try:
            process_preview_rows_llm_batched(u_id, db_sess, user_id)
        finally:
            db_sess.close()

    background_tasks.add_task(_bg, upload_id, current_user.id)
    repo.set_upload_status(upload_id, "processing")
    return {"upload_id": upload_id, "status": "processing"}
