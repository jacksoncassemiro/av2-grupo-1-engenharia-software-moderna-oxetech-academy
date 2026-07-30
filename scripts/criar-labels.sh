#!/usr/bin/env bash
# Cria as labels usadas pelos templates de Issue e pelo popular-board.sh --issues.
set -euo pipefail

REPO="jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy"

criar() {
  gh label create "$1" --repo "${REPO}" --color "$2" --description "$3" --force >/dev/null \
    && echo "  ok  $1"
}

command -v gh >/dev/null || { echo "ERRO: gh CLI nao encontrado." >&2; exit 1; }

echo "==> Criando labels em ${REPO}"
criar "user-story"    "0E8A16" "User Story do backlog"
criar "tarefa"        "1D76DB" "Tarefa tecnica"
criar "backend"       "5319E7" "FastAPI, SQLAlchemy, Alembic"
criar "frontend"      "FBCA04" "Next.js, React, Mantine"
criar "qa"            "006B75" "Testes, evidencias, CI"
criar "infra"         "C5DEF5" "Docker, ambiente, configuracao"
criar "documentacao"  "0075CA" "Documentacao e ADR"
criar "bug"           "D73A4A" "Defeito encontrado em teste ou uso"
criar "tech-debt"     "E99695" "Debito tecnico / antipadrao a refatorar"
criar "blocked"       "B60205" "Impedimento registrado"
criar "obrigatorio"   "B60205" "Escopo obrigatorio do MVP"
criar "desejavel"     "BFDADC" "Escopo desejavel - corta primeiro"
echo "==> Pronto."
