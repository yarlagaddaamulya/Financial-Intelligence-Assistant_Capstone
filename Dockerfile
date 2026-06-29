# Use a lightweight Python base image
FROM python:3.11-slim

# Set environment variables for non-interactive production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Set the working directory
WORKDIR /app

# Install system dependencies for handling PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure data persistence folders exist
RUN mkdir -p /app/data /app/chroma_db

# Expose Streamlit port
EXPOSE 8501

# Start the application
ENTRYPOINT ["streamlit", "run", "app.py"]