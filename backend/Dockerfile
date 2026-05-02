FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpcap-dev iptables \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN python -m pip install --upgrade pip==24.0 \
    && for attempt in 1 2 3 4 5; do \
        pip install --retries 20 --timeout 120 --progress-bar off -r backend/requirements.txt && break; \
        echo "pip install falhou (tentativa ${attempt}/5), tentando novamente..."; \
        if [ "$attempt" -eq 5 ]; then exit 1; fi; \
      done

COPY backend backend
COPY estudo estudo
COPY alembic alembic
COPY alembic.ini .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
