# Use a slim Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Render listens on 0.0.0.0:10000+ internally)
EXPOSE 8000

# Start app using run.py
CMD ["python", "run.py"]
