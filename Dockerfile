FROM python:3.11-slim

WORKDIR /app

# Installing system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./tests ./tests
COPY pytest.ini .

EXPOSE 8000

# Running the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
