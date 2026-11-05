#!/usr/bin/env bash
set -Eeuo pipefail

# Executa a partir da raiz do projeto, independentemente do diretório atual.
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
else
    echo "Erro: Python não foi encontrado. Instale Python 3 e tente novamente." >&2
    exit 1
fi

if ! "$PYTHON" -m venv --help >/dev/null 2>&1; then
    echo "Erro: o módulo venv não está disponível nesta instalação do Python." >&2
    echo "Em distribuições Debian/Ubuntu/Pop!_OS, instale o pacote python3-venv." >&2
    exit 1
fi

if [[ ! -d ".venv" ]]; then
    echo "==> Criando ambiente virtual..."
    "$PYTHON" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Atualizando o instalador de pacotes..."
python -m pip install --upgrade pip

echo "==> Instalando dependências..."
python -m pip install -r requirements.txt

echo "==> Aplicando migrações do banco de dados..."
python manage.py migrate

echo "==> Verificando a configuração do Django..."
python manage.py check

echo
echo "Projeto pronto. Acesse o Django Admin em:"
echo "http://127.0.0.1:8000/admin/"
echo
echo "Para criar um administrador, abra outro terminal, ative .venv e execute:"
echo "python manage.py createsuperuser"
echo

exec python manage.py runserver 127.0.0.1:8000
