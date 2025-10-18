# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy whole repo into image so /app/backend exists
COPY . /app

# Install requirements (adjust path if req file is elsewhere)
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir -r src/requirements.txt

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
