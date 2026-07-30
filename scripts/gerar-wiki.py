#!/usr/bin/env python3
"""Gera as paginas de wiki/ a partir de docs/.

docs/ e a fonte da verdade. Este script converte os links relativos entre arquivos
markdown nos links de pagina que o Wiki do GitHub espera, e aponta os links de
arquivos do repositorio para o blob no GitHub.

  python scripts/gerar-wiki.py            # gera
  python scripts/gerar-wiki.py --check    # falha se wiki/ estiver desatualizado

Home.md, _Sidebar.md, _Footer.md e README.md sao escritos a mao e preservados.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
WIKI = RAIZ / "wiki"

REPO = "https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy"
BLOB = f"{REPO}/blob/develop"

PRESERVADOS = {"Home.md", "_Sidebar.md", "_Footer.md", "README.md"}

PAGINAS = {
    "00-visao-do-produto.md": "Visao-do-Produto",
    "01-requisitos.md": "Requisitos",
    "02-backlog.md": "Backlog-e-User-Stories",
    "03-arquitetura.md": "Arquitetura",
    "04-modelo-de-dados.md": "Modelo-de-Dados",
    "05-clean-code.md": "Clean-Code-e-SOLID",
    "06-design-patterns.md": "Design-Patterns",
    "07-plano-de-testes.md": "Plano-de-Testes",
    "08-casos-de-teste.md": "Casos-de-Teste",
    "09-ci-cd.md": "CI-CD",
    "10-git-flow.md": "Git-Flow",
    "11-ciclo-desenvolvimento.md": "Ciclo-de-Desenvolvimento",
    "12-cronograma.md": "Cronograma",
    "13-papeis-e-responsabilidades.md": "Papeis-e-Responsabilidades",
    "14-conflitos-e-decisoes.md": "Conflitos-e-Decisoes",
}

ADRS = {
    "ADR-001-monorepo.md": "ADR-001-Monorepo",
    "ADR-002-camadas-mvc.md": "ADR-002-Camadas-MVC",
    "ADR-003-autenticacao.md": "ADR-003-Autenticacao",
    "ADR-004-bootstrap-atendente.md": "ADR-004-Bootstrap-do-Atendente",
    "ADR-005-cadastro-paciente.md": "ADR-005-Cadastro-de-Paciente",
    "ADR-006-design-patterns.md": "ADR-006-Design-Patterns",
    "ADR-007-vitest.md": "ADR-007-Vitest",
}

RODAPE = (
    "\n\n---\n\n"
    "> 📄 Esta página é gerada a partir de `docs/` no repositório. "
    "**Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.\n"
)

ARQUIVOS_DO_REPO = {
    "CLAUDE.md": f"{BLOB}/CLAUDE.md",
    ".github/workflows/ci.yml": f"{BLOB}/.github/workflows/ci.yml",
    ".github/pull_request_template.md": f"{BLOB}/.github/pull_request_template.md",
    ".claude/skills/": f"{BLOB}/.claude/skills",
}


def converter(texto: str) -> str:
    """Reescreve os links do markdown para o formato do Wiki."""
    for arquivo, pagina in PAGINAS.items():
        texto = texto.replace(f"](../{arquivo}", f"]({pagina}")
        texto = texto.replace(f"]({arquivo}", f"]({pagina}")

    for arquivo, pagina in ADRS.items():
        texto = texto.replace(f"](adr/{arquivo})", f"]({pagina})")
        texto = texto.replace(f"]({arquivo})", f"]({pagina})")

    texto = texto.replace("](adr/)", "](ADR-001-Monorepo)")
    texto = texto.replace("](adr/README.md)", "](ADR-001-Monorepo)")

    # ancora que sobrou com nome de arquivo
    texto = re.sub(
        r"\]\((?:\.\./)?(\d{2}-[a-z0-9-]+)\.md#",
        lambda m: "](" + PAGINAS.get(m.group(1) + ".md", m.group(1)) + "#",
        texto,
    )

    for relativo, absoluto in ARQUIVOS_DO_REPO.items():
        texto = texto.replace(f"](../../{relativo})", f"]({absoluto})")
        texto = texto.replace(f"](../{relativo})", f"]({absoluto})")

    for pasta in ("material-aulas", "evidencias", "apresentacao"):
        texto = texto.replace(f"]({pasta}/)", f"]({BLOB}/docs/{pasta})")

    return texto


def gerar() -> dict[str, str]:
    """Devolve {nome_do_arquivo: conteudo} das paginas geradas."""
    resultado: dict[str, str] = {}

    for arquivo, pagina in PAGINAS.items():
        origem = DOCS / arquivo
        if not origem.exists():
            print(f"AVISO: {origem} nao encontrado", file=sys.stderr)
            continue
        resultado[f"{pagina}.md"] = converter(origem.read_text(encoding="utf-8")) + RODAPE

    for arquivo, pagina in ADRS.items():
        origem = DOCS / "adr" / arquivo
        if not origem.exists():
            print(f"AVISO: {origem} nao encontrado", file=sys.stderr)
            continue
        resultado[f"{pagina}.md"] = converter(origem.read_text(encoding="utf-8")) + RODAPE

    return resultado


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="nao escreve; falha se wiki/ estiver desatualizado"
    )
    args = parser.parse_args()

    paginas = gerar()
    WIKI.mkdir(exist_ok=True)

    desatualizadas: list[str] = []
    for nome, conteudo in paginas.items():
        destino = WIKI / nome
        atual = destino.read_text(encoding="utf-8") if destino.exists() else None
        if atual == conteudo:
            continue
        desatualizadas.append(nome)
        if not args.check:
            destino.write_text(conteudo, encoding="utf-8")

    # remove paginas geradas que nao correspondem mais a nenhum doc
    esperadas = set(paginas) | PRESERVADOS
    orfas = [f.name for f in WIKI.glob("*.md") if f.name not in esperadas]
    for orfa in orfas:
        desatualizadas.append(f"{orfa} (orfa)")
        if not args.check:
            (WIKI / orfa).unlink()

    if args.check:
        if desatualizadas:
            print("wiki/ desatualizado. Rode: python scripts/gerar-wiki.py", file=sys.stderr)
            for nome in desatualizadas:
                print(f"  - {nome}", file=sys.stderr)
            return 1
        print(f"wiki/ em sincronia ({len(paginas)} paginas geradas + {len(PRESERVADOS)} manuais)")
        return 0

    if desatualizadas:
        print(f"{len(desatualizadas)} pagina(s) atualizada(s):")
        for nome in desatualizadas:
            print(f"  - {nome}")
    else:
        print("Nada a fazer: wiki/ ja esta em sincronia.")
    print(f"\nTotal: {len(paginas)} geradas + {len(PRESERVADOS)} escritas a mao")
    print("Publicar com: ./scripts/publicar-wiki.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
