FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install -r backend/requirements.txt

COPY backend backend
COPY estudo estudo
COPY sniffer sniffer

CMD ["python", "sniffer/start_sniffer.py"]
