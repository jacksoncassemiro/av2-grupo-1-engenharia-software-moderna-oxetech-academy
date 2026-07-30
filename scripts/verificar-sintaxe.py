#!/usr/bin/env python3
"""Verificacao de sintaxe dos scripts de automacao, sem precisar de PowerShell.

Motivacao: o ambiente onde os scripts sao escritos nem sempre tem `pwsh` instalado,
e um `.ps1` com chave ou parentese desbalanceado falha em tempo de execucao - as vezes
em SILENCIO, dependendo da politica de execucao do Windows. Este script faz uma checagem
estrutural barata que pega esse tipo de erro antes de rodar.

O que ele trata (e o que uma checagem ingenua de `contar chaves` erra):

  - here-strings `@"..."@` e `@'...'@`, cujo terminador pode ter codigo depois
    (ex.: `"@ -ForegroundColor Yellow`)
  - comentarios de bloco `<# ... #>` (o bloco de ajuda dos scripts)
  - comentarios de linha `#`
  - strings simples e duplas, com escape

Nao substitui um parser de verdade: valida balanceamento, nao semantica.

  python scripts/verificar-sintaxe.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def analisar_powershell(caminho: Path) -> list[str]:
    """Devolve a lista de problemas estruturais encontrados no .ps1."""
    problemas: list[str] = []
    chaves = parenteses = colchetes = 0
    terminador_here: str | None = None
    em_bloco_de_comentario = False

    for numero, original in enumerate(caminho.read_text(encoding="utf-8").split("\n"), 1):
        linha = original

        # here-string aberta: só o terminador no início da linha encerra
        if terminador_here is not None:
            if linha.startswith(terminador_here):
                linha = linha[len(terminador_here) :]
                terminador_here = None
            else:
                continue

        # comentário de bloco <# ... #>
        if em_bloco_de_comentario:
            if "#>" in linha:
                linha = linha.split("#>", 1)[1]
                em_bloco_de_comentario = False
            else:
                continue
        while "<#" in linha:
            antes, depois = linha.split("<#", 1)
            if "#>" in depois:
                linha = antes + depois.split("#>", 1)[1]
            else:
                linha = antes
                em_bloco_de_comentario = True
                break

        # abertura de here-string no fim da linha
        abertura = re.search(r"@(\"|')\s*$", linha)
        if abertura:
            terminador_here = abertura.group(1) + "@"
            linha = linha[: abertura.start()]

        # strings e comentário de linha
        linha = re.sub(r'"(?:[^"\\]|\\.)*"', '""', linha)
        linha = re.sub(r"'(?:[^'])*'", "''", linha)
        linha = re.sub(r"#.*", "", linha)

        chaves += linha.count("{") - linha.count("}")
        parenteses += linha.count("(") - linha.count(")")
        colchetes += linha.count("[") - linha.count("]")

        for nome, saldo in (("chave", chaves), ("parentese", parenteses), ("colchete", colchetes)):
            if saldo < 0:
                problemas.append(f"L{numero}: {nome} fechado sem abertura")

    if terminador_here is not None:
        problemas.append(f"here-string {terminador_here} nunca fechada")
    if em_bloco_de_comentario:
        problemas.append("comentário de bloco <# nunca fechado")
    for nome, saldo in (("chaves", chaves), ("parênteses", parenteses), ("colchetes", colchetes)):
        if saldo:
            problemas.append(f"{nome} desbalanceados: {saldo:+d}")

    return problemas


def analisar_bash(caminho: Path) -> list[str]:
    processo = subprocess.run(
        ["bash", "-n", str(caminho)], capture_output=True, text=True, check=False
    )
    return [] if processo.returncode == 0 else [processo.stderr.strip()]


def main() -> int:
    houve_erro = False

    for caminho in sorted(RAIZ.glob("*.ps1")):
        problemas = analisar_powershell(caminho)
        marca = "ok " if not problemas else "!! "
        print(f"  {marca} {caminho.name}")
        for problema in problemas:
            print(f"        {problema}")
        houve_erro = houve_erro or bool(problemas)

    for caminho in sorted(RAIZ.glob("*.sh")):
        problemas = analisar_bash(caminho)
        marca = "ok " if not problemas else "!! "
        print(f"  {marca} {caminho.name}")
        for problema in problemas:
            print(f"        {problema}")
        houve_erro = houve_erro or bool(problemas)

    for caminho in sorted(RAIZ.glob("*.py")):
        if caminho.name == Path(__file__).name:
            continue
        processo = subprocess.run(
            [sys.executable, "-m", "py_compile", str(caminho)],
            capture_output=True,
            text=True,
            check=False,
        )
        problemas = [] if processo.returncode == 0 else [processo.stderr.strip()]
        print(f"  {'ok ' if not problemas else '!! '} {caminho.name}")
        for problema in problemas:
            print(f"        {problema}")
        houve_erro = houve_erro or bool(problemas)

    print()
    if houve_erro:
        print("Há problemas de sintaxe. Corrija antes de rodar os scripts.")
        return 1
    print("Todos os scripts passaram na verificação estrutural.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
