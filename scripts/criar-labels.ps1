<#
.SYNOPSIS
  Cria as labels usadas pelos templates de Issue. Versao Windows / PowerShell.

.EXAMPLE
  .\scripts\criar-labels.ps1
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Repo = 'jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy'

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host @"
ERRO: GitHub CLI (gh) nao encontrado.
  winget install --id GitHub.cli
  gh auth login
Depois abra um terminal NOVO e rode de novo.
"@ -ForegroundColor Red
    exit 1
}

$labels = @(
    @{ Nome = 'user-story';   Cor = '0E8A16'; Desc = 'User Story do backlog' }
    @{ Nome = 'tarefa';       Cor = '1D76DB'; Desc = 'Tarefa tecnica' }
    @{ Nome = 'backend';      Cor = '5319E7'; Desc = 'FastAPI, SQLAlchemy, Alembic' }
    @{ Nome = 'frontend';     Cor = 'FBCA04'; Desc = 'Next.js, React, Mantine' }
    @{ Nome = 'qa';           Cor = '006B75'; Desc = 'Testes, evidencias, CI' }
    @{ Nome = 'infra';        Cor = 'C5DEF5'; Desc = 'Docker, ambiente, configuracao' }
    @{ Nome = 'documentacao'; Cor = '0075CA'; Desc = 'Documentacao e ADR' }
    @{ Nome = 'bug';             Cor = 'D73A4A'; Desc = 'Defeito encontrado em teste ou uso' }
    @{ Nome = 'funcionalidade';  Cor = 'A2EEEF'; Desc = 'Capacidade nova solicitada - passa pelo PO' }
    @{ Nome = 'melhoria';        Cor = '7057FF'; Desc = 'Otimizacao de algo que ja existe' }
    @{ Nome = 'tech-debt';       Cor = 'E99695'; Desc = 'Debito tecnico / antipadrao a refatorar' }
    @{ Nome = 'blocked';         Cor = 'B60205'; Desc = 'Impedimento registrado' }
    @{ Nome = 'p0';              Cor = 'B60205'; Desc = 'Nao corta - sustenta RN obrigatoria' }
    @{ Nome = 'p1';              Cor = 'FBCA04'; Desc = 'Completa fluxo - corta depois' }
    @{ Nome = 'p2';              Cor = 'BFDADC'; Desc = 'Corta primeiro se o prazo apertar' }
    @{ Nome = 'melhoria-futura'; Cor = 'D4C5F9'; Desc = 'Fora do MVP - ver docs/15-melhorias-futuras.md' }
)

Write-Host "==> Criando labels em $Repo" -ForegroundColor Cyan
foreach ($l in $labels) {
    gh label create $l.Nome --repo $Repo --color $l.Cor --description $l.Desc --force *>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ok  $($l.Nome)" -ForegroundColor Green
    } else {
        Write-Host "  !!  falhou: $($l.Nome)" -ForegroundColor Red
    }
}
Write-Host '==> Pronto.' -ForegroundColor Green
