FROM python:3.14-slim

WORKDIR /post_creation

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# we .dockerignore to prevent .env and other unwanted files from entering
COPY . .  

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

