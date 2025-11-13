# backend/src/infrastructure/ingest/parsers.py
import pandas as pd
import pdfplumber
from typing import List, Dict
from datetime import datetime
import re
import logging


logger = logging.getLogger("ingest.parsers")

def parse_excel(path: str) -> List[Dict]:
    """
    Heuristic-driven Excel parser:
      - read first sheet
      - normalize column names lowercased
      - attempt to locate date, description, amount, credit/debit columns
    Returns list of canonical row dicts.
    """
    try:
        df = pd.read_excel(path, sheet_name=0, dtype=str)
    except Exception as e:
        logger.exception("Failed reading excel: %s", e)
        return []

    # normalize header names
    df.columns = [str(c).strip() for c in df.columns]
    cols_lower = {c.lower(): c for c in df.columns}

    def get_col(*names):
        for n in names:
            if n in cols_lower:
                return cols_lower[n]
        return None

    date_col = get_col("date", "transaction date", "value date", "posting date")
    desc_col = get_col("description", "narration", "details", "particulars")
    debit_col = get_col("debit", "withdrawal", "debit amount", "dr")
    credit_col = get_col("credit", "deposit", "credit amount", "cr")
    amt_col = get_col("amount", "amt", "value")

    rows = []
    for _, r in df.iterrows():
        raw_desc = _val(r, desc_col) or _val(r, "Remarks") or ""
        # determine amount: prefer amt_col else credit/debit
        raw_amount = _val(r, amt_col)
        raw_cd = None
        if raw_amount is None and debit_col:
            raw_amount = _val(r, debit_col)
            raw_cd = "DR"
        if raw_amount is None and credit_col:
            raw_amount = _val(r, credit_col)
            raw_cd = "CR"
        row = {
            "tx_date": try_parse_date(_val(r, date_col)),
            "raw_description": raw_desc,
            "raw_amount": try_parse_amount(raw_amount),
            "currency": detect_currency_from_str(raw_desc) or None,
            "raw_credit_debit": raw_cd
        }
        rows.append(row)
    return rows

def _val(row, col):
    if col is None:
        return None
    v = row.get(col)
    return None if (pd.isna(v) or v is None) else str(v).strip()

def parse_pdf(path: str) -> List[Dict]:
    """
    Try table extraction first (pdfplumber extract_table). If not present, fallback to line heuristics.
    """
    rows = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    # handle first detected table(s)
                    for table in tables:
                        if not table:
                            continue
                        headers = [h.strip() if h else f"col{i}" for i,h in enumerate(table[0])]
                        for row in table[1:]:
                            data = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
                            rows.append({
                                "tx_date": try_parse_date(data.get("Date") or data.get("Txn Date") or data.get(headers[0])),
                                "raw_description": (data.get("Description") or data.get("Narration") or "") ,
                                "raw_amount": try_parse_amount(data.get("Amount") or data.get("Value") or data.get("Amt")),
                                "currency": None,
                                "raw_credit_debit": data.get("Type") or None
                            })
                else:
                    text = page.extract_text() or ""
                    # naive regex: date ... amount
                    for line in text.split("\n"):
                        m = re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}).*?(-?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)", line)
                        if m:
                            rows.append({
                                "tx_date": try_parse_date(m.group(1)),
                                "raw_description": line,
                                "raw_amount": try_parse_amount(m.group(2)),
                                "currency": None,
                                "raw_credit_debit": None
                            })
    except Exception as e:
        logger.exception("pdf parse failed: %s", e)
    return rows

def try_parse_date(v):
    if v is None: 
        return None
    if isinstance(v, datetime):
        return v.date()
    s = str(v).strip()
    # common formats
    for fmt in ("%Y-%m-%d","%d-%m-%Y","%d/%m/%Y","%d-%b-%Y","%d %b %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except:
            pass
    # try numeric excel date
    try:
        val = float(s)
        return (datetime(1899,12,30) + pd.to_timedelta(val, unit='D')).date()
    except:
        return None

def try_parse_amount(v):
    if v is None:
        return None
    s = str(v).replace(",", "").strip()
    if "(" in s and ")" in s:
        s = "-" + s.replace("(", "").replace(")", "")
    m = re.search(r"-?\d+(\.\d+)?", s)
    if m:
        try:
            return float(m.group(0))
        except:
            return None
    return None

def detect_currency_from_str(s: str):
    if not s:
        return None
    s = s.upper()
    if "INR" in s or "Rs." in s or "₹" in s:
        return "INR"
    if "USD" in s or "$" in s:
        return "USD"
    return None