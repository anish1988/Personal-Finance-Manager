FROM python:3.11-slim

WORKDIR /app

# 12-Factor: explicit dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src

# 12-Factor: bind to a port
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
