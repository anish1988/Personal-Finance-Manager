# backend/src/api/routes/uploads.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
import os
from typing import List
from api.dependencies import get_db, get_current_user
from infrastructure.db.upload_postgres_repository import UploadPostgresRepository
from src.config.settings import settings
from infrastructure.ingest.processor import process_upload

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_statement(
    background_tasks: BackgroundTasks,
    bank_name: str = Form(None),
    account_type: str = Form(None),
    statement_month: str = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # basic validation
    if not files or len(files) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided")

    # create storage path
    base_dir = settings.UPLOAD_DIR.rstrip("/")
    user_dir = os.path.join(base_dir, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)

    repo = UploadPostgresRepository(db)
    original_filename = files[0].filename if len(files) > 0 else None

    # Transactional flow: create upload (flush only), create file rows (flush), then commit once
    try:
        upload = repo.create_upload_obj(
            user_id=current_user.id,
            bank_name=bank_name,
            account_type=account_type,
            statement_month=statement_month,
            original_filename=original_filename,
            storage_path=user_dir
        )

        upload_subdir = os.path.join(user_dir, str(upload.id))
        os.makedirs(upload_subdir, exist_ok=True)

        created_files = []
        for f in files:
            filename = f.filename
            safe_path = os.path.join(upload_subdir, filename)
            content = await f.read()
            size_bytes = len(content)
            max_bytes = settings.MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024
            if size_bytes > max_bytes:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File {filename} exceeds max size")

            with open(safe_path, "wb") as fh:
                fh.write(content)

            file_rec = repo.add_file_record_obj(
                upload_id=upload.id,
                filename=filename,
                storage_path=safe_path,
                size_bytes=size_bytes,
                mime_type=f.content_type
            )
            created_files.append(file_rec)

        # commit once for upload + all files
        db.commit()

        # refresh objects for returning
        db.refresh(upload)
        for fr in created_files:
            db.refresh(fr)

    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {str(exc)}")

    # enqueue background processing using a fresh DB session inside the task
    def _bg_task(u_id: int):
        from api.dependencies import SessionLocal
        db_sess = SessionLocal()
        try:
            process_upload(u_id, db_sess)
        finally:
            db_sess.close()

    background_tasks.add_task(_bg_task, upload.id)

    return {"upload_id": upload.id, "status": upload.status}
