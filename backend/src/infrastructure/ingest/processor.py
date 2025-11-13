# backend/src/infrastructure/ingest/processor.py
import os
import logging
from sqlalchemy.orm import Session
from infrastructure.ingest.parsers import parse_excel, parse_pdf
from infrastructure.db.upload_postgres_repository import UploadPostgresRepository

logger = logging.getLogger("ingest.processor")
logging.basicConfig(level=logging.INFO)

def process_upload(upload_id: int, db: Session):
    """
    Background processing entrypoint.
    - update status -> processing
    - iterate files -> (placeholder) read or call parsers
    - save preview rows later (not implemented here)
    - mark upload as done or failed
    """
    repo = UploadPostgresRepository(db)
    try:
        repo.set_upload_status(upload_id, "processing")
        files = repo.get_upload_files(upload_id)
        for f in files:
            logger.info(f"Processing file {f.filename} at {f.storage_path}")
            # Placeholder: determine file type and call specific parser
            # e.g., if f.filename.endswith('.xlsx'): parse_excel(...)
            # For now we just mark parsed flag in DB
            f.parsed = True
            db.add(f)
            db.commit()
        repo.set_upload_status(upload_id, "needs_review")  # preview stage
    except Exception as e:
        logger.exception("Processing failed")
        repo.set_upload_status(upload_id, "failed")
        raise

def process_upload(upload_id:int, db:Session):
    repo = UploadPostgresRepository(db)
    repo.set_upload_status(upload_id, "processing")
    files = repo.get_upload_files(upload_id)
    for f in files:
        path = f.storage_path
        rows = []
        if path.lower().endswith((".xlsx",".xls")):
            rows = parse_excel(path)
        elif path.lower().endswith(".pdf"):
            rows = parse_pdf(path)
        else:
            # unsupported - skip or mark
            continue
        for row in rows:
            # save preview row
            repo.save_preview_row(upload_id, row)
    # mark upload as needs_review (preview available)
    repo.set_upload_status(upload_id, "needs_review")
