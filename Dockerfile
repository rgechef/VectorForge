# Use a slim Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose internal port
EXPOSE 10000

# Start FastAPI using Uvicorn
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
