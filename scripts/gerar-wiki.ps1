<#
.SYNOPSIS
  Atalho para scripts/gerar-wiki.py. Gera wiki/ a partir de docs/.

.EXAMPLE
  .\scripts\gerar-wiki.ps1
.EXAMPLE
  .\scripts\gerar-wiki.ps1 -Check
#>
[CmdletBinding()]
param(
    [switch] $Check
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_python.ps1')
$py = Assert-Python

$argumentos = @($py.Args) + @(Join-Path $PSScriptRoot 'gerar-wiki.py')
if ($Check) { $argumentos += '--check' }

& $py.Exe @argumentos
exit $LASTEXITCODE
