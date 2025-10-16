FROM python:3.11-slim

WORKDIR /app

# 12-Factor: explicit dependencies
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt

#COPY src/ ./src


# Copy the backend src folder into /app/src in container
COPY src ./src

# Copy requirements
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt



# 12-Factor: bind to a port
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
