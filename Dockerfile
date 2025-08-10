FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make migration script executable
RUN chmod +x migrate.sh

# Expose port
EXPOSE 8000

# Start the CRM application with database migrations
CMD ["sh", "-c", "./migrate.sh && python app.py"]
