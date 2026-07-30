#!/usr/bin/env bash
# Popula o quadro Kanban do GitHub Projects com as User Stories e tarefas.
#
# DOIS MODOS:
#   --draft   (padrao)  cria DRAFT ITEMS: vivem so no board, NAO criam Issue no repo
#   --issues            cria Issues no repositorio e adiciona ao board
#
# Draft item aceita responsavel e campos customizados, mas nao aceita label.
# Pode ser convertido em Issue depois pela interface ("Convert to issue").
#
# Uso:
#   ./scripts/popular-board.sh --dry-run          # so lista o que criaria
#   ./scripts/popular-board.sh                    # draft items
#   ./scripts/popular-board.sh --issues           # Issues + board
#   ./scripts/popular-board.sh --sprint 1         # so a Sprint 1
#
# Requisitos: gh CLI autenticado com escopo `project`
#   gh auth login
#   gh auth refresh -s project,read:project
set -euo pipefail

DONO="jacksoncassemiro"
NUMERO_PROJETO=3
REPO="jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy"

MODO="draft"
DRY_RUN=false
SPRINT_FILTRO=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --issues)  MODO="issues"; shift ;;
    --draft)   MODO="draft";  shift ;;
    --dry-run) DRY_RUN=true;  shift ;;
    --sprint)  SPRINT_FILTRO="$2"; shift 2 ;;
    -h|--help) sed -n '2,25p' "$0"; exit 0 ;;
    *) echo "Opcao desconhecida: $1" >&2; exit 1 ;;
  esac
done

if ! ${DRY_RUN}; then
  command -v gh >/dev/null || { echo "ERRO: gh CLI nao encontrado. https://cli.github.com" >&2; exit 1; }
  gh auth status >/dev/null 2>&1 || { echo "ERRO: rode 'gh auth login'." >&2; exit 1; }
  if ! gh project view "${NUMERO_PROJETO}" --owner "${DONO}" >/dev/null 2>&1; then
    cat >&2 <<'MSG'
ERRO: sem acesso ao Project.
Rode:  gh auth refresh -s project,read:project
MSG
    exit 1
  fi
fi

# ─────────────────────────────────────────────────────────────
# Itens: SPRINT|TIPO|TITULO|CORPO
# ─────────────────────────────────────────────────────────────
ITENS=(
"1|US|US-00: Autenticacao e vinculacao de conta por CPF|Como Paciente ou Atendente, quero fazer login ou ativar meu primeiro acesso usando CPF ou e-mail, para acessar a plataforma conforme meu perfil.

Regras: RN01, RN02, RN07, RN11, RN12, RN13
Criterios de aceite: docs/02-backlog.md#us-00
Prioridade: P0"
"1|BACKEND|[BACKEND] POST /api/auth/login com login flexivel CPF ou e-mail|US-00. Normaliza o login: apenas digitos quando nao houver @, lowercase quando houver. Devolve JWT com tipo_usuario e paciente_id. RN11, RN13."
"1|BACKEND|[BACKEND] GET /api/auth/verificar-cpf/{cpf}|US-00. Devolve {cadastro_existe, login_ativo, nome} para a tela de primeiro acesso decidir o formulario."
"1|BACKEND|[BACKEND] POST /api/auth/vincular-ou-criar|US-00. Ativa o login de paciente existente OU faz o auto-cadastro completo. Resolve o conflito do enunciado (ADR-005). RN01, RN02, RN07."
"1|BACKEND|[BACKEND] Dependencias de autorizacao por perfil|US-00. usuario_atual, exigir_paciente, exigir_atendente. 401 sem token, 403 com perfil errado. RN12."
"1|FRONTEND|[FRONTEND] Tela de login com campo unico CPF ou E-mail|US-00. Mascara dinamica de CPF quando o valor nao contem @. Erro da API via notification."
"1|FRONTEND|[FRONTEND] Tela de primeiro acesso em duas etapas|US-00. Etapa 1 verifica o CPF; etapa 2 mostra formulario reduzido (so senha) ou completo (auto-cadastro)."
"1|FRONTEND|[FRONTEND] Guarda de rota nos route groups (paciente) e (atendente)|US-00. Layout de cada grupo valida o tipo_usuario do token e redireciona. RF05."
"1|US|US-15: Cadastro de atendentes|Como Atendente, quero cadastrar outros atendentes, para que a recepcao nao dependa de uma unica conta.

Regras: RN02, RN11, RN14
Origem: conflito C02 / ADR-004
Prioridade: P2"
"1|BACKEND|[BACKEND] POST /api/atendente/atendentes|US-15. Protegido por exigir_atendente. Nao existe rota publica de cadastro de atendente. RN14."
"1|FRONTEND|[FRONTEND] Tela de cadastro de atendente|US-15."
"1|US|US-01: Gestao de especialidades|Como Atendente, quero gerenciar as especialidades medicas, para organizar o portfolio de atendimento.

Criterios: docs/02-backlog.md#us-01
Prioridade: P0"
"1|BACKEND|[BACKEND] POST e GET /api/especialidades|US-01, US-06. Bloqueia nome duplicado. GET devolve apenas ativas."
"1|FRONTEND|[FRONTEND] Tela de cadastro e listagem de especialidades|US-01."
"1|US|US-02: Gestao de medicos|Como Atendente, quero gerenciar os medicos da clinica, para inclui-los na grade de atendimento.

Regras: RN02, RN08
Prioridade: P0"
"1|BACKEND|[BACKEND] POST e GET /api/medicos com filtro por especialidade|US-02, US-06. Valida e-mail e CRM unicos. RN02."
"1|FRONTEND|[FRONTEND] Formulario de medico com Select de especialidade|US-02. Impede salvar sem especialidade."
"1|US|US-03: Cadastro de pacientes|Como Atendente, quero cadastrar novos pacientes, para viabilizar seus futuros agendamentos.

Regras: RN01, RN02, RN07, RN08
Nota: NAO cria credencial. O login e ativado no primeiro acesso (US-00).
Prioridade: P0"
"1|BACKEND|[BACKEND] POST /api/pacientes com e-mail opcional|US-03. RN01 CPF unico, RN02 e-mail unico quando nao nulo, RN07 CPF valido."
"1|FRONTEND|[FRONTEND] Formulario de paciente com mascara e validacao de CPF|US-03. RN07 no cliente, espelhando o backend."
"1|US|US-05: Cadastro de agenda e horarios disponiveis|Como Atendente, quero cadastrar a grade horaria de um medico, para disponibilizar horarios para agendamento.

Regras: RN05, RN09
Prioridade: P0"
"1|BACKEND|[BACKEND] POST /api/medicos/{id}/agenda com lista de horarios|US-05. RN05 unique (medico, data, horario), RN09 horario comercial 08:00-18:00."
"1|FRONTEND|[FRONTEND] Painel de lancamento de agenda|US-05. DatePickerInput + multiplos TimeInput."
"1|QA|[QA] Escrever CT01 a CT04|Cadastro de paciente, CPF duplicado, e-mail duplicado (inclusive nulo), primeiro acesso. docs/08-casos-de-teste.md"
"1|QA|[QA] Escrever CT08, CT13, CT14|Alocacao dupla (RN05), horario comercial (RN09), atendente cria atendente (RN14)."
"1|QA|[QA] Configurar branch protection em main e develop|PR obrigatorio, 1 aprovacao, quality-gate como required status check. docs/10-git-flow.md"
"1|QA|[QA] Sessao exploratoria EXP-01 - cadastros|45 min. Charter: falhas de validacao e duplicidade em US-01 a US-04. Registrar em docs/07-plano-de-testes.md"
"1|INFRA|[INFRA] Migracao inicial do Alembic|Revisar o autogenerate: ele NAO cria o indice parcial uq_slot_ativo nem detecta bem ENUM. Conferir docs/04-modelo-de-dados.md."
"1|INFRA|[INFRA] Gerar e commitar o yarn.lock|Rodar yarn install no frontend e commitar o lockfile para o CI usar --frozen-lockfile."
"2|US|US-06: Consulta de medicos e especialidades|Como Paciente, quero pesquisar medicos e especialidades, para encontrar o profissional correto.

Prioridade: P2"
"2|US|US-07: Visualizacao de horarios disponiveis|Como Paciente, quero ver os horarios disponiveis de um medico, para escolher a melhor data.

Regras: RN03
Prioridade: P1"
"2|BACKEND|[BACKEND] GET /api/medicos/{id}/horarios-livres|US-07. Somente slots com disponivel = true. RN03."
"2|FRONTEND|[FRONTEND] Calendario com horarios livres e estado vazio|US-07."
"2|US|US-08: Solicitacao de consulta pelo paciente|Como Paciente, quero escolher medico, data e horario disponivel, para agendar meu atendimento.

Regras: RN03, RN06 (status inicial SOLICITADA)
Prioridade: P0"
"2|BACKEND|[BACKEND] POST /api/consultas com SELECT FOR UPDATE|US-08. Reserva com lock pessimista + indice parcial uq_slot_ativo. Resolve a corrida descrita no CA2. RN03."
"2|FRONTEND|[FRONTEND] Fluxo de confirmacao de agendamento|US-08. modals.openConfirmModal antes de enviar."
"2|US|US-09: Cadastro de consultas pelo atendente|Como Atendente, quero cadastrar consultas para os pacientes, para preencher a agenda imediatamente.

Regras: RN03, RN05, RN06 (status inicial CONFIRMADA)
Prioridade: P1"
"2|BACKEND|[BACKEND] POST /api/atendente/consultas|US-09. Status inicial CONFIRMADA, diferente da US-08."
"2|FRONTEND|[FRONTEND] Tela de agendamento pelo atendente|US-09. Busca de paciente + selecao de medico e horario."
"2|US|US-04: Atualizacao cadastral pelo paciente|Como Paciente, quero atualizar meus dados, para manter meu perfil correto.

Regras: RN02, RN08, RN12
Prioridade: P2"
"2|BACKEND|[BACKEND] PUT /api/pacientes/me|US-04. paciente_id vem do token, nunca do path. RN12. CPF nao editavel."
"2|FRONTEND|[FRONTEND] Tela de perfil do paciente|US-04. CPF em modo leitura."
"2|US|US-10: Visualizacao de consultas e historico|Como Paciente, quero ver minhas consultas agendadas e passadas, para acompanhar meu historico.

Regras: RN12
Prioridade: P2"
"2|BACKEND|[BACKEND] GET /api/consultas filtrando pelo token|US-10. Retorna apenas as consultas do paciente autenticado. RN12."
"2|FRONTEND|[FRONTEND] Lista de consultas com Badge por status|US-10. SOLICITADA amarelo, CONFIRMADA teal, FINALIZADA cinza, CANCELADA vermelho."
"2|US|US-11: Cancelamento de consulta pelo paciente|Como Paciente, quero cancelar uma consulta agendada, para liberar o horario.

Regras: RN03, RN04, RN10, RN15
Prioridade: P0"
"2|BACKEND|[BACKEND] PATCH /api/consultas/{id}/cancelar com Strategy|US-11. CancelamentoPorPaciente valida 24h (RN04) no fuso America/Maceio (RN15). Libera o slot (RN03)."
"2|FRONTEND|[FRONTEND] Acao de cancelar com modal e campo de motivo|US-11."
"2|US|US-12: Cancelamento de consultas pelo atendente|Como Atendente, quero cancelar consultas, para manter a agenda atualizada em imprevistos.

Regras: RN03, RN10
Prioridade: P1"
"2|BACKEND|[BACKEND] PATCH /api/atendente/consultas/{id}/cancelar|US-12. CancelamentoPorAtendente, sem validacao de prazo. Libera o slot."
"2|US|US-13: Confirmacao e finalizacao de consultas|Como Atendente, quero confirmar consultas solicitadas e finalizar as realizadas, para que o status reflita a realidade da clinica.

Regras: RN06, RN10
Origem: conflito C04 - sem esta US, consulta solicitada ficaria eternamente SOLICITADA e FINALIZADA seria codigo morto.
Prioridade: P1"
"2|BACKEND|[BACKEND] PATCH /api/atendente/consultas/{id}/status|US-13. Valida por TRANSICOES_PERMITIDAS. RN06, RN10."
"2|FRONTEND|[FRONTEND] Acoes de confirmar e finalizar na lista do atendente|US-13. Filtro por status para achar as pendentes."
"2|QA|[QA] Executar CT05 a CT07|Horario ocupado (RN03), cancelamento com 48h e com 12h (RN04). Coletar evidencias."
"2|QA|[QA] Executar CT09 a CT12|Ciclo de status (RN06), reagendar slot cancelado (RN03/RN10), 403 e 401 (RN12)."
"2|QA|[QA] Sessao exploratoria EXP-03 - agendamento e concorrencia|45 min. Duas abas no mesmo slot, duplo clique em Confirmar, estado obsoleto."
"2|QA|[QA] Sessao exploratoria EXP-04 - cancelamento e limites de 24h|45 min. Fronteira exata: 23h59, 24h00, 24h01. Testar em maquina com outro fuso."
"2|QA|[QA] Relatorio final de testes e evidencias de CI|Preencher docs/08-casos-de-teste.md secao 4 e capturar o quality-gate verde + um PR bloqueado."
"2|DOCS|[DOCS] Montar slides da apresentacao|Roteiro de 15 slides em docs/13-papeis-e-responsabilidades.md. Salvar em docs/apresentacao/."
"2|DOCS|[DOCS] Release v1.0.0|release/1.0 -> main com --no-ff, tag anotada, merge de volta em develop. docs/10-git-flow.md secao 6."
"2|US|US-14: Agenda geral da clinica (DESEJAVEL)|Como Atendente, quero ver a agenda consolidada de todos os medicos, para gerenciar os atendimentos do dia.

Origem: conflito C08
Prioridade: P3 - corta primeiro se o prazo apertar."
)

total=0
criados=0

echo "==> Modo: ${MODO}${SPRINT_FILTRO:+ (Sprint ${SPRINT_FILTRO} apenas)}"
${DRY_RUN} && echo "==> DRY RUN - nada sera criado"
echo

for item in "${ITENS[@]}"; do
  sprint="${item%%|*}"
  resto="${item#*|}"
  tipo="${resto%%|*}"
  resto="${resto#*|}"
  titulo="${resto%%|*}"
  corpo="${resto#*|}"

  [[ -n "${SPRINT_FILTRO}" && "${sprint}" != "${SPRINT_FILTRO}" ]] && continue
  total=$((total + 1))

  if ${DRY_RUN}; then
    printf '  [S%s] %-8s %s\n' "${sprint}" "${tipo}" "${titulo}"
    continue
  fi

  if [[ "${MODO}" == "draft" ]]; then
    gh project item-create "${NUMERO_PROJETO}" \
      --owner "${DONO}" \
      --title "${titulo}" \
      --body "${corpo}" >/dev/null
  else
    case "${tipo}" in
      US)       labels="user-story" ;;
      BACKEND)  labels="tarefa,backend" ;;
      FRONTEND) labels="tarefa,frontend" ;;
      QA)       labels="tarefa,qa" ;;
      INFRA)    labels="tarefa,infra" ;;
      DOCS)     labels="tarefa,documentacao" ;;
      *)        labels="tarefa" ;;
    esac
    url=$(gh issue create --repo "${REPO}" \
      --title "${titulo}" --body "${corpo}" --label "${labels}" 2>/dev/null) \
      || url=$(gh issue create --repo "${REPO}" --title "${titulo}" --body "${corpo}")
    gh project item-add "${NUMERO_PROJETO}" --owner "${DONO}" --url "${url}" >/dev/null
  fi

  criados=$((criados + 1))
  printf '  ok  [S%s] %s\n' "${sprint}" "${titulo}"
done

echo
if ${DRY_RUN}; then
  echo "==> ${total} itens seriam criados."
else
  echo "==> ${criados} itens criados."
  echo "==> Board: https://github.com/users/${DONO}/projects/${NUMERO_PROJETO}"
fi

cat <<'FIM'

Proximos passos manuais no board:
  1. Mover para "Ready" os itens da Sprint 1 que atendem a Definition of Ready.
  2. Atribuir responsavel a cada item (draft item aceita assignee).
  3. Respeitar o WIP: no maximo 2 itens por pessoa em "In progress".
  4. Se usou --draft e quiser rastreabilidade em PR, converta o item em Issue
     pela interface ("Convert to issue").
FIM
