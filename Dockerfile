FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port (Railway handles mapping, but 8000 is our fastAPI default)
EXPOSE 8000

# Start command
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
