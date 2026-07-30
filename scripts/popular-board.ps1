<#
.SYNOPSIS
  Fecha as issues originais e recria o board com rastreabilidade completa. Windows / PowerShell.

.DESCRIPTION
  Le os itens de scripts\board-itens.json (fonte unica, compartilhada com o .sh).

  DECISAO DA EQUIPE: as 41 issues originais (#4 a #45, criadas por @Lothriiik) sao
  FECHADAS com comentario de justificativa e recriadas com US, RNs, criterio de aceite,
  Definition of Done e label. O fechamento usa --reason "not planned" e preserva todo o
  historico - nada e apagado.

  IDEMPOTENTE em tudo: pula issue ja fechada e titulo que ja existe. Pode rodar 2x.

  Colunas do board: To Do | In Dev | Code Review | In QA | UAT | Done

.PARAMETER Auditar
  Mostra o que existe vs. o planejado. Nao escreve nada.

.PARAMETER DryRun
  Mostra exatamente o que faria (fechar X, criar Y). Nao escreve nada.

.PARAMETER Fechar
  Fecha as 41 issues originais. Faca isto ANTES de -Criar, ou use -Tudo.

.PARAMETER Criar
  Cria os itens novos (User Stories + tarefas + processo).

.PARAMETER Tudo
  Equivale a -Fechar seguido de -Criar.

.PARAMETER Modo
  'issues' (padrao) cria Issues no repo e adiciona ao board - permite label e referencia em PR.
  'draft' cria itens que vivem so no board, sem Issue.

.PARAMETER Sprint
  Filtra a criacao por sprint: 1 ou 2.

.PARAMETER Secao
  Cria so uma parte: user_stories | tarefas | processo.

.EXAMPLE
  .\scripts\popular-board.ps1 -Auditar
  .\scripts\popular-board.ps1 -Tudo -DryRun        # ⭐ confira antes
  .\scripts\popular-board.ps1 -Tudo
  .\scripts\popular-board.ps1 -Criar -Secao processo

.NOTES
  Requer GitHub CLI autenticado com escopo de project:
    winget install --id GitHub.cli
    gh auth login
    gh auth refresh -s project,read:project
#>
[CmdletBinding()]
param(
    [switch]$Auditar,
    [switch]$DryRun,
    [switch]$Fechar,
    [switch]$Criar,
    [switch]$Tudo,
    [ValidateSet('issues', 'draft')]
    [string]$Modo = 'issues',
    [ValidateSet('1', '2')]
    [string]$Sprint,
    [ValidateSet('user_stories', 'tarefas', 'processo')]
    [string]$Secao
)

$ErrorActionPreference = 'Stop'

$Dono          = 'jacksoncassemiro'
$NumeroProjeto = 3
$Repo          = 'jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy'
$ArquivoItens  = Join-Path $PSScriptRoot 'board-itens.json'

if ($Tudo) { $Fechar = $true; $Criar = $true }

if (-not ($Auditar -or $Fechar -or $Criar)) {
    Write-Host @"
Nada a fazer. Escolha uma acao:

  -Auditar            mostra o que existe vs. o planejado (nao escreve)
  -Tudo -DryRun       mostra o que fecharia e criaria (nao escreve)   <- comece aqui
  -Tudo               fecha as 41 originais e cria os 82 novos
  -Fechar             so fecha as originais
  -Criar              so cria os novos
  -Criar -Secao processo   cria so os itens de QA/INFRA/DOCS

Ajuda completa:  Get-Help .\scripts\popular-board.ps1 -Full
"@ -ForegroundColor Yellow
    exit 0
}

if (-not (Test-Path $ArquivoItens)) {
    Write-Host "ERRO: $ArquivoItens nao encontrado." -ForegroundColor Red
    exit 1
}

$dados = Get-Content $ArquivoItens -Raw -Encoding UTF8 | ConvertFrom-Json

# ─────────────────────────────────────────────────────────────
# Pre-requisitos
# ─────────────────────────────────────────────────────────────
if (-not $DryRun) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Host @"
ERRO: GitHub CLI (gh) nao encontrado.
  winget install --id GitHub.cli
  gh auth login
  gh auth refresh -s project,read:project
Depois abra um terminal NOVO (para o PATH atualizar).
"@ -ForegroundColor Red
        exit 1
    }
    gh auth status *>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "ERRO: rode 'gh auth login'." -ForegroundColor Red; exit 1 }

    gh project view $NumeroProjeto --owner $Dono *>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: sem acesso ao Project. Rode: gh auth refresh -s project,read:project" -ForegroundColor Red
        exit 1
    }
}

# ─────────────────────────────────────────────────────────────
# Estado atual
# ─────────────────────────────────────────────────────────────
$TitulosExistentes = @()
$AbertasPorNumero  = @{}

if (-not $DryRun) {
    Write-Host '==> Lendo o estado atual do repositorio...' -ForegroundColor Cyan

    $abertas = gh issue list --repo $Repo --state open --limit 500 --json number,title | ConvertFrom-Json
    foreach ($i in $abertas) { $AbertasPorNumero[[int]$i.number] = $i.title }

    $todas   = @(gh issue list --repo $Repo --state all --limit 500 --json title --jq '.[].title' 2>$null)
    $noBoard = @(gh project item-list $NumeroProjeto --owner $Dono --limit 500 --format json --jq '.items[].content.title' 2>$null)
    $TitulosExistentes = @($todas + $noBoard) | Where-Object { $_ } | Sort-Object -Unique

    Write-Host "    $($abertas.Count) issues abertas · $($todas.Count) no total · $($noBoard.Count) itens no board" -ForegroundColor DarkGray
}

function Test-JaExiste([string]$Titulo) { return $TitulosExistentes -contains $Titulo }

function Get-ItensParaCriar {
    $lista = @()
    foreach ($secao in 'user_stories', 'tarefas', 'processo') {
        if ($Secao -and $Secao -ne $secao) { continue }
        foreach ($i in $dados.$secao) {
            if ($Sprint -and $i.sprint -ne $Sprint) { continue }
            $lista += [pscustomobject]@{ Secao = $secao; Sprint = $i.sprint; Tipo = $i.tipo; Titulo = $i.titulo; Corpo = $i.corpo }
        }
    }
    return $lista
}

$LabelsPorTipo = @{
    US = 'user-story'; BACKEND = 'tarefa,backend'; FRONTEND = 'tarefa,frontend'
    QA = 'tarefa,qa';  INFRA   = 'tarefa,infra';   DOCS     = 'tarefa,documentacao'
}

# ─────────────────────────────────────────────────────────────
# Auditoria
# ─────────────────────────────────────────────────────────────
if ($Auditar) {
    Write-Host "`n════ ISSUES ABERTAS HOJE ════" -ForegroundColor Cyan
    gh issue list --repo $Repo --state open --limit 500 `
        --json number,title,labels `
        --template '{{range .}}#{{.number}}  {{.title}}{{if .labels}}  [{{range .labels}}{{.name}} {{end}}]{{else}}  (sem label){{end}}{{"\n"}}{{end}}'

    Write-Host "`n════ A FECHAR (originais sem rastreabilidade) ════" -ForegroundColor Cyan
    $aFechar = 0
    foreach ($o in $dados.issues_a_fechar) {
        if ($AbertasPorNumero.ContainsKey([int]$o.numero)) {
            Write-Host ("  #{0,-3} {1}" -f $o.numero, $o.titulo) -ForegroundColor Yellow
            $aFechar++
        }
    }
    Write-Host "  -> $aFechar de $($dados.issues_a_fechar.Count) ainda abertas" -ForegroundColor DarkGray

    Write-Host "`n════ A CRIAR ════" -ForegroundColor Cyan
    foreach ($secao in 'user_stories', 'tarefas', 'processo') {
        $novos = @($dados.$secao | Where-Object { -not (Test-JaExiste $_.titulo) })
        Write-Host ("  {0,-14} {1,3} de {2,3} ainda nao existem" -f $secao, $novos.Count, $dados.$secao.Count)
    }

    Write-Host "`n════ COBERTURA DAS USER STORIES (apos recriar) ════" -ForegroundColor Cyan
    foreach ($us in '00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15') {
        $qtd = @($dados.tarefas | Where-Object { $_.titulo -like "[[]US-$us]*" }).Count
        $temUS = @($dados.user_stories | Where-Object { $_.titulo -like "US-$us*" }).Count
        Write-Host ("  US-{0}  {1} tarefa(s) + {2} item guarda-chuva" -f $us, $qtd, $temUS) -ForegroundColor Green
    }
    exit 0
}

