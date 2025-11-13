# backend/src/infrastructure/ingest/processor_llm.py
from domain.services.jwt_service import JWTService  # not needed here
from sqlalchemy.orm import Session
from infrastructure.db.postgres_repository import UploadPostgresRepository
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

import os, json, time, logging
from typing import List, Dict
from config.settings import settings

logger = logging.getLogger("processor_llm")
logging.basicConfig(level=logging.INFO)



# LangChain imports (optional; if not installed you can rely on mock)
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.output_parsers import PydanticOutputParser
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except Exception:
    LANGCHAIN_AVAILABLE = False

# Pydantic schema used for robust parsing
if LANGCHAIN_AVAILABLE:
    class LLMOut(BaseModel):
        category: str = Field(..., description="Category name")
        transaction_type: str = Field(..., description="'income' or 'expense'")
        upi_id: str | None = None
        normalized_description: str
        confidence: float = Field(..., ge=0.0, le=1.0)

    LLM_PARSER = PydanticOutputParser(pydantic_object=LLMOut)

PROMPT = """You are a JSON extractor for bank transactions.
For the transaction below produce ONLY JSON matching the schema:
{{
  "category":"one of: Groceries, Restaurants, Transport, Fuel, Rent, Utilities, Shopping, Healthcare, Entertainment, Income, Others",
  "transaction_type":"income|expense",
  "upi_id": "<upi or null>",
  "normalized_description": "<short merchant name>",
  "confidence": 0.0-1.0
}}
Transaction:
date: {tx_date}
amount: {raw_amount}
description: {raw_description}
user_comment: {user_comment}
Return only valid JSON.
"""

def _get_llm_client():
    # Use LANGCHAIN ChatOpenAI wrapper when available
    if os.getenv("MOCK_LLM", "false").lower() == "true" or not LANGCHAIN_AVAILABLE:
        return None
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

def _call_llm_for_rows(llm, rows: List[Dict]) -> List[Dict]:
    """
    Batch call: send list of transactions and expect a JSON array of outputs.
    If using mock (llm is None), use heuristic mock function.
    """
    if os.getenv("MOCK_LLM", "false").lower() == "true" or llm is None:
        return [_mock_llm(row) for row in rows]

    # Build single prompt with items enumerated for batch
    items_text = "\n".join([f"Item {i+1}:\ndate: {r.get('tx_date')}\namount: {r.get('raw_amount')}\ndescription: {r.get('raw_description')}\nuser_comment: {r.get('user_comment') or ''}\n" for i,r in enumerate(rows)])
    prompt = PROMPT.replace("{tx_date}", "")  # we'll craft per-row via enumerated text
    final_prompt = f"Batch items:\n{items_text}\nFor each Item i return JSON object in an array. Return only JSON array."
    # naive LangChain invocation (simple)
    result = llm.predict(final_prompt)
    # try parse JSON array
    try:
        arr = json.loads(result)
        return arr
    except Exception:
        # fallback: attempt to parse multiple JSON objects in text
        objs = []
        import re
        for m in re.finditer(r'(\{(?:[^{}]|(?R))*\})', result, re.S):
            try:
                objs.append(json.loads(m.group(1)))
            except:
                pass
        if objs:
            return objs
    # final fallback: produce default others
    return [_mock_llm(r) for r in rows]

def _mock_llm(row: Dict) -> Dict:
    desc = (row.get("raw_description") or "").lower()
    # simple keyword mapping
    if any(k in desc for k in ("amazon","flipkart","myntra")):
        cat = "Shopping"
    elif any(k in desc for k in ("uber","ola","taxi","fuel")):
        cat = "Transport"
    elif any(k in desc for k in ("grocery","grocer","bigbasket","dmart","reliance")):
        cat = "Groceries"
    elif any(k in desc for k in ("salary","credit")):
        cat = "Income"
    else:
        cat = "Others"
    tx_type = "income" if cat == "Income" or (row.get("raw_amount") and float(row.get("raw_amount"))>0 and row.get("raw_credit_debit")=="CR") else "expense"
    upi = None
    m = re.search(r"([\w\.\-]+@[\w\-]+)", str(row.get("raw_description") or ""))
    if m:
        upi = m.group(1)
    return {
        "category": cat,
        "transaction_type": tx_type,
        "upi_id": upi,
        "normalized_description": (row.get("raw_description") or "")[:80],
        "confidence": 0.9
    }

def process_preview_rows_llm_batched(upload_id: int, db: Session, user_id: int, batch_size: int = 10):
    """
    Process preview rows in batches: calls LLM in batches and insert transactions.
    """
    repo = UploadPostgresRepository(db)
    preview_rows = repo.list_unprocessed_preview_rows(upload_id)
    logger.info("Processing %d preview rows for upload %s", len(preview_rows), upload_id)
    llm = _get_llm_client()

    # process in batches
    idx = 0
    while idx < len(preview_rows):
        batch = preview_rows[idx: idx+batch_size]
        rows_payload = []
        for p in batch:
            rows_payload.append({
                "tx_date": p.tx_date.isoformat() if getattr(p,'tx_date', None) else "",
                "raw_amount": float(p.raw_amount) if getattr(p,'raw_amount', None) is not None else 0.0,
                "raw_description": p.raw_description or "",
                "user_comment": p.user_comment or ""
            })
        logger.info("Calling LLM for batch size=%d", len(rows_payload))
        outputs = _call_llm_for_rows(llm, rows_payload)
        # outputs expected list with same length
        for p, out in zip(batch, outputs):
            # sanitize out
            if not isinstance(out, dict):
                out = _mock_llm(rows_payload[0])
            # map category to category_id
            cat_name = out.get("category") or "Others"
            cat_id = repo.get_or_create_category_id(cat_name, user_id=user_id)
            # update preview row
            repo.update_preview_row(p.id, {
                "suggested_category": cat_name,
                "suggested_transaction_type": out.get("transaction_type"),
                "suggested_upi_id": out.get("upi_id"),
                "user_comment": p.user_comment or None
            })
            repo.mark_preview_processed(p.id, out)
            # insert into transactions
            tx = repo.insert_transaction_from_preview(p, user_id, category_id=cat_id)
            logger.info("Inserted tx id=%s from preview id=%s", tx.id, p.id)
        idx += batch_size
        time.sleep(0.2)
    # finally mark upload done
    repo.set_upload_status(upload_id, "done")
    return True