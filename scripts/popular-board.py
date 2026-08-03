#!/usr/bin/env python3
"""Limpa e recria o board do projeto (GitHub Projects nº 3).

Implementacao unica em Python — os arquivos .ps1 e .sh sao so atalhos que chamam
este script. Isso evita manter a mesma logica em tres linguagens (que foi a fonte
dos erros silenciosos no PowerShell).

Pre-requisitos
--------------
    gh auth login
    gh auth refresh -s project,read:project      # escopo de Projects, obrigatorio
    python scripts/gerar-board-itens.py          # gera scripts/board-itens.json

Uso
---
    python scripts/popular-board.py --auditar               # so mostra o diagnostico
    python scripts/popular-board.py --tudo --dry-run        # confira ANTES de escrever
    python scripts/popular-board.py --tudo                  # limpa e recria
    python scripts/popular-board.py --limpar                # so limpa
    python scripts/popular-board.py --criar                 # so cria
    python scripts/popular-board.py --criar --secao processo
    python scripts/popular-board.py --criar --sprint 1
    python scripts/popular-board.py --tudo --apagar         # DELETA em vez de fechar

Seguranca
---------
* Sem nenhuma flag, o script NAO FAZ NADA e mostra as opcoes. De proposito.
* Itens cujo Status no board seja UAT ou Done sao SEMPRE preservados.
* Issues com label bug / funcionalidade / melhoria nunca sao tocadas.
* Idempotente: pula titulo que ja existe e issue ja fechada. Se falhar no meio,
  rode de novo — ele continua de onde parou.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ITENS = RAIZ / "scripts" / "board-itens.json"

REPO = "jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy"
OWNER = "jacksoncassemiro"
PROJETO = "6"

# Labels que marcam issue aberta pela equipe fora do planejamento — nunca tocar.
LABELS_INTOCAVEIS = {"bug", "funcionalidade", "melhoria"}

# Labels que marcam item gerado pelo planejamento — candidato a limpeza.
LABELS_PLANEJAMENTO = {"user-story", "tarefa"}

LABEL_POR_TIPO = {
    "US": ["user-story"],
    "BACKEND": ["tarefa", "backend"],
    "FRONTEND": ["tarefa", "frontend"],
    "QA": ["tarefa", "qa"],
    "INFRA": ["tarefa", "infra"],
    "DOCS": ["tarefa", "documentacao"],
}

COMENTARIO_FECHAMENTO = """Fechada no **rebaseline de escopo de 30/07/2026**, não descartada.

O planejamento anterior tinha 82 itens para 8 dias úteis e 6 pessoas. O escopo foi reduzido às
13 funcionalidades do enunciado mais autenticação, e as atividades foram reescritas para serem
**autocontidas** — critério de aceite, texto integral das regras de negócio e Definition of Done
dentro do próprio corpo da issue, em vez de espalhados por `docs/`.

O conteúdo desta issue foi preservado e reaproveitado na atividade equivalente do board novo.
Se o assunto dela ficou fora do MVP, ele está registrado com justificativa e versão-alvo em
[`docs/15-melhorias-futuras.md`](../blob/develop/docs/15-melhorias-futuras.md).

