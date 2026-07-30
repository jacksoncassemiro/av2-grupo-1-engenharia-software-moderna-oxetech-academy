#!/usr/bin/env bash
# Fecha as issues originais e recria o board com rastreabilidade completa.
# Versao Linux/macOS/Git Bash. Le os itens de scripts/board-itens.json (mesma fonte do .ps1).
#
#   ./scripts/popular-board.sh --auditar
#   ./scripts/popular-board.sh --tudo --dry-run     # confira antes
#   ./scripts/popular-board.sh --tudo
#   ./scripts/popular-board.sh --criar --secao processo
#
# Requisitos: gh CLI autenticado com escopo project, e python3.
#   gh auth login && gh auth refresh -s project,read:project
set -euo pipefail

DONO="jacksoncassemiro"
NUMERO_PROJETO=3
REPO="jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ITENS_JSON="${RAIZ}/scripts/board-itens.json"

MODO="issues"; DRY_RUN=false; AUDITAR=false; FECHAR=false; CRIAR=false
SPRINT=""; SECAO=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --auditar) AUDITAR=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --fechar)  FECHAR=true;  shift ;;
    --criar)   CRIAR=true;   shift ;;
    --tudo)    FECHAR=true; CRIAR=true; shift ;;
    --draft)   MODO="draft";  shift ;;
    --issues)  MODO="issues"; shift ;;
    --sprint)  SPRINT="$2"; shift 2 ;;
    --secao)   SECAO="$2";  shift 2 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "Opcao desconhecida: $1" >&2; exit 1 ;;
  esac
done

if ! ${AUDITAR} && ! ${FECHAR} && ! ${CRIAR}; then
  cat <<'MSG'
Nada a fazer. Escolha uma acao:

  --auditar             mostra o que existe vs. o planejado (nao escreve)
  --tudo --dry-run      mostra o que fecharia e criaria (nao escreve)   <- comece aqui
  --tudo                fecha as 41 originais e cria os 82 novos
  --fechar              so fecha as originais
  --criar               so cria os novos
  --criar --secao processo   cria so os itens de QA/INFRA/DOCS
MSG
  exit 0
fi

[[ -f "${ITENS_JSON}" ]] || { echo "ERRO: ${ITENS_JSON} nao encontrado." >&2; exit 1; }
command -v python3 >/dev/null || { echo "ERRO: python3 necessario para ler o JSON." >&2; exit 1; }

if ! ${DRY_RUN}; then
  command -v gh >/dev/null || { echo "ERRO: gh CLI nao encontrado. https://cli.github.com" >&2; exit 1; }
  gh auth status >/dev/null 2>&1 || { echo "ERRO: rode 'gh auth login'." >&2; exit 1; }
  gh project view "${NUMERO_PROJETO}" --owner "${DONO}" >/dev/null 2>&1 \
    || { echo "ERRO: sem acesso ao Project. Rode: gh auth refresh -s project,read:project" >&2; exit 1; }
fi

# ── Estado atual ─────────────────────────────────────────────
TITULOS_EXISTENTES=""
ABERTAS=""
if ! ${DRY_RUN}; then
  echo "==> Lendo o estado atual do repositorio..."
  ABERTAS=$(gh issue list --repo "${REPO}" --state open --limit 500 --json number --jq '.[].number' 2>/dev/null || true)
  todas=$(gh issue list --repo "${REPO}" --state all --limit 500 --json title --jq '.[].title' 2>/dev/null || true)
  no_board=$(gh project item-list "${NUMERO_PROJETO}" --owner "${DONO}" --limit 500 --format json --jq '.items[].content.title' 2>/dev/null || true)
  TITULOS_EXISTENTES=$(printf '%s\n%s\n' "${todas}" "${no_board}" | sed '/^$/d' | sort -u)
fi

ja_existe() { [[ -n "${TITULOS_EXISTENTES}" ]] && grep -Fxq "$1" <<< "${TITULOS_EXISTENTES}"; }
esta_aberta() { [[ -n "${ABERTAS}" ]] && grep -Fxq "$1" <<< "${ABERTAS}"; }

# Le o JSON e emite linhas: SECAO<TAB>SPRINT<TAB>TIPO<TAB>TITULO<TAB>CORPO_BASE64
ler_itens() {
  python3 - "${ITENS_JSON}" "${SPRINT}" "${SECAO}" <<'PY'
import base64, json, sys
caminho, sprint, secao_filtro = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(caminho, encoding="utf-8"))
for secao in ("user_stories", "tarefas", "processo"):
    if secao_filtro and secao_filtro != secao:
        continue
    for i in d[secao]:
        if sprint and i["sprint"] != sprint:
            continue
        corpo = base64.b64encode(i["corpo"].encode("utf-8")).decode("ascii")
        print("\t".join([secao, i["sprint"], i["tipo"], i["titulo"], corpo]))
PY
}

ler_a_fechar() {
  python3 - "${ITENS_JSON}" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
for o in d["issues_a_fechar"]:
    print(f"{o['numero']}\t{o['titulo']}")
PY
}

label_de() {
  case "$1" in
    US) echo "user-story" ;; BACKEND) echo "tarefa,backend" ;; FRONTEND) echo "tarefa,frontend" ;;
    QA) echo "tarefa,qa" ;;  INFRA) echo "tarefa,infra" ;;    DOCS) echo "tarefa,documentacao" ;;
    *) echo "tarefa" ;;
  esac
}