# ─────────────────────────────────────────────────────────────
# Fechar as originais
# ─────────────────────────────────────────────────────────────
if ($Fechar) {
    Write-Host "`n════ FECHANDO AS ISSUES ORIGINAIS ════" -ForegroundColor Cyan

    $justificativa = @'
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
'@

    $fechadas = 0; $jaFechadas = 0
    foreach ($o in $dados.issues_a_fechar) {
        $numero = [int]$o.numero

        if (-not $DryRun -and -not $AbertasPorNumero.ContainsKey($numero)) {
            $jaFechadas++
            Write-Host ("  --  #{0} ja esta fechada" -f $numero) -ForegroundColor DarkGray
            continue
        }

        if ($DryRun) {
            Write-Host ("  [dry] fecharia #{0,-3} {1}" -f $numero, $o.titulo)
            continue
        }

        gh issue comment $numero --repo $Repo --body $justificativa *>$null
        gh issue close $numero --repo $Repo --reason 'not planned' *>$null

        if ($LASTEXITCODE -eq 0) {
            $fechadas++
            Write-Host ("  ok  fechada #{0,-3} {1}" -f $numero, $o.titulo) -ForegroundColor Green
        }
        else {
            Write-Host ("  !!  falhou #{0}" -f $numero) -ForegroundColor Red
        }
    }

    if (-not $DryRun) {
        Write-Host "`n  $fechadas fechadas, $jaFechadas ja estavam fechadas." -ForegroundColor Cyan
    }
}

# ─────────────────────────────────────────────────────────────
# Criar os novos
# ─────────────────────────────────────────────────────────────
if ($Criar) {
    $itens = Get-ItensParaCriar
    $filtros = @()
    if ($Sprint) { $filtros += "Sprint $Sprint" }
    if ($Secao)  { $filtros += $Secao }
    $sufixo = if ($filtros) { " (" + ($filtros -join ', ') + ")" } else { '' }

    Write-Host "`n════ CRIANDO OS ITENS ($Modo)$sufixo ════" -ForegroundColor Cyan
    if ($DryRun) { Write-Host '  DRY RUN - nada sera criado' -ForegroundColor Yellow }

    $criados = 0; $pulados = 0
    foreach ($item in $itens) {
        if ($DryRun) {
            Write-Host ("  [dry] [S{0}] {1,-8} {2}" -f $item.Sprint, $item.Tipo, $item.Titulo)
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
            $labels = $LabelsPorTipo[$item.Tipo]
            $url = gh issue create --repo $Repo --title $item.Titulo --body $item.Corpo --label $labels 2>$null
            if ($LASTEXITCODE -ne 0 -or -not $url) {
                Write-Host ("  ..  label ausente, criando sem label: {0}" -f $item.Titulo) -ForegroundColor DarkYellow
                $url = gh issue create --repo $Repo --title $item.Titulo --body $item.Corpo
            }
            if ($url) { gh project item-add $NumeroProjeto --owner $Dono --url $url *>$null }
        }

        if ($LASTEXITCODE -eq 0) {
            $criados++
            $TitulosExistentes += $item.Titulo
            Write-Host ("  ok  [S{0}] {1}" -f $item.Sprint, $item.Titulo) -ForegroundColor Green
        }
        else {
            Write-Host ("  !!  falhou: {0}" -f $item.Titulo) -ForegroundColor Red
        }
    }

    if ($DryRun) {
        Write-Host "`n  $($itens.Count) itens seriam criados." -ForegroundColor Cyan
    }
    else {
        Write-Host "`n  $criados criados, $pulados pulados por ja existirem." -ForegroundColor Cyan
        Write-Host "  Board: https://github.com/users/$Dono/projects/$NumeroProjeto" -ForegroundColor Cyan
    }
}

if (-not $DryRun -and $Criar) {
    Write-Host @"

Proximos passos manuais no board:
  1. Colunas: To Do -> In Dev -> Code Review -> In QA -> UAT -> Done
  2. Mover para "In Dev" so o que a pessoa esta fazendo AGORA. WIP maximo 2 por pessoa.
  3. Cada um se atribui ao puxar o item (quem puxa, assume).
  4. Preencher Priority e Size nos itens da Sprint 1.
  5. Os itens "US-XX:" sao guarda-chuva: o PO move para UAT e valida os criterios de aceite.
     As tarefas "[US-XX] [AREA]" sao a execucao.
"@ -ForegroundColor DarkGray
}