Justificativa completa: [`ADR-008`](../blob/develop/docs/adr/ADR-008-rebaseline-escopo.md)."""

VERDE, AMARELO, VERMELHO, CINZA, RESET = (
    "\033[32m", "\033[33m", "\033[31m", "\033[90m", "\033[0m"
)
if sys.platform == "win32":
    try:
        import ctypes

        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7
        )
    except Exception:  # pragma: no cover
        VERDE = AMARELO = VERMELHO = CINZA = RESET = ""


def ok(msg):
    print(f"  {VERDE}ok{RESET}    {msg}")


def pular(msg):
    print(f"  {CINZA}pula{RESET}  {msg}")


def aviso(msg):
    print(f"  {AMARELO}!{RESET}     {msg}")


def erro(msg):
    print(f"  {VERMELHO}ERRO{RESET}  {msg}")


def gh(*args, entrada=None, silencioso=False):
    """Roda o gh CLI e devolve stdout. Levanta em caso de erro."""
    proc = subprocess.run(
        ["gh", *args],
        input=entrada,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        if not silencioso:
            erro(f"gh {' '.join(args[:3])} ... falhou: {proc.stderr.strip()[:300]}")
        raise RuntimeError(proc.stderr)
    return proc.stdout


def checar_ambiente():
    if shutil.which("gh") is None:
        erro("GitHub CLI (gh) nao encontrado no PATH.")
        print("      Instale com:  winget install --id GitHub.cli")
        print("      Depois:       gh auth login")
        sys.exit(1)
    try:
        gh("auth", "status", silencioso=True)
    except RuntimeError:
        erro("gh nao esta autenticado. Rode:  gh auth login")
        sys.exit(1)
    if not ITENS.exists():
        erro(f"{ITENS.name} nao existe. Rode:  python scripts/gerar-board-itens.py")
        sys.exit(1)


def carregar_planejado():
    dados = json.loads(ITENS.read_text(encoding="utf-8"))
    itens = []
    for secao in ("user_stories", "tarefas", "processo"):
        for it in dados.get(secao, []):
            itens.append({**it, "secao": secao})
    return dados, itens


def listar_issues_abertas():
    bruto = gh(
        "issue", "list", "--repo", REPO, "--state", "open", "--limit", "400",
        "--json", "number,title,labels,url",
    )
    issues = json.loads(bruto)
    for i in issues:
        i["labels"] = {lbl["name"] for lbl in i.get("labels", [])}
    return issues


def listar_itens_do_board():
    """Devolve {numero_da_issue: {'status': ..., 'item_id': ...}}."""
    try:
        bruto = gh(
            "project", "item-list", PROJETO, "--owner", OWNER,
            "--format", "json", "--limit", "400", silencioso=True,
        )
    except RuntimeError:
        aviso("Nao consegui ler o board (falta escopo 'project'?).")
        aviso("Rode:  gh auth refresh -s project,read:project")
        aviso("Seguindo sem checar Status — NADA sera fechado por seguranca.")
        return None
    dados = json.loads(bruto)
    mapa = {}
    for item in dados.get("items", []):
        conteudo = item.get("content") or {}
        numero = conteudo.get("number")
        if numero is None:
            continue
        mapa[numero] = {
            "status": (item.get("status") or "").strip(),
            "item_id": item.get("id"),
        }
    return mapa


# ---------------------------------------------------------------- auditoria
def auditar(planejado, issues, board):
    titulos_planejados = {i["titulo"] for i in planejado}
    titulos_existentes = {i["title"] for i in issues}
    preservar = set(
        json.loads(ITENS.read_text(encoding="utf-8")).get(
            "preservar_status", ["UAT", "Done"]
        )
    )

    a_criar = [i for i in planejado if i["titulo"] not in titulos_existentes]
    ja_existem = [i for i in planejado if i["titulo"] in titulos_existentes]

    obsoletas, preservadas, ignoradas = [], [], []
    for iss in issues:
        if iss["title"] in titulos_planejados:
            continue
        if iss["labels"] & LABELS_INTOCAVEIS:
            ignoradas.append(iss)
            continue
        if not (iss["labels"] & LABELS_PLANEJAMENTO):
            ignoradas.append(iss)
            continue
        status = (board or {}).get(iss["number"], {}).get("status", "")
        if board is None or status in preservar:
            preservadas.append((iss, status or "board nao lido"))
        else:
            obsoletas.append((iss, status or "sem status"))

    print()
    print("=" * 74)
    print("  AUDITORIA DO BOARD")
    print("=" * 74)
    print(f"  Planejado em board-itens.json ......... {len(planejado):>3}")
    print(f"  Issues abertas hoje ................... {len(issues):>3}")
    print()
    print(f"  {VERDE}A criar{RESET} .............................. {len(a_criar):>3}")
    print(f"  {CINZA}Ja existem (serao puladas){RESET} ........... {len(ja_existem):>3}")
    print(f"  {AMARELO}A limpar (fora do plano novo){RESET} ........ {len(obsoletas):>3}")
    print(f"  {VERDE}Preservadas (UAT/Done){RESET} ............... {len(preservadas):>3}")
    print(f"  {CINZA}Ignoradas (bug/feature/melhoria){RESET} ...... {len(ignoradas):>3}")
    print()

    if preservadas:
        print(f"  {VERDE}PRESERVADAS — nao serao tocadas{RESET}")
        for iss, status in preservadas:
            print(f"    #{iss['number']:<4} [{status:<10}] {iss['title'][:60]}")
        print()
    if obsoletas:
        print(f"  {AMARELO}SERAO FECHADAS E REMOVIDAS DO BOARD{RESET}")
        for iss, status in obsoletas[:15]:
            print(f"    #{iss['number']:<4} [{status:<10}] {iss['title'][:60]}")
        if len(obsoletas) > 15:
            print(f"    ... e mais {len(obsoletas) - 15}")
        print()
    if ignoradas:
        print(f"  {CINZA}IGNORADAS — bug, funcionalidade ou melhoria{RESET}")
        for iss in ignoradas[:10]:
            print(f"    #{iss['number']:<4} {iss['title'][:66]}")
        print()

    return a_criar, obsoletas, preservadas


# ------------------------------------------------------------------ limpeza
def limpar(obsoletas, board, dry_run, apagar):
    if not obsoletas:
        print("  Nada para limpar.")
        return
    print()
    print("-" * 74)
    print(f"  LIMPEZA — {len(obsoletas)} itens" + (" [DRY-RUN]" if dry_run else ""))
    print("-" * 74)
    for iss, _status in obsoletas:
        alvo = f"#{iss['number']} {iss['title'][:52]}"
        if dry_run:
            acao = "APAGARIA" if apagar else "fecharia + tiraria do board"
            pular(f"{acao}: {alvo}")
            continue
        try:
            if apagar:
                gh("issue", "delete", str(iss["number"]), "--repo", REPO, "--yes")
                ok(f"apagada: {alvo}")
                continue

            gh(
                "issue", "close", str(iss["number"]), "--repo", REPO,
                "--reason", "not planned", "--comment", COMENTARIO_FECHAMENTO,
            )
            item_id = (board or {}).get(iss["number"], {}).get("item_id")
            if item_id:
                try:
                    gh(
                        "project", "item-delete", PROJETO, "--owner", OWNER,
                        "--id", item_id, silencioso=True,
                    )
                except RuntimeError:
                    aviso(f"fechada, mas nao saiu do board: {alvo}")
                    continue
            ok(f"fechada e removida do board: {alvo}")
        except RuntimeError:
            erro(f"falhou: {alvo}")


# ------------------------------------------------------------------ criacao
def criar(a_criar, dry_run, secao=None, sprint=None):
    alvo = a_criar
    if secao:
        mapa = {"us": "user_stories", "tarefas": "tarefas", "processo": "processo"}
        alvo = [i for i in alvo if i["secao"] == mapa.get(secao, secao)]
    if sprint:
        alvo = [i for i in alvo if i["sprint"] == str(sprint)]

    if not alvo:
        print("  Nada para criar (tudo ja existe ou o filtro nao casou).")
        return

    print()
    print("-" * 74)
    print(f"  CRIACAO — {len(alvo)} itens" + (" [DRY-RUN]" if dry_run else ""))
    print("-" * 74)

    for item in alvo:
        labels = LABEL_POR_TIPO.get(item["tipo"], ["tarefa"])
        etiqueta = f"[S{item['sprint']}] {item['titulo'][:56]}"
        if dry_run:
            pular(f"criaria ({','.join(labels)}): {etiqueta}")
            continue
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".md", delete=False, encoding="utf-8"
            ) as fh:
                fh.write(item["corpo"])
                tmp = fh.name
            args = [
                "issue", "create", "--repo", REPO,
                "--title", item["titulo"], "--body-file", tmp,
            ]
            for lbl in labels:
                args += ["--label", lbl]
            url = gh(*args).strip().splitlines()[-1]
            try:
                gh(
                    "project", "item-add", PROJETO, "--owner", OWNER,
                    "--url", url, silencioso=True,
                )
                ok(f"criada e no board: {etiqueta}")
            except RuntimeError:
                aviso(f"criada, mas NAO entrou no board: {etiqueta}")
        except RuntimeError:
            erro(f"falhou: {etiqueta}")
        finally:
            if tmp:
                pathlib.Path(tmp).unlink(missing_ok=True)


# --------------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(
        description="Limpa e recria o board do projeto.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--auditar", action="store_true", help="so mostra o diagnostico")
    p.add_argument("--limpar", action="store_true", help="fecha os itens fora do plano")
    p.add_argument("--criar", action="store_true", help="cria os itens que faltam")
    p.add_argument("--tudo", action="store_true", help="limpar + criar")
    p.add_argument("--dry-run", action="store_true", help="mostra sem escrever nada")
    p.add_argument("--apagar", action="store_true",
                   help="DELETA a issue em vez de fechar (irreversivel)")
    p.add_argument("--secao", choices=["us", "tarefas", "processo"],
                   help="filtra a criacao por secao")
    p.add_argument("--sprint", choices=["1", "2"], help="filtra a criacao por sprint")
    args = p.parse_args()

    if not any([args.auditar, args.limpar, args.criar, args.tudo]):
        p.print_help()
        print()
        print("  Nenhuma acao pedida — nada foi feito, de proposito.")
        print("  Comece por:  python scripts/popular-board.py --auditar")
        return

    checar_ambiente()
    dados, planejado = carregar_planejado()
    issues = listar_issues_abertas()
    board = listar_itens_do_board()

    a_criar, obsoletas, _preservadas = auditar(planejado, issues, board)

    if args.auditar and not (args.limpar or args.criar or args.tudo):
        print("  Auditoria apenas. Nada foi alterado.")
        print("  Proximo passo:  python scripts/popular-board.py --tudo --dry-run")
        return

    if args.apagar and not args.dry_run:
        print()
        print(f"  {VERMELHO}ATENCAO:{RESET} --apagar DELETA as issues. E irreversivel.")
        resposta = input("  Digite APAGAR para confirmar: ").strip()
        if resposta != "APAGAR":
            print("  Cancelado.")
            return

    if args.limpar or args.tudo:
        limpar(obsoletas, board, args.dry_run, args.apagar)
    if args.criar or args.tudo:
        criar(a_criar, args.dry_run, args.secao, args.sprint)

    print()
    if args.dry_run:
        print("  DRY-RUN — nada foi escrito. Rode de novo sem --dry-run para aplicar.")
    else:
        print("  Pronto. Confira em:")
        print(f"  https://github.com/users/{OWNER}/projects/{PROJETO}/views/1")


if __name__ == "__main__":
    main()
