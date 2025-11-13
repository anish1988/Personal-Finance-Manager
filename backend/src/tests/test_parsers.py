# backend/src/tests/test_parsers.py
import os
from infrastructure.ingest.parsers import parse_excel, parse_pdf, try_parse_date, try_parse_amount
def test_try_parse_amount():
    assert try_parse_amount("1,234.50") == 1234.5
    assert try_parse_amount("(1,234.50)") == -1234.5
    assert try_parse_amount("-500") == -500.0

# For parse_excel/pdf we include small fixture files under backend/tests/fixtures/
def test_parse_excel_sample():
    path = "backend/src/tests/fixtures/sample_statement.xlsx"
    rows = parse_excel(path)
    assert isinstance(rows, list)

def test_parse_pdf_sample():
    path = "backend/src/tests/fixtures/sample_statement.pdf"
    rows = parse_pdf(path)
    assert isinstance(rows, list)
