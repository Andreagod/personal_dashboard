FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for web app
EXPOSE 5000

# Command is overridden in docker-compose
CMD ["python", "run.py"]
