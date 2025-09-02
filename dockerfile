FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching helps if requirements.txt doesn’t change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
