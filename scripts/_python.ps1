<#
.SYNOPSIS
  Encontra um Python que REALMENTE funciona. Usado pelos outros .ps1 via dot-source.

.DESCRIPTION
  O Windows instala um atalho falso em
      %LOCALAPPDATA%\Microsoft\WindowsApps\python.exe
  (o "App Execution Alias"). Ele existe no PATH, o `Get-Command python` o encontra,
  mas ao ser executado ele apenas imprime

      "Python was not found; run without arguments to install from the Microsoft Store..."

  e nao roda nada. Por isso NAO basta checar se o comando existe: e preciso executar
  `--version` e conferir a saida.

  Ordem de preferencia:
    1. py -3      -> Python Launcher, instalado junto com o Python do python.org
    2. python3
    3. python

  Candidatos cujo caminho esteja dentro de WindowsApps sao descartados de saida.
#>

function Get-PythonCommand {
    [CmdletBinding()]
    param()

    $candidatos = @(
        @{ Exe = 'py';      Args = @('-3') }
        @{ Exe = 'python3'; Args = @() }
        @{ Exe = 'python';  Args = @() }
    )

    foreach ($c in $candidatos) {
        $cmd = Get-Command $c.Exe -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }

        # Descarta o atalho da Microsoft Store.
        if ($cmd.Source -and $cmd.Source -like '*\WindowsApps\*') {
            Write-Verbose "Ignorando atalho da Microsoft Store: $($cmd.Source)"
            continue
        }

        # Testa de verdade: so vale se `--version` responder com "Python X.Y.Z".
        try {
            $saida = & $c.Exe @($c.Args + '--version') 2>&1 | Out-String
        } catch {
            continue
        }
        if ($LASTEXITCODE -eq 0 -and $saida -match 'Python\s+3\.(\d+)') {
            $minor = [int]$Matches[1]
            if ($minor -lt 9) {
                Write-Verbose "Python 3.$minor e antigo demais, procurando outro."
                continue
            }
            return @{
                Exe     = $c.Exe
                Args    = $c.Args
                Versao  = $saida.Trim()
                Caminho = $cmd.Source
            }
        }
    }

    return $null
}

function Assert-Python {
    <#
      Devolve o Python encontrado ou encerra o script com uma mensagem util.
    #>
    [CmdletBinding()]
    param()

    $py = Get-PythonCommand
    if ($py) { return $py }

    Write-Host ''
    Write-Host '  ERRO: Python 3.9+ nao encontrado.' -ForegroundColor Red
    Write-Host ''
    Write-Host '  Se apareceu a mensagem "Python was not found; run without arguments to'
    Write-Host '  install from the Microsoft Store", o que voce tem no PATH e um ATALHO'
    Write-Host '  falso do Windows, nao o Python.'
    Write-Host ''
    Write-Host '  Como resolver (escolha um):' -ForegroundColor Yellow
    Write-Host ''
    Write-Host '  1) Instalar o Python de verdade (recomendado):'
    Write-Host '       winget install --id Python.Python.3.12' -ForegroundColor Cyan
    Write-Host '     Feche e abra o terminal. Confira com:  py -3 --version'
    Write-Host ''
    Write-Host '  2) Desligar o atalho falso:'
    Write-Host '       Configuracoes > Aplicativos > Configuracoes avancadas de aplicativos'
    Write-Host '       > Aliases de execucao de aplicativo  ->  desligue "python.exe" e "python3.exe"'
    Write-Host ''
    Write-Host '  Este script precisa de Python porque a fonte dos itens do board e'
    Write-Host '  gerada por scripts/gerar-board-itens.py. O mesmo vale para'
    Write-Host '  scripts/gerar-wiki.py.'
    Write-Host ''
    exit 1
}
