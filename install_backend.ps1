<#
Script para criar ambiente virtual e instalar dependências do backend (Windows PowerShell).
Execute este script a partir da pasta `backend` ou dê o caminho completo para ele.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

if (-Not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python não encontrado no PATH. Instale Python 3.10+ e tente novamente."
    exit 1
}

python -m venv .venv
Write-Host "Ambiente virtual criado em .venv"

Write-Host "Ativando ambiente virtual..."
. .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Dependências instaladas. Para ativar manualmente o venv: .\.venv\Scripts\Activate.ps1"
Write-Host "Para executar a API: python -m uvicorn backend.main:app --reload (execute a partir da raiz do projeto ou ajuste o path)"
