#!/usr/bin/env bash
# Atalho para scripts/popular-board.py. Linux, macOS, Git Bash e WSL.
#
# A logica de verdade esta no .py — uma implementacao so para os tres sistemas.
# Este arquivo apenas traduz as flags longas e repassa.
#
# Pre-requisitos:
#   gh auth login
#   gh auth refresh -s project,read:project
#   python3 scripts/gerar-board-itens.py
#
# Uso:
#   ./scripts/popular-board.sh --auditar
#   ./scripts/popular-board.sh --tudo --dry-run
#   ./scripts/popular-board.sh --tudo
#   ./scripts/popular-board.sh --criar --secao processo
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PYTHON=""
for candidato in python3 python py; do
  if command -v "$candidato" >/dev/null 2>&1; then PYTHON="$candidato"; break; fi
done

if [[ -z "$PYTHON" ]]; then
  echo "ERRO: Python nao encontrado no PATH." >&2
  echo "      Debian/Ubuntu:  sudo apt install python3" >&2
  echo "      macOS:          brew install python" >&2
  exit 1
fi

exec "$PYTHON" "${DIR}/popular-board.py" "$@"
