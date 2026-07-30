#!/usr/bin/env bash
# Publica as paginas de wiki/ no Wiki do GitHub.
#
# O Wiki do GitHub e um repositorio git separado: <repo>.wiki.git
# Este script clona, sincroniza o conteudo de wiki/ e faz push.
#
#   ./scripts/publicar-wiki.sh            # publica
#   ./scripts/publicar-wiki.sh --dry-run  # mostra o que faria
set -euo pipefail

REPO="jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy"
WIKI_URL="https://github.com/${REPO}.wiki.git"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ORIGEM="${RAIZ}/wiki"
TMP="$(mktemp -d)"
DRY_RUN=false

[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

trap 'rm -rf "${TMP}"' EXIT

if [[ ! -d "${ORIGEM}" ]]; then
  echo "ERRO: pasta ${ORIGEM} nao encontrada." >&2
  exit 1
fi

echo "==> Clonando o wiki de ${REPO}"
if ! git clone --quiet "${WIKI_URL}" "${TMP}/wiki" 2>/dev/null; then
  cat >&2 <<'MSG'
ERRO: nao foi possivel clonar o wiki.

Causas comuns:
  1. O Wiki nunca foi inicializado. Crie a primeira pagina pela interface web
     (Wiki -> Create the first page) e rode este script de novo.
  2. O Git nao conseguiu autenticar o clone via HTTPS. Verifique se voce tem
     acesso ao repositorio e tente novamente.
     Se voce preferir SSH, troque a variavel WIKI_URL deste script por:
       git@github.com:${REPO}.wiki.git
MSG
  exit 1
fi

echo "==> Sincronizando paginas"
# Remove os .md antigos (mantem .git) e copia os novos.
# README.md de wiki/ e meta-documentacao da pasta - nao vai para o Wiki.
find "${TMP}/wiki" -maxdepth 1 -name '*.md' -delete
for pagina in "${ORIGEM}"/*.md; do
  [[ "$(basename "${pagina}")" == "README.md" ]] && continue
  cp "${pagina}" "${TMP}/wiki/"
done

cd "${TMP}/wiki"

if git diff --quiet && git diff --cached --quiet && [[ -z "$(git status --porcelain)" ]]; then
  echo "==> Nada mudou. Wiki ja esta atualizado."
  exit 0
fi

echo "==> Alteracoes:"
git add -A
git status --short

if ${DRY_RUN}; then
  echo
  echo "==> --dry-run: nada foi publicado."
  exit 0
fi

git -c user.name="${GIT_AUTHOR_NAME:-$(git config --global user.name || echo 'Equipe 01')}" \
    -c user.email="${GIT_AUTHOR_EMAIL:-$(git config --global user.email || echo 'equipe01@example.com')}" \
    commit --quiet -m "docs(wiki): sincroniza paginas a partir de wiki/"

git push --quiet origin HEAD
echo
echo "==> Publicado: https://github.com/${REPO}/wiki"
