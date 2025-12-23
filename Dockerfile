FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for pydub/ffmpeg if voice processing is used)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
