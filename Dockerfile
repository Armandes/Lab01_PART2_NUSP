FROM python:3.13.1-slim

WORKDIR /app

COPY requirements.docker.txt .
RUN pip install --no-cache-dir -r requirements.docker.txt

COPY . .

CMD ["python", "data/gold/carga.py"]