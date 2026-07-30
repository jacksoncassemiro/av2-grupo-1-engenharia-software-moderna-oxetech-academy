<#
.SYNOPSIS
  Audita e popula o quadro Kanban do GitHub Projects. Versao Windows / PowerShell.

.DESCRIPTION
  IDEMPOTENTE: antes de criar, le os titulos que ja existem (issues do repo e itens
  do board) e pula os repetidos. Pode rodar quantas vezes quiser.

  A equipe ja criou ~41 issues a partir das tarefas da Wiki (US-00 a US-12), com
  titulos no padrao "[US-00] [BACKEND] Endpoint de Login". Rode -Auditar primeiro.

  Colunas reais do board: To Do | In Dev | Code Review | In QA | UAT | Done

.PARAMETER Auditar
  So mostra o que existe vs. o planejado. Nao cria nada. COMECE POR AQUI.

.PARAMETER DryRun
  Lista o que seria criado, sem criar.

.PARAMETER Modo
  'draft' (padrao) cria itens que vivem so no board, sem Issue no repo.
  'issues' cria Issues no repositorio e adiciona ao board.

.PARAMETER Sprint
  Filtra por sprint: 1 ou 2.

.EXAMPLE
  .\scripts\popular-board.ps1 -Auditar
  .\scripts\popular-board.ps1 -DryRun
  .\scripts\popular-board.ps1
  .\scripts\popular-board.ps1 -Modo issues -Sprint 1

.NOTES
  Requer o GitHub CLI com escopo de project:
    winget install --id GitHub.cli
    gh auth login
    gh auth refresh -s project,read:project
#>
[CmdletBinding()]
param(
    [switch]$Auditar,
    [switch]$DryRun,
    [ValidateSet('draft', 'issues')]
    [string]$Modo = 'draft',
    [ValidateSet('1', '2')]
    [string]$Sprint
)

$ErrorActionPreference = 'Stop'

$Dono           = 'jacksoncassemiro'
$NumeroProjeto  = 3
$Repo           = 'jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy'

# ─────────────────────────────────────────────────────────────
# Itens planejados: Sprint / Tipo / Titulo / Corpo
# ─────────────────────────────────────────────────────────────
$Itens = @(
    @{ S = '1'; T = 'US';       Titulo = 'US-00: Autenticacao e vinculacao de conta por CPF'; Corpo = "Como Paciente ou Atendente, quero fazer login ou ativar meu primeiro acesso usando CPF ou e-mail, para acessar a plataforma conforme meu perfil.`n`nRegras: RN01, RN02, RN07, RN11, RN12, RN13`nCriterios de aceite: docs/02-backlog.md#us-00`nPrioridade: P0" }
    @{ S = '1'; T = 'BACKEND';  Titulo = '[BACKEND] POST /api/auth/login com login flexivel CPF ou e-mail'; Corpo = 'US-00. Normaliza o login: apenas digitos quando nao houver @, lowercase quando houver. Devolve JWT com tipo_usuario e paciente_id. RN11, RN13.' }
    @{ S = '1'; T = 'BACKEND';  Titulo = '[BACKEND] GET /api/auth/verificar-cpf/{cpf}'; Corpo = 'US-00. Devolve {cadastro_existe, login_ativo, nome} para a tela de primeiro acesso decidir o formulario.' }
    @{ S = '1'; T = 'BACKEND';  Titulo = '[BACKEND] POST /api/auth/vincular-ou-criar'; Corpo = 'US-00. Ativa o login de paciente existente OU faz o auto-cadastro completo. Resolve o conflito do enunciado (ADR-005). RN01, RN02, RN07.' }
    @{ S = '1'; T = 'BACKEND';  Titulo = '[BACKEND] Dependencias de autorizacao por perfil'; Corpo = 'US-00. usuario_atual, exigir_paciente, exigir_atendente. 401 sem token, 403 com perfil errado. RN12.' }
    @{ S = '1'; T = 'FRONTEND'; Titulo = '[FRONTEND] Tela de login com campo unico CPF ou E-mail'; Corpo = 'US-00. Mascara dinamica de CPF quando o valor nao contem @. Erro da API via notification.' }
    @{ S = '1'; T = 'FRONTEND'; Titulo = '[FRONTEND] Tela de primeiro acesso em duas etapas'; Corpo = 'US-00. Etapa 1 verifica o CPF; etapa 2 mostra formulario reduzido (so senha) ou completo (auto-cadastro).' }
    @{ S = '1'; T = 'FRONTEND'; Titulo = '[FRONTEND] Guarda de rota nos route groups (paciente) e (atendente)'; Corpo = 'US-00. Layout de cada grupo valida o tipo_usuario do token e redireciona. RF05. NAO usar middleware/proxy.' }
    @{ S = '1'; T = 'US';       Titulo = 'US-15: Cadastro de atendentes'; Corpo = "Como Atendente, quero cadastrar outros atendentes, para que a recepcao nao dependa de uma unica conta.`n`nRegras: RN02, RN11, RN14`nOrigem: conflito C02 / ADR-004`nPrioridade: P2" }
    @{ S = '1'; T = 'BACKEND';  Titulo = '[BACKEND] POST /api/atendente/atendentes'; Corpo = 'US-15. Protegido por exigir_atendente. Nao existe rota publica de cadastro de atendente. RN14.' }
    @{ S = '1'; T = 'FRONTEND'; Titulo = '[FRONTEND] Tela de cadastro de atendente'; Corpo = 'US-15.' }
    @{ S = '1'; T = 'US';       Titulo = 'US-01: Gestao de especialidades'; Corpo = "Como Atendente, quero gerenciar as especialidades medicas, para organizar o portfolio de atendimento.`n`nCriterios: docs/02-backlog.md#us-01`nPrioridade: P0" }
    @{ S = '1'; T = 'BACKEND';  Titulo = '[BACKEND] POST e GET /api/especialidades'; Corpo = 'US-01, US-06. Bloqueia nome duplicado. GET devolve apenas ativas.' }
    @{ S = '1'; T = 'FRONTEND'; Titulo = '[FRONTEND] Tela de cadastro e listagem de especialidades'; Corpo = 'US-01.' }
    @{ S = '1'; T = 'US';       Titulo = 'US-02: Gestao de medicos'; Corpo = "Como Atendente, quero gerenciar os medicos da clinica, para inclui-los na grade de atendimento.`n`nRegras: RN02, RN08`nPrioridade: P0" }
    @{ S = '1'; T = 'BACKEND';  Titulo = '[BACKEND] POST e GET /api/medicos com filtro por especialidade'; Corpo = 'US-02, US-06. Valida e-mail e CRM unicos. RN02.' }
    @{ S = '1'; T = 'FRONTEND'; Titulo = '[FRONTEND] Formulario de medico com Select de especialidade'; Corpo = 'US-02. Impede salvar sem especialidade.' }
    @{ S = '1'; T = 'US';       Titulo = 'US-03: Cadastro de pacientes'; Corpo = "Como Atendente, quero cadastrar novos pacientes, para viabilizar seus futuros agendamentos.`n`nRegras: RN01, RN02, RN07, RN08`nNota: NAO cria credencial. O login e ativado no primeiro acesso (US-00).`nPrioridade: P0" }
    @{ S = '1'; T = 'BACKEND';  Titulo = '[BACKEND] POST /api/pacientes com e-mail opcional'; Corpo = 'US-03. RN01 CPF unico, RN02 e-mail unico quando nao nulo, RN07 CPF valido.' }
    @{ S = '1'; T = 'FRONTEND'; Titulo = '[FRONTEND] Formulario de paciente com mascara e validacao de CPF'; Corpo = 'US-03. RN07 no cliente, espelhando o backend.' }
    @{ S = '1'; T = 'US';       Titulo = 'US-05: Cadastro de agenda e horarios disponiveis'; Corpo = "Como Atendente, quero cadastrar a grade horaria de um medico, para disponibilizar horarios para agendamento.`n`nRegras: RN05, RN09`nPrioridade: P0" }
    @{ S = '1'; T = 'BACKEND';  Titulo = '[BACKEND] POST /api/medicos/{id}/agenda com lista de horarios'; Corpo = 'US-05. RN05 unique (medico, data, horario), RN09 horario comercial 08:00-18:00.' }
    @{ S = '1'; T = 'FRONTEND'; Titulo = '[FRONTEND] Painel de lancamento de agenda'; Corpo = 'US-05. DatePickerInput + multiplos TimeInput.' }
    @{ S = '1'; T = 'QA';       Titulo = '[QA] Escrever CT01 a CT04'; Corpo = 'Cadastro de paciente, CPF duplicado, e-mail duplicado (inclusive nulo), primeiro acesso. docs/08-casos-de-teste.md' }
    @{ S = '1'; T = 'QA';       Titulo = '[QA] Escrever CT08, CT13, CT14'; Corpo = 'Alocacao dupla (RN05), horario comercial (RN09), atendente cria atendente (RN14).' }
    @{ S = '1'; T = 'QA';       Titulo = '[QA] Configurar branch protection em main e develop'; Corpo = 'PR obrigatorio, 1 aprovacao, quality-gate como required status check. docs/10-git-flow.md secao 2.' }
    @{ S = '1'; T = 'QA';       Titulo = '[QA] Sessao exploratoria EXP-01 - cadastros'; Corpo = '45 min. Charter: falhas de validacao e duplicidade em US-01 a US-04. Registrar em docs/07-plano-de-testes.md.' }
    @{ S = '1'; T = 'INFRA';    Titulo = '[INFRA] Revisar a migracao inicial do Alembic'; Corpo = 'O autogenerate NAO cria o indice parcial uq_slot_ativo. Ver docs/04-modelo-de-dados.md e tests/integration/test_migracoes.py.' }
    @{ S = '2'; T = 'US';       Titulo = 'US-06: Consulta de medicos e especialidades'; Corpo = "Como Paciente, quero pesquisar medicos e especialidades, para encontrar o profissional correto.`n`nPrioridade: P2" }
    @{ S = '2'; T = 'US';       Titulo = 'US-07: Visualizacao de horarios disponiveis'; Corpo = "Como Paciente, quero ver os horarios disponiveis de um medico, para escolher a melhor data.`n`nRegras: RN03`nPrioridade: P1" }
    @{ S = '2'; T = 'BACKEND';  Titulo = '[BACKEND] GET /api/medicos/{id}/horarios-livres'; Corpo = 'US-07. Somente slots com disponivel = true. RN03.' }
    @{ S = '2'; T = 'FRONTEND'; Titulo = '[FRONTEND] Calendario com horarios livres e estado vazio'; Corpo = 'US-07.' }
    @{ S = '2'; T = 'US';       Titulo = 'US-08: Solicitacao de consulta pelo paciente'; Corpo = "Como Paciente, quero escolher medico, data e horario disponivel, para agendar meu atendimento.`n`nRegras: RN03, RN06 (status inicial SOLICITADA)`nPrioridade: P0" }
    @{ S = '2'; T = 'BACKEND';  Titulo = '[BACKEND] POST /api/consultas com SELECT FOR UPDATE'; Corpo = 'US-08. Reserva com lock pessimista + indice parcial uq_slot_ativo. Resolve a corrida de dois pacientes no mesmo slot. RN03.' }
    @{ S = '2'; T = 'FRONTEND'; Titulo = '[FRONTEND] Fluxo de confirmacao de agendamento'; Corpo = 'US-08. modals.openConfirmModal antes de enviar.' }
    @{ S = '2'; T = 'US';       Titulo = 'US-09: Cadastro de consultas pelo atendente'; Corpo = "Como Atendente, quero cadastrar consultas para os pacientes, para preencher a agenda imediatamente.`n`nRegras: RN03, RN05, RN06 (status inicial CONFIRMADA)`nPrioridade: P1" }
    @{ S = '2'; T = 'BACKEND';  Titulo = '[BACKEND] POST /api/atendente/consultas'; Corpo = 'US-09. Status inicial CONFIRMADA, diferente da US-08.' }
    @{ S = '2'; T = 'FRONTEND'; Titulo = '[FRONTEND] Tela de agendamento pelo atendente'; Corpo = 'US-09. Busca de paciente + selecao de medico e horario.' }
    @{ S = '2'; T = 'US';       Titulo = 'US-04: Atualizacao cadastral pelo paciente'; Corpo = "Como Paciente, quero atualizar meus dados, para manter meu perfil correto.`n`nRegras: RN02, RN08, RN12`nPrioridade: P2" }
    @{ S = '2'; T = 'BACKEND';  Titulo = '[BACKEND] PUT /api/pacientes/me'; Corpo = 'US-04. paciente_id vem do token, nunca do path. RN12. CPF nao editavel.' }
    @{ S = '2'; T = 'FRONTEND'; Titulo = '[FRONTEND] Tela de perfil do paciente'; Corpo = 'US-04. CPF em modo leitura.' }
    @{ S = '2'; T = 'US';       Titulo = 'US-10: Visualizacao de consultas e historico'; Corpo = "Como Paciente, quero ver minhas consultas agendadas e passadas, para acompanhar meu historico.`n`nRegras: RN12`nPrioridade: P2" }
    @{ S = '2'; T = 'BACKEND';  Titulo = '[BACKEND] GET /api/consultas filtrando pelo token'; Corpo = 'US-10. Retorna apenas as consultas do paciente autenticado. RN12.' }
    @{ S = '2'; T = 'FRONTEND'; Titulo = '[FRONTEND] Lista de consultas com Badge por status'; Corpo = 'US-10. SOLICITADA amarelo, CONFIRMADA teal, FINALIZADA cinza, CANCELADA vermelho.' }
    @{ S = '2'; T = 'US';       Titulo = 'US-11: Cancelamento de consulta pelo paciente'; Corpo = "Como Paciente, quero cancelar uma consulta agendada, para liberar o horario.`n`nRegras: RN03, RN04, RN10, RN15`nPrioridade: P0" }
    @{ S = '2'; T = 'BACKEND';  Titulo = '[BACKEND] PATCH /api/consultas/{id}/cancelar com Strategy'; Corpo = 'US-11. CancelamentoPorPaciente valida 24h (RN04) no fuso America/Maceio (RN15). Libera o slot (RN03).' }
    @{ S = '2'; T = 'FRONTEND'; Titulo = '[FRONTEND] Acao de cancelar com modal e campo de motivo'; Corpo = 'US-11.' }
    @{ S = '2'; T = 'US';       Titulo = 'US-12: Cancelamento de consultas pelo atendente'; Corpo = "Como Atendente, quero cancelar consultas, para manter a agenda atualizada em imprevistos.`n`nRegras: RN03, RN10`nPrioridade: P1" }
    @{ S = '2'; T = 'BACKEND';  Titulo = '[BACKEND] PATCH /api/atendente/consultas/{id}/cancelar'; Corpo = 'US-12. CancelamentoPorAtendente, sem validacao de prazo. Libera o slot.' }
    @{ S = '2'; T = 'US';       Titulo = 'US-13: Confirmacao e finalizacao de consultas'; Corpo = "Como Atendente, quero confirmar consultas solicitadas e finalizar as realizadas, para que o status reflita a realidade da clinica.`n`nRegras: RN06, RN10`nOrigem: conflito C04 - sem esta US, consulta solicitada ficaria eternamente SOLICITADA e FINALIZADA seria codigo morto.`nPrioridade: P1" }
    @{ S = '2'; T = 'BACKEND';  Titulo = '[BACKEND] PATCH /api/atendente/consultas/{id}/status'; Corpo = 'US-13. Valida por TRANSICOES_PERMITIDAS. RN06, RN10.' }
    @{ S = '2'; T = 'FRONTEND'; Titulo = '[FRONTEND] Acoes de confirmar e finalizar na lista do atendente'; Corpo = 'US-13. Filtro por status para achar as pendentes.' }
    @{ S = '2'; T = 'QA';       Titulo = '[QA] Executar CT05 a CT07'; Corpo = 'Horario ocupado (RN03), cancelamento com 48h e com 12h (RN04). Coletar evidencias.' }
    @{ S = '2'; T = 'QA';       Titulo = '[QA] Executar CT09 a CT12'; Corpo = 'Ciclo de status (RN06), reagendar slot cancelado (RN03/RN10), 403 e 401 (RN12).' }
    @{ S = '2'; T = 'QA';       Titulo = '[QA] Sessao exploratoria EXP-03 - agendamento e concorrencia'; Corpo = '45 min. Duas abas no mesmo slot, duplo clique em Confirmar, estado obsoleto.' }
    @{ S = '2'; T = 'QA';       Titulo = '[QA] Sessao exploratoria EXP-04 - cancelamento e limites de 24h'; Corpo = '45 min. Fronteira exata: 23h59, 24h00, 24h01. Testar em maquina com outro fuso.' }
    @{ S = '2'; T = 'QA';       Titulo = '[QA] Relatorio final de testes e evidencias de CI'; Corpo = 'Preencher docs/08-casos-de-teste.md secao 4 e capturar o quality-gate verde + um PR bloqueado.' }
    @{ S = '2'; T = 'DOCS';     Titulo = '[DOCS] Montar slides da apresentacao'; Corpo = 'Roteiro de 15 slides em docs/13-papeis-e-responsabilidades.md. Salvar em docs/apresentacao/.' }
    @{ S = '2'; T = 'DOCS';     Titulo = '[DOCS] Release v1.0.0'; Corpo = 'release/1.0 -> main com --no-ff, tag anotada, merge de volta em develop. docs/10-git-flow.md secao 6.' }
    @{ S = '2'; T = 'US';       Titulo = 'US-14: Agenda geral da clinica (DESEJAVEL)'; Corpo = "Como Atendente, quero ver a agenda consolidada de todos os medicos, para gerenciar os atendimentos do dia.`n`nOrigem: conflito C08`nPrioridade: P3 - corta primeiro se o prazo apertar." }
)

$LabelsPorTipo = @{
    US       = 'user-story'
    BACKEND  = 'tarefa,backend'
    FRONTEND = 'tarefa,frontend'
    QA       = 'tarefa,qa'
    INFRA    = 'tarefa,infra'
    DOCS     = 'tarefa,documentacao'
}

# ─────────────────────────────────────────────────────────────
# Pre-requisitos
# ─────────────────────────────────────────────────────────────
$precisaGh = -not $DryRun

if ($precisaGh) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Host @"
ERRO: GitHub CLI (gh) nao encontrado.

Instale e autentique:
  winget install --id GitHub.cli
  gh auth login
  gh auth refresh -s project,read:project

Depois abra um terminal NOVO (para o PATH atualizar) e rode este script de novo.
"@ -ForegroundColor Red
        exit 1
    }

    gh auth status *>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: rode 'gh auth login'." -ForegroundColor Red
        exit 1
    }

    gh project view $NumeroProjeto --owner $Dono *>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: sem acesso ao Project. Rode: gh auth refresh -s project,read:project" -ForegroundColor Red
        exit 1
    }
}

# ─────────────────────────────────────────────────────────────
# Titulos que ja existem
# ─────────────────────────────────────────────────────────────
$Existentes = @()

if ($precisaGh) {
    Write-Host '==> Lendo o que ja existe (para nao duplicar)...' -ForegroundColor Cyan

    $issues = @(gh issue list --repo $Repo --state all --limit 500 --json title --jq '.[].title' 2>$null)
    $noBoard = @(gh project item-list $NumeroProjeto --owner $Dono --limit 500 --format json --jq '.items[].content.title' 2>$null)

    $Existentes = @($issues + $noBoard) | Where-Object { $_ } | Sort-Object -Unique
    Write-Host "    $($issues.Count) issues no repo, $($noBoard.Count) itens no board" -ForegroundColor DarkGray
}

function Test-JaExiste([string]$Titulo) {
    return $Existentes -contains $Titulo
}

# ─────────────────────────────────────────────────────────────
# Modo auditoria
# ─────────────────────────────────────────────────────────────
if ($Auditar) {
    Write-Host "`n════ ITENS QUE JA EXISTEM ($Repo) ════" -ForegroundColor Cyan
    gh issue list --repo $Repo --state all --limit 500 `
        --json number,title,labels `
        --template '{{range .}}#{{.number}}  {{.title}}{{if .labels}}  [{{range .labels}}{{.name}} {{end}}]{{end}}{{"\n"}}{{end}}'

    Write-Host "`n════ COBERTURA DAS USER STORIES ════" -ForegroundColor Cyan
    foreach ($us in '00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15') {
        $qtd = @($Existentes | Where-Object { $_ -match "US-?$us" }).Count
        $cor = if ($qtd -eq 0) { 'Red' } else { 'Green' }
        $marca = if ($qtd -eq 0) { '!! FALTA' } else { 'ok      ' }
        Write-Host ("  {0} US-{1}  -> {2} item(ns) mencionando" -f $marca, $us, $qtd) -ForegroundColor $cor
    }

    Write-Host "`n════ ITENS PLANEJADOS SEM TITULO IDENTICO ════" -ForegroundColor Cyan
    $faltando = 0
    foreach ($item in $Itens) {
        if (-not (Test-JaExiste $item.Titulo)) {
            Write-Host ("  [{0,-8}] {1}" -f $item.T, $item.Titulo) -ForegroundColor Yellow
            $faltando++
        }
    }

    Write-Host "`n  $faltando de $($Itens.Count) itens planejados nao tem titulo identico no repo." -ForegroundColor Cyan
    Write-Host '  Atencao: titulo diferente NAO significa que o trabalho nao esteja coberto.' -ForegroundColor DarkGray
    Write-Host '  Compare com a lista acima antes de rodar sem -Auditar.' -ForegroundColor DarkGray
    exit 0
}

# ─────────────────────────────────────────────────────────────
# Criacao
# ─────────────────────────────────────────────────────────────
$filtro = if ($Sprint) { " (Sprint $Sprint apenas)" } else { '' }
Write-Host "==> Modo: $Modo$filtro" -ForegroundColor Cyan
if ($DryRun) { Write-Host '==> DRY RUN - nada sera criado' -ForegroundColor Yellow }
Write-Host ''

$total = 0; $criados = 0; $pulados = 0

foreach ($item in $Itens) {
    if ($Sprint -and $item.S -ne $Sprint) { continue }
    $total++

    if ($DryRun) {
        Write-Host ("  [S{0}] {1,-8} {2}" -f $item.S, $item.T, $item.Titulo)
        continue
    }

    if (Test-JaExiste $item.Titulo) {
        $pulados++
        Write-Host ("  --  ja existe: {0}" -f $item.Titulo) -ForegroundColor DarkGray
        continue
    }

    if ($Modo -eq 'draft') {
        gh project item-create $NumeroProjeto --owner $Dono --title $item.Titulo --body $item.Corpo *>$null
    }
    else {
        $labels = $LabelsPorTipo[$item.T]
        $url = gh issue create --repo $Repo --title $item.Titulo --body $item.Corpo --label $labels 2>$null
        if ($LASTEXITCODE -ne 0) {
            $url = gh issue create --repo $Repo --title $item.Titulo --body $item.Corpo
        }
        gh project item-add $NumeroProjeto --owner $Dono --url $url *>$null
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host ("  !!  falhou: {0}" -f $item.Titulo) -ForegroundColor Red
        continue
    }

    $criados++
    Write-Host ("  ok  [S{0}] {1}" -f $item.S, $item.Titulo) -ForegroundColor Green
}

Write-Host ''
if ($DryRun) {
    Write-Host "==> $total itens seriam avaliados (neste modo nao ha checagem de duplicidade)." -ForegroundColor Cyan
}
else {
    Write-Host "==> $criados criados, $pulados pulados por ja existirem." -ForegroundColor Green
    Write-Host "==> Board: https://github.com/users/$Dono/projects/$NumeroProjeto" -ForegroundColor Cyan
}

Write-Host @"

Proximos passos manuais no board:
  1. Deixar em "To Do" os itens da Sprint 1 que atendem a Definition of Ready.
  2. Atribuir responsavel a cada item.
  3. Respeitar o WIP: no maximo 2 itens por pessoa em "In Dev".
  4. Se usou o modo draft e quiser rastreabilidade em PR, converta o item em Issue
     pela interface ("Convert to issue").
"@ -ForegroundColor DarkGray
