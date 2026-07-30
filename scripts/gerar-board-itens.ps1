<#
.SYNOPSIS
  Atalho para scripts/gerar-board-itens.py. Gera scripts/board-itens.json.

.EXAMPLE
  .\scripts\gerar-board-itens.ps1
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_python.ps1')
$py = Assert-Python

& $py.Exe @($py.Args + (Join-Path $PSScriptRoot 'gerar-board-itens.py'))
exit $LASTEXITCODE
