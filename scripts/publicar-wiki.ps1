<#
.SYNOPSIS
  Publica as paginas de wiki/ no Wiki do GitHub. Versao Windows / PowerShell.

.DESCRIPTION
  O Wiki do GitHub e um repositorio git separado (<repo>.wiki.git). Este script
  clona, sincroniza o conteudo de wiki/ e faz push usando as suas credenciais git.

.EXAMPLE
  .\scripts\publicar-wiki.ps1 -DryRun
  .\scripts\publicar-wiki.ps1
#>
[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$Repo    = 'jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy'
$WikiUrl = "https://github.com/$Repo.wiki.git"
$Raiz    = Split-Path -Parent $PSScriptRoot
$Origem  = Join-Path $Raiz 'wiki'
$Tmp     = Join-Path ([System.IO.Path]::GetTempPath()) ("wiki-" + [guid]::NewGuid().ToString('N').Substring(0, 8))

function Limpar {
    if (Test-Path $Tmp) {
        Remove-Item $Tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "git nao encontrado no PATH. Instale o Git for Windows: https://git-scm.com/download/win"
    }

    if (-not (Test-Path $Origem)) {
        throw "Pasta nao encontrada: $Origem"
    }

    $paginas = Get-ChildItem -Path $Origem -Filter '*.md' | Where-Object { $_.Name -ne 'README.md' }
    if ($paginas.Count -eq 0) {
        throw "Nenhuma pagina .md em $Origem. Rode antes: .\scripts\gerar-wiki.ps1"
    }

    Write-Host "==> Clonando o wiki de $Repo" -ForegroundColor Cyan
    git clone --quiet $WikiUrl $Tmp 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host @"
ERRO: nao foi possivel clonar o wiki.

Causas comuns:
    1. O Wiki nunca foi inicializado. Crie a primeira pagina pela interface web
         (aba Wiki -> Create the first page) e rode este script de novo.
    2. O Git nao conseguiu autenticar o clone via HTTPS. Verifique se voce tem
         acesso ao repositorio e tente novamente.
         Se voce preferir SSH, troque a variavel `$WikiUrl` deste script por:
             git@github.com:$Repo.wiki.git
"@ -ForegroundColor Red
        exit 1
    }

    Write-Host "==> Sincronizando $($paginas.Count) paginas" -ForegroundColor Cyan
    # Remove os .md antigos (mantem .git) e copia os novos.
    Get-ChildItem -Path $Tmp -Filter '*.md' | Remove-Item -Force
    foreach ($pagina in $paginas) {
        Copy-Item $pagina.FullName -Destination $Tmp -Force
    }

    Push-Location $Tmp
    try {
        $mudancas = git status --porcelain
        if ([string]::IsNullOrWhiteSpace($mudancas)) {
            Write-Host "==> Nada mudou. Wiki ja esta atualizado." -ForegroundColor Green
            exit 0
        }

        Write-Host "==> Alteracoes:" -ForegroundColor Cyan
        git add -A
        git status --short

        if ($DryRun) {
            Write-Host "`n==> -DryRun: nada foi publicado." -ForegroundColor Yellow
            exit 0
        }

        $nome  = git config --global user.name
        $email = git config --global user.email
        if ([string]::IsNullOrWhiteSpace($nome))  { $nome  = 'Equipe 01' }
        if ([string]::IsNullOrWhiteSpace($email)) { $email = 'equipe01@example.com' }

        git -c "user.name=$nome" -c "user.email=$email" commit --quiet -m 'docs(wiki): sincroniza paginas a partir de wiki/'
        git push --quiet origin HEAD
        if ($LASTEXITCODE -ne 0) { throw 'git push falhou' }

        Write-Host "`n==> Publicado: https://github.com/$Repo/wiki" -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
}
finally {
    Limpar
}
