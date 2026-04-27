# Deploy Online com Docker (VPS)

Este guia sobe frontend + API + banco para acesso externo.

## 1. Preparar variaveis

1. Copie o arquivo de exemplo:

```bash
cp .env.online.example .env.online
```

2. Edite `.env.online` com:
- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `VITE_API_URL`
- `FRONTEND_ORIGINS`

## 2. Subir stack online

```bash
docker compose -f docker-compose.online.yml --env-file .env.online up -d --build
```

## 3. Verificar containers

```bash
docker compose -f docker-compose.online.yml ps
```

## 4. Testar endpoints

```bash
curl -I http://127.0.0.1:${WEB_PORT:-80}
curl -I http://127.0.0.1:${API_PORT:-8000}/docs
```

## 5. Acesso externo

- Frontend: `http://SEU_IP_PUBLICO:${WEB_PORT}`
- API Docs: `http://SEU_IP_PUBLICO:${API_PORT}/docs`

## 6. Firewall (Oracle / VPS)

Liberar entrada TCP para:
- `80` (frontend)
- `8000` (API)

Se usar HTTPS com dominio, libere tambem:
- `443`

## 7. Logs

```bash
docker compose -f docker-compose.online.yml logs -f web api db
```

## 8. Atualizacao

```bash
git pull
docker compose -f docker-compose.online.yml --env-file .env.online up -d --build
```

## Observacoes

- Este compose online nao usa `network_mode: host`.
- Se for usar sniffer com captura de trafego de interfaces do host, mantenha o compose host/sniffer dedicado.
- Para producao real, o recomendado e colocar Nginx/Traefik com HTTPS na frente da API e frontend.
