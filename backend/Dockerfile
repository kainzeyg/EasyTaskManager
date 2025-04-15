FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей для сборки
RUN apt-get update && \
    apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    python3-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc python3-dev libssl-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p /app/static
COPY static/default_avatar.png /app/static/default_avatar.png

CMD ["sh", "-c", "sleep 25 && uvicorn app.main:app --host 0.0.0.0 --port 8001"]