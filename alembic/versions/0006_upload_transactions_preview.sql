-- create preview table
CREATE TABLE IF NOT EXISTS upload_transactions_preview (
  id SERIAL PRIMARY KEY,
  upload_id INTEGER NOT NULL REFERENCES uploads(id) ON DELETE CASCADE,
  tx_date DATE,
  raw_description TEXT,
  raw_amount NUMERIC(12,2),
  currency VARCHAR(16),
  raw_credit_debit TEXT, -- e.g., 'CR'/'DR' or original column
  suggested_category VARCHAR(128),
  suggested_transaction_type VARCHAR(16), -- income/expense
  suggested_upi_id VARCHAR(256),
  user_comment TEXT,  -- user-entered comment before processing
  lllm_result JSONB,  -- store LLM output (category, fields, confidence)
  processed BOOLEAN DEFAULT false,
  processed_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT now()
);

-- add source_upload_id to transactions if not exists
ALTER TABLE transactions
  ADD COLUMN IF NOT EXISTS source_upload_id INTEGER REFERENCES uploads(id);
