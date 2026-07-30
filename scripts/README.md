# Scripts

Cada script existe em **duas versões**: `.ps1` (Windows / PowerShell) e `.sh` (Linux, macOS,
Git Bash / WSL). Fazem exatamente a mesma coisa.

## ⚠️ Windows: leia isto primeiro

Duas coisas fazem o script "não fazer nada":

**1. Você rodou o `.sh` no PowerShell.** O PowerShell não executa shell script. Use o `.ps1`:

```powershell
.\scripts\popular-board.ps1 -Auditar     # ✅ certo no Windows
./scripts/popular-board.sh --auditar     # ❌ só funciona no Git Bash / WSL
```

**2. A política de execução do PowerShell bloqueia scripts.** Por padrão o Windows recusa
executar `.ps1` e, em algumas configurações, falha **silenciosamente**. Libere só para a sessão
atual (não muda nada permanentemente na máquina):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Ou, sem alterar política nenhuma, invoque direto:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\popular-board.ps1 -Auditar
```

Para conferir se o script foi mesmo lido, rode com `-Verbose`. Se não sair **nada**, é a
política de execução.

---

## Pré-requisito: GitHub CLI

Os scripts de board e labels usam o `gh`:

```powershell
winget install --id GitHub.cli
# feche e abra o terminal para o PATH atualizar
gh auth login
gh auth refresh -s project,read:project     # escopo de Projects, obrigatório
```

Confira: `gh auth status` e `gh project view 3 --owner jacksoncassemiro`

O `publicar-wiki` usa apenas **git** (que você já tem).

---

## `popular-board` — auditar e popular o Kanban

```powershell
.\scripts\popular-board.ps1 -Auditar                 # ⭐ COMECE AQUI
.\scripts\popular-board.ps1 -DryRun                  # lista o que criaria
.\scripts\popular-board.ps1                          # cria draft items
.\scripts\popular-board.ps1 -Modo issues             # cria Issues + adiciona ao board
.\scripts\popular-board.ps1 -Sprint 1                # só a Sprint 1
```

```bash
./scripts/popular-board.sh --auditar
./scripts/popular-board.sh --dry-run
./scripts/popular-board.sh
./scripts/popular-board.sh --issues
./scripts/popular-board.sh --sprint 1
```

### ⚠️ O board já está populado

A equipe já criou **41 issues** a partir das tarefas da Wiki (US-00 a US-12), com títulos no
padrão `[US-00] [BACKEND] Endpoint de Login`. O script é **idempotente** (pula título repetido),
mas os títulos planejados aqui usam outra convenção — então rodar direto criaria itens
*parecidos*, não idênticos.

**Rode `-Auditar` primeiro.** Ele mostra três coisas:

1. Todas as issues existentes, com número e labels
2. Cobertura de cada `US-00` a `US-15` — quais têm zero itens
3. Quais itens planejados não têm título idêntico no repo

O que o planejamento tem e a Wiki não tinha, e portanto provavelmente **falta** no board:

| Item | Por que importa |
|---|---|
| **US-13** confirmar/finalizar consulta | Sem ela a RN06 não é demonstrável — consulta solicitada ficaria eternamente `SOLICITADA` |
| **US-14** agenda geral | A lista de funcionalidades pede "gerenciar a agenda geral" |
| **US-15** cadastro de atendente | RN14 — sem ela o sistema depende de uma única conta |
| Tarefas de **QA** | CTs, sessões exploratórias, branch protection |
| Tarefas de **INFRA** | Revisão da migração |
| Tarefas de **DOCS** | Slides, release `v1.0.0` |

### Draft item ou Issue?

| | Draft (padrão) | Issue (`-Modo issues`) |
|---|---|---|
| Aparece no board | ✅ | ✅ |
| Cria Issue no repositório | ❌ | ✅ |
| Aceita responsável | ✅ | ✅ |
| Aceita label | ❌ | ✅ |
| Referenciável em PR (`#12`) | ❌ | ✅ |
| Conversível depois | ✅ *(Convert to issue)* | — |

Recomendação: `-Modo issues` para as User Stories (você vai querer referenciar nos PRs) e draft
para as tarefas granulares.

### Colunas reais do board

`To Do` · `In Dev` · `Code Review` · `In QA` · `UAT` · `Done` — documentadas em
[`../docs/10-git-flow.md`](../docs/10-git-flow.md) §7.

---

## `criar-labels` — labels dos templates de Issue

```powershell
.\scripts\criar-labels.ps1
```

```bash
./scripts/criar-labels.sh
```

Necessário antes de `popular-board -Modo issues`, senão as labels não existem.

---

## `gerar-wiki.py` — gera `wiki/` a partir de `docs/`

`docs/` é a **fonte da verdade**. Este script converte os links relativos do markdown nos links
de página que o Wiki do GitHub espera.

```powershell
python scripts\gerar-wiki.py             # gera / atualiza
python scripts\gerar-wiki.py --check     # falha se wiki/ estiver desatualizado
```

`Home.md`, `_Sidebar.md`, `_Footer.md` e `README.md` são escritos à mão e preservados. Páginas
geradas que não correspondem mais a nenhum documento são removidas.

---

## `publicar-wiki` — publica `wiki/` no Wiki do GitHub

O Wiki é um repositório git separado (`<repo>.wiki.git`). O script clona, sincroniza e faz push.

```powershell
.\scripts\publicar-wiki.ps1 -DryRun      # mostra o que mudaria
.\scripts\publicar-wiki.ps1              # publica
```

```bash
./scripts/publicar-wiki.sh --dry-run
./scripts/publicar-wiki.sh
```

**Se o clone falhar:**

- O Wiki precisa ter ao menos uma página criada pela interface web. Neste repositório já existe.
- O script usa **SSH** (`git@github.com:...`). Teste com `ssh -T git@github.com`. Se você usa
  HTTPS, troque a variável `$WikiUrl` (no `.ps1`) ou `WIKI_URL` (no `.sh`) por
  `https://github.com/<owner>/<repo>.wiki.git`.

⚠️ O script **substitui** os `.md` do Wiki pelos de `wiki/`. Se alguém editou direto na
interface web, essas alterações são perdidas. Regra da equipe: **edite em `docs/`, gere com
`gerar-wiki.py`, publique com `publicar-wiki`.**

---

## Fluxo completo no Windows

```powershell
# 1. liberar scripts nesta sessão
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 2. auditar o board antes de mexer
.\scripts\popular-board.ps1 -Auditar

# 3. criar labels e só então os itens que faltam
.\scripts\criar-labels.ps1
.\scripts\popular-board.ps1 -DryRun
.\scripts\popular-board.ps1

# 4. wiki
python scripts\gerar-wiki.py
.\scripts\publicar-wiki.ps1 -DryRun
.\scripts\publicar-wiki.ps1
```
