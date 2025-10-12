CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    type VARCHAR(10), -- income/expense
    category VARCHAR(50),
    sub_category VARCHAR(50),
    amount NUMERIC(12,2),
    date DATE,
    description TEXT
);
