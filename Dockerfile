FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for CadQuery/OpenCASCADE/OpenGL
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
