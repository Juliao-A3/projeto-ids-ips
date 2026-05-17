FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

ARG INSTALL_PROFILE=sniffer

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends libpcap-dev iptables \
	&& rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
COPY agents/requeriment.txt agents/requeriment.txt
COPY agents/sniffer_requirements.txt agents/sniffer_requirements.txt

RUN python -m pip install --upgrade pip \
	&& if [ "$INSTALL_PROFILE" = "sniffer" ]; then pip install -r agents/sniffer_requirements.txt; fi \
	&& if [ "$INSTALL_PROFILE" = "firewall" ]; then pip install -r agents/requeriment.txt; fi

COPY backend backend
COPY models models
COPY sniffer sniffer
COPY agents agents

CMD ["python", "/app/sniffer/start_sniffer.py"]

