# Instruções para rodar o projeto localmente (Windows)

Este documento descreve os comandos e caminhos onde executar a instalação das dependências do backend (Python/FastAPI) e do frontend (Node/Vite).

## Backend (Python / FastAPI)

- Caminho do backend: `backend/`
- Arquivo de dependências criado: `backend/requirements.txt`
- Script de instalação (PowerShell): `backend/install_backend.ps1`

Comandos (PowerShell) — execute a partir de `projeto-ids-ips\backend` ou dê o caminho completo:

```powershell
# entrar na pasta do projeto (exemplo)
cd C:\Users\Herder Ernesto Ngola\Desktop\vscode\projeto-ids-ips\backend

# executar o script (cria .venv e instala dependências)
.\install_backend.ps1

# ativar venv manualmente (se necessário)
. .venv\Scripts\Activate.ps1

# executar API (a partir da raiz do repositório)
cd ..
python -m uvicorn backend.main:app --reload
```

Observações:
- Crie um arquivo `.env` na raiz do projeto com pelo menos `SECRET_KEY=uma_chave`.
- Banco de dados: por padrão local usa SQLite (`backend/database/banco.db`), mas em produção use PostgreSQL definindo `DATABASE_URL`.
- O `requirements.txt` usa `uvicorn[standard]`, que habilita suporte WebSocket para endpoints como `/sniffer/ws`.

## Frontend (Node / Vite / React + TypeScript)

- Caminho do frontend: `frontend/`
- Dependências definidas em: `frontend/package.json`

Comandos (PowerShell) — execute a partir de `projeto-ids-ips\frontend`:

```powershell
cd C:\Users\Herder Ernesto Ngola\Desktop\vscode\projeto-ids-ips\frontend
npm install
npm run dev
```

Requisitos:
- Instale Node.js (recomendo Node 18+ ou 20+).
