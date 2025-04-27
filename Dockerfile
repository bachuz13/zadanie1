# syntax=docker/dockerfile:1.4

# Etap 1 - budowanie środowiska
FROM python:3.12-alpine AS builder
LABEL org.opencontainers.image.authors="Sebastian Żurawski"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Etap 2 - finalny obraz
FROM python:3.12-alpine

WORKDIR /app

# Kopiujemy tylko zainstalowane rzeczy + aplikację
COPY --from=builder /install /usr/local
COPY app.py .

EXPOSE 5000

# Dodajemy healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --spider http://localhost:5000 || exit 1

CMD ["python", "app.py"]