# ── Auditoria ────────────────────────────────────────────────
if ${AUDITAR}; then
  echo; echo "════ ISSUES ABERTAS HOJE ════"
  gh issue list --repo "${REPO}" --state open --limit 500 \
    --json number,title,labels \
    --template '{{range .}}#{{.number}}  {{.title}}{{if .labels}}  [{{range .labels}}{{.name}} {{end}}]{{else}}  (sem label){{end}}{{"\n"}}{{end}}'

  echo; echo "════ A FECHAR (originais sem rastreabilidade) ════"
  n=0
  while IFS=$'\t' read -r numero titulo; do
    if esta_aberta "${numero}"; then printf '  #%-3s %s\n' "${numero}" "${titulo}"; n=$((n+1)); fi
  done < <(ler_a_fechar)
  echo "  -> ${n} ainda abertas"

  echo; echo "════ A CRIAR ════"
  for secao in user_stories tarefas processo; do
    total=0; faltam=0
    while IFS=$'\t' read -r s _ _ titulo _; do
      [[ "${s}" == "${secao}" ]] || continue
      total=$((total+1)); ja_existe "${titulo}" || faltam=$((faltam+1))
    done < <(SECAO="" SPRINT="" ler_itens)
    printf '  %-14s %3s de %3s ainda nao existem\n' "${secao}" "${faltam}" "${total}"
  done
  exit 0
fi

# ── Fechar ───────────────────────────────────────────────────
if ${FECHAR}; then
  echo; echo "════ FECHANDO AS ISSUES ORIGINAIS ════"
  JUSTIFICATIVA=$(cat <<'MSG'
Fechada como **substituída**, não como descartada.

O escopo técnico desta issue está correto e foi **preservado integralmente** na issue
recriada. O motivo do fechamento é rastreabilidade: a AV2 avalia a cadeia
requisito → código → teste → evidência, e as issues originais não citavam a User Story,
as regras de negócio cobertas, o critério de aceite nem o Definition of Done — e não
tinham label, o que impedia usar o board para WIP e métricas.

A versão recriada tem o mesmo título e a mesma descrição técnica, mais:

- **US** e **RNs** cobertas, com os IDs de `docs/01-requisitos.md`
- Link do critério de aceite em `docs/02-backlog.md`
- **Definition of Done** por área (backend / frontend)
- Label de área e de escopo (obrigatório / desejável)
- Item guarda-chuva da User Story, onde o PO valida os critérios de aceite em UAT

Crédito do levantamento original: @Lothriiik.
MSG
)
  fechadas=0; ja=0
  while IFS=$'\t' read -r numero titulo; do
    if ${DRY_RUN}; then printf '  [dry] fecharia #%-3s %s\n' "${numero}" "${titulo}"; continue; fi
    if ! esta_aberta "${numero}"; then ja=$((ja+1)); printf '  --  #%s ja esta fechada\n' "${numero}"; continue; fi
    gh issue comment "${numero}" --repo "${REPO}" --body "${JUSTIFICATIVA}" >/dev/null
    gh issue close   "${numero}" --repo "${REPO}" --reason 'not planned' >/dev/null
    fechadas=$((fechadas+1)); printf '  ok  fechada #%-3s %s\n' "${numero}" "${titulo}"
  done < <(ler_a_fechar)
  ${DRY_RUN} || echo "  ${fechadas} fechadas, ${ja} ja estavam fechadas."
fi

# ── Criar ────────────────────────────────────────────────────
if ${CRIAR}; then
  echo; echo "════ CRIANDO OS ITENS (${MODO})${SPRINT:+ · Sprint ${SPRINT}}${SECAO:+ · ${SECAO}} ════"
  ${DRY_RUN} && echo "  DRY RUN - nada sera criado"
  criados=0; pulados=0; total=0
  while IFS=$'\t' read -r _secao sprint tipo titulo corpo_b64; do
    total=$((total+1))
    corpo=$(printf '%s' "${corpo_b64}" | base64 -d)

    if ${DRY_RUN}; then printf '  [dry] [S%s] %-8s %s\n' "${sprint}" "${tipo}" "${titulo}"; continue; fi
    if ja_existe "${titulo}"; then pulados=$((pulados+1)); printf '  --  ja existe: %s\n' "${titulo}"; continue; fi

    if [[ "${MODO}" == "draft" ]]; then
      gh project item-create "${NUMERO_PROJETO}" --owner "${DONO}" --title "${titulo}" --body "${corpo}" >/dev/null
    else
      url=$(gh issue create --repo "${REPO}" --title "${titulo}" --body "${corpo}" --label "$(label_de "${tipo}")" 2>/dev/null) \
        || url=$(gh issue create --repo "${REPO}" --title "${titulo}" --body "${corpo}")
      [[ -n "${url}" ]] && gh project item-add "${NUMERO_PROJETO}" --owner "${DONO}" --url "${url}" >/dev/null
    fi
    criados=$((criados+1))
    TITULOS_EXISTENTES="${TITULOS_EXISTENTES}"$'\n'"${titulo}"
    printf '  ok  [S%s] %s\n' "${sprint}" "${titulo}"
  done < <(ler_itens)

  if ${DRY_RUN}; then echo "  ${total} itens seriam criados."
  else
    echo "  ${criados} criados, ${pulados} pulados por ja existirem."
    echo "  Board: https://github.com/users/${DONO}/projects/${NUMERO_PROJETO}"
    cat <<'FIM'

Proximos passos manuais no board:
  1. Colunas: To Do -> In Dev -> Code Review -> In QA -> UAT -> Done
  2. Mover para "In Dev" so o que a pessoa esta fazendo AGORA. WIP maximo 2 por pessoa.
  3. Cada um se atribui ao puxar o item (quem puxa, assume).
  4. Os itens "US-XX:" sao guarda-chuva: o PO move para UAT e valida os criterios de aceite.
FIM
  fi
fi
