# Use the official CadQuery image with OCP pre-installed
FROM cadquery/cadquery:latest

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies (your own packages)
RUN pip install --no-cache-dir -r requirements.txt

# Expose default port
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
