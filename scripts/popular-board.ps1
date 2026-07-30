<#
.SYNOPSIS
  Atalho para scripts/popular-board.py. Windows / PowerShell.

.DESCRIPTION
  A logica de verdade esta em popular-board.py. Motivo: a fonte dos itens
  (scripts/board-itens.json) e gerada por scripts/gerar-board-itens.py, entao Python
  ja e pre-requisito do fluxo do board. Manter uma segunda implementacao em PowerShell
  significaria duas copias da mesma logica divergindo entre si.

  Pre-requisitos:
      winget install --id Python.Python.3.12
      winget install --id GitHub.cli
      gh auth login
      gh auth refresh -s project,read:project
      py -3 scripts\gerar-board-itens.py

.EXAMPLE
  .\scripts\popular-board.ps1 -Auditar
.EXAMPLE
  .\scripts\popular-board.ps1 -Tudo -DryRun
.EXAMPLE
  .\scripts\popular-board.ps1 -Tudo
.EXAMPLE
  .\scripts\popular-board.ps1 -Criar -Secao processo
#>
[CmdletBinding()]
param(
    [switch] $Auditar,
    [switch] $Limpar,
    [switch] $Criar,
    [switch] $Tudo,
    [switch] $DryRun,
    [switch] $Apagar,
    [ValidateSet('us', 'tarefas', 'processo')] [string] $Secao,
    [ValidateSet('1', '2')] [string] $Sprint
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_python.ps1')
$py = Assert-Python
Write-Verbose "Usando $($py.Versao) em $($py.Caminho)"

$script = Join-Path $PSScriptRoot 'popular-board.py'

$argumentos = @($py.Args) + @($script)
if ($Auditar) { $argumentos += '--auditar' }
if ($Limpar)  { $argumentos += '--limpar' }
if ($Criar)   { $argumentos += '--criar' }
if ($Tudo)    { $argumentos += '--tudo' }
if ($DryRun)  { $argumentos += '--dry-run' }
if ($Apagar)  { $argumentos += '--apagar' }
if ($Secao)   { $argumentos += @('--secao', $Secao) }
if ($Sprint)  { $argumentos += @('--sprint', $Sprint) }

& $py.Exe @argumentos
exit $LASTEXITCODE
