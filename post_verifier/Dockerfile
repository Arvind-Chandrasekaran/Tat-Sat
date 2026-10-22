FROM python:3.14-slim

WORKDIR /post_verifier

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# we .dockerignore to prevent .env and other unwanted files from entering
COPY . .  

CMD ["python3", "-u", "worker.py"]


