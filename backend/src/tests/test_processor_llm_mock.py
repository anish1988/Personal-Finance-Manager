# backend/src/tests/test_processor_llm_mock.py
import os
os.environ["MOCK_LLM"] = "true"
from infrastructure.ingest.processor_llm import _mock_llm, _call_llm_for_rows

def test_mock_llm_simple():
    row = {"raw_description": "Amazon order ID 123", "raw_amount": 500}
    out = _mock_llm(row)
    assert "category" in out
    assert "confidence" in out

def test_batch_call_mock():
    rows = [{"raw_description":"BigBasket grocery","raw_amount":200}, {"raw_description":"Salary credit","raw_amount":50000}]
    outs = _call_llm_for_rows(None, rows)
    assert len(outs) == 2
