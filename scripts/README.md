# Scripts

Automação do board e da Wiki.

**A lógica de verdade está nos arquivos `.py`.** Os `.ps1` e `.sh` são atalhos finos que
chamam o Python — uma implementação só, testada uma vez, que roda igual em Windows, Linux e
macOS.

O motivo: a fonte dos itens (`board-itens.json`) já é gerada por `gerar-board-itens.py`, e o
`wiki/` por `gerar-wiki.py`. Python já era pré-requisito do fluxo. Manter uma segunda
implementação em PowerShell significaria duas cópias da mesma lógica divergindo entre si — e
`.ps1` é justamente onde já perdemos tempo com falha silenciosa.

| Script | O que faz | Precisa de |
|---|---|---|
| `gerar-board-itens.py` | Gera `board-itens.json` a partir das User Stories e das regras de negócio | Python |
| `popular-board.py` | Limpa o board e recria os itens | Python + `gh` |
| `criar-labels.ps1` / `.sh` | Cria as labels usadas pelas issues | `gh` |
| `gerar-wiki.py` | Gera `wiki/` a partir de `docs/` | Python |
| `publicar-wiki.ps1` / `.sh` | Publica `wiki/` no Wiki do GitHub | **só git** |
| `verificar-sintaxe.py` | Checa a sintaxe dos scripts antes de rodar | Python |
| `_python.ps1` | Encontra um Python que funciona de verdade. Não se roda direto | — |

Os `.ps1` de `popular-board`, `gerar-wiki` e `gerar-board-itens` são **atalhos** que chamam o
`.py` correspondente. O `publicar-wiki` é PowerShell/bash puro e **não usa Python**.

---

## ⚠️ Windows: os três erros que já pegaram a equipe

### 1. `Python was not found; run without arguments to install from the Microsoft Store`

O Windows instala um **atalho falso** em
`%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe`. Ele aparece no PATH, mas não é o Python:
ao ser executado só abre a loja. É o *App Execution Alias*.

Confira o que você tem:

```powershell
py -3 --version          # se responder "Python 3.x.y", está tudo bem
where.exe python         # se apontar para WindowsApps, é o atalho falso
```

Resolva de um dos dois jeitos:

```powershell
# a) instalar o Python de verdade (recomendado)
winget install --id Python.Python.3.12
# feche e abra o terminal, depois: py -3 --version

# b) desligar o atalho falso
# Configurações > Aplicativos > Configurações avançadas de aplicativos
# > Aliases de execução de aplicativo -> desligue python.exe e python3.exe
```

Os `.ps1` deste diretório procuram o Python na ordem `py -3` → `python3` → `python`,
**ignoram** qualquer executável dentro de `WindowsApps` e validam rodando `--version`. Se nada
funcionar, eles param com a instrução acima em vez de falhar de forma confusa.

### 2. `syntax error near unexpected token $'do\r'` nos `.sh`

Fim de linha **CRLF**. O Git no Windows vem com `core.autocrlf=true` e converte LF → CRLF ao
fazer checkout. O bash lê o `\r` como parte do comando e quebra com uma mensagem que não diz o
que aconteceu.

O `.gitattributes` do repositório já força `eol=lf` para `*.sh`, mas ele **só age em arquivos
que o Git ainda vai escrever**. Para aplicar aos que já estão no disco:

```powershell
git add --renormalize .
git checkout -- scripts/
py -3 scripts\verificar-sintaxe.py     # deve sair tudo "ok"
```

Se persistir, force para este repositório:

```powershell
git config core.autocrlf false
git rm --cached -r . ; git reset --hard
```

> Isso só afeta quem **executa** os `.sh` (Git Bash, WSL, Linux, macOS). No PowerShell você usa
> os `.ps1`, que devem mesmo ficar em CRLF — o `.gitattributes` cuida dos dois casos.

### 3. Os scripts "não fazem nada"

**Você rodou o `.sh` no PowerShell.** PowerShell não executa shell script.

```powershell
.\scripts\popular-board.ps1 -Auditar     # ✅ certo no Windows
./scripts/popular-board.sh --auditar     # ❌ só no Git Bash / WSL
```

**A política de execução bloqueia `.ps1`** — e, em algumas configurações, falha em silêncio.
Libere só para a sessão atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Ou pule o PowerShell e chame o Python direto — funciona igual:

```powershell
py -3 scripts\popular-board.py --auditar
```

---

## Pré-requisitos

```powershell
winget install --id Python.Python.3.12
winget install --id GitHub.cli
# feche e abra o terminal para o PATH atualizar

gh auth login
gh auth refresh -s project,read:project     # escopo de Projects, OBRIGATÓRIO
```

Confira os três:

```powershell
py -3 --version                             # deve dizer "Python 3.x.y"
gh auth status
gh project view 3 --owner jacksoncassemiro
```

> **Python é necessário?** Para o **board** e para **gerar** a wiki, sim. Para **publicar** a
> wiki, não — o `publicar-wiki` usa só git.

Sem o escopo `project`, o `popular-board` não consegue ler o Status dos itens — e, por
segurança, **não fecha nada**. Ele avisa quando isso acontece.

O `publicar-wiki` usa apenas **git**.

---

## 🚦 Runbook completo — do zero ao board e à Wiki publicados

Ordem obrigatória. Cada passo depende do anterior. Windows / PowerShell, na raiz do repositório.

```powershell
# ── FASE 0 · Preparar a sessão ────────────────────────────────────────────
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

py -3 --version                       # deve dizer "Python 3.x.y"
gh auth status                        # deve listar o escopo 'project'
py -3 scripts\verificar-sintaxe.py     # todos os scripts devem sair "ok"

# ── FASE 1 · Commitar a documentação ──────────────────────────────────────
# A Wiki e o board apontam para docs/ no GitHub. Se docs/ não estiver
# publicado, os links das issues nascem quebrados.
git checkout develop
git pull
git add -A
git commit -m "docs: rebaseline de escopo, separacao backend/frontend e board autocontido"
git push origin develop

# ── FASE 2 · Wiki ─────────────────────────────────────────────────────────
.\scripts\gerar-wiki.ps1 -Check        # confere se wiki/ está em dia com docs/
.\scripts\publicar-wiki.ps1 -DryRun    # mostra o que mudaria
.\scripts\publicar-wiki.ps1            # publica

# ── FASE 3 · Labels (antes das issues!) ───────────────────────────────────
.\scripts\criar-labels.ps1             # sem isso as issues nascem sem label

# ── FASE 4 · Board ────────────────────────────────────────────────────────
.\scripts\gerar-board-itens.ps1        # regenera scripts/board-itens.json
.\scripts\popular-board.ps1 -Auditar   # ⭐ LEIA a saída antes de continuar
.\scripts\popular-board.ps1 -Tudo -DryRun
.\scripts\popular-board.ps1 -Tudo      # aplica de verdade

# ── FASE 5 · Conferir ─────────────────────────────────────────────────────
.\scripts\popular-board.ps1 -Auditar   # "A criar" deve estar em 0
```

### Por que esta ordem

| Fase | Depende de | Se pular |
|---|---|---|
| 1 · commit de `docs/` | — | Os links no rodapé das issues apontam para arquivos que não existem no GitHub |
| 2 · Wiki | Fase 1 | A Wiki publica conteúdo desatualizado |
| 3 · labels | — | As issues nascem sem label; o board não serve para WIP nem métricas |
| 4 · board | Fases 1 e 3 | Issues sem label e com link quebrado |
| 5 · conferir | Fase 4 | Você não descobre o que falhou no meio |

### O que esperar do `-Auditar`

Hoje o board tem **108 itens**. A auditoria separa em quatro grupos:

- **A criar** — os 57 do planejamento novo que ainda não existem
- **Já existem** — títulos que batem; serão pulados (o script é idempotente)
- **A limpar** — fora do planejamento novo, com label `user-story`/`tarefa`, e **fora** de
  UAT/Done. Estes serão fechados e removidos do board
- **Preservadas** — em UAT ou Done. **Nunca são tocadas**

Se a linha "A limpar" trouxer algo que você quer manter, mova esse item para **UAT** no board
pela interface e rode o `-Auditar` de novo antes de aplicar.

### Se algo falhar no meio

Tudo é idempotente. Rode o mesmo comando de novo — ele pula o que já foi feito e continua.

---

## `gerar-board-itens.py` — a fonte dos itens

Gera `board-itens.json`. **Não edite o JSON à mão** — ele é sobrescrito.

Existe um gerador em vez de um JSON estático porque o texto das regras de negócio, os critérios
de aceite e a Definition of Done se repetem em dezenas de issues. Escrever à mão garantiria
divergência entre elas. Aqui cada RN é escrita **uma vez**, no dicionário `RN`, e injetada em
toda issue que a menciona.

Para mudar um item, edite as estruturas `US` (User Stories e tarefas) ou `PROCESSO` (QA, INFRA,
DOCS) no `.py` e rode o gerador de novo.

### Princípio: a issue é autocontida

Toda issue traz **no próprio corpo**: contexto, o que fazer, texto integral das regras de
negócio, critérios de aceite, Definition of Done e como testar. Links para `docs/` aparecem só
no rodapé, como referência complementar.

Isso é resposta a um problema real: na versão anterior do board, a descrição da atividade
apontava para `docs/` e quem pegava a tarefa precisava abrir dois ou três documentos e
correlacionar à mão para saber o que fazer e quando parar.

Se a issue e `docs/` divergirem, **`docs/` é a fonte da verdade** e a issue é corrigida.

### O que ele gera

| Seção | Qtd | O que é |
|---|---|---|
| `user_stories` | 14 | Guarda-chuva `US-00:` a `US-13:` — é onde o PO valida os critérios de aceite na coluna **UAT** |
| `tarefas` | 28 | Execução, no padrão `[US-XX] [ÁREA] Título` — cada uma equivale a um PR |
| `processo` | 15 | QA, INFRA e DOCS — entregáveis avaliados que não pertencem a nenhuma US |

Escopo congelado pelo [ADR-008](../docs/adr/ADR-008-rebaseline-escopo.md): US-14 e US-15 saíram
do MVP e viraram MF01 e MF02 em [`docs/15-melhorias-futuras.md`](../docs/15-melhorias-futuras.md).

---

## `popular-board` — limpar e recriar

```powershell
.\scripts\popular-board.ps1 -Auditar              # o que existe vs. o planejado
.\scripts\popular-board.ps1 -Tudo -DryRun         # ⭐ confira antes de escrever
.\scripts\popular-board.ps1 -Tudo                 # limpa e cria
.\scripts\popular-board.ps1 -Limpar               # só limpa
.\scripts\popular-board.ps1 -Criar                # só cria
.\scripts\popular-board.ps1 -Criar -Secao processo
.\scripts\popular-board.ps1 -Criar -Sprint 1
```

```bash
./scripts/popular-board.sh --auditar
./scripts/popular-board.sh --tudo --dry-run
./scripts/popular-board.sh --tudo
```

**Sem nenhuma flag, o script não faz nada** e mostra as opções — de propósito.

### O que a limpeza faz

Uma issue aberta é candidata a limpeza quando **todas** estas condições valem:

1. O título **não** está no planejamento novo
2. Ela tem label `user-story` ou `tarefa`
3. O Status dela no board **não** é `UAT` nem `Done`

Se as três valem, a issue é **fechada** com `--reason "not planned"` e um comentário de
justificativa, e o item é **removido do board**. A issue continua existindo: histórico, autoria
e discussão ficam preservados.

### O que nunca é tocado

| Categoria | Por quê |
|---|---|
| Issues em **UAT** ou **Done** | Já foram trabalhadas — combinado da equipe |
| Issues com label `bug`, `funcionalidade` ou `melhoria` | Foram abertas pela equipe fora do planejamento |
| Issues já fechadas | Nada a fazer |
| Qualquer coisa, se o Status do board não puder ser lido | Sem saber o que está em UAT, o script prefere não fechar nada. Rode `gh auth refresh -s project,read:project` |

### `-Apagar` — apagar de verdade

```powershell
.\scripts\popular-board.ps1 -Tudo -Apagar
```

Usa `gh issue delete` em vez de fechar. **É irreversível** e o script pede confirmação digitada.
Prefira o padrão (fechar + remover do board): o board fica igualmente limpo e o histórico
sobrevive, que é o que a avaliação examina.

### Idempotência

Roda quantas vezes quiser: pula issue já fechada e título que já existe. Se falhar no meio,
rode de novo — continua de onde parou.

### Colunas do board

`To Do` · `In Dev` · `Code Review` · `In QA` · `UAT` · `Done`

O **UAT** separado de *Done* é o que dá lugar ao entregável "verificar critérios de aceite" do
PO. Documentado em [`../docs/10-git-flow.md`](../docs/10-git-flow.md) §7.

---

## `criar-labels` — labels das issues

```powershell
.\scripts\criar-labels.ps1
```

```bash
./scripts/criar-labels.sh
```

**Rode antes do `popular-board -Criar`**, senão as issues nascem sem label — e sem label o board
não serve para WIP nem para métricas.

---

## `verificar-sintaxe.py` — checar antes de rodar

```powershell
py -3 scripts\verificar-sintaxe.py
```

Valida balanceamento nos `.ps1` (tratando here-strings `@"..."@` e blocos `<# ... #>`), `bash -n`
nos `.sh` e `py_compile` nos `.py`. Não substitui um parser, mas pega a classe de erro que trava
o script.

---

## `gerar-wiki.py` — gerar `wiki/` a partir de `docs/`

`docs/` é a **fonte da verdade**. Este script converte os links relativos do markdown nos links
de página que o Wiki do GitHub espera.

```powershell
.\scripts\gerar-wiki.ps1                 # gera / atualiza
.\scripts\gerar-wiki.ps1 -Check          # falha se wiki/ estiver desatualizado
```

`Home.md`, `_Sidebar.md`, `_Footer.md` e `README.md` são escritos à mão e preservados. Páginas
geradas que não correspondem mais a nenhum documento são removidas.

---

## `publicar-wiki` — publicar no Wiki do GitHub

O Wiki é um repositório git separado (`<repo>.wiki.git`). O script clona, sincroniza e faz push.

```powershell
.\scripts\publicar-wiki.ps1 -DryRun      # mostra o que mudaria
.\scripts\publicar-wiki.ps1              # publica
```

```bash
./scripts/publicar-wiki.sh --dry-run
./scripts/publicar-wiki.sh
```

**Se o clone falhar:** o Wiki precisa ter ao menos uma página criada pela interface web — neste
repositório já existe. O script usa **HTTPS** por padrão; para SSH, troque `$WikiUrl` (`.ps1`) ou
`WIKI_URL` (`.sh`).

⚠️ O script **substitui** os `.md` do Wiki pelos de `wiki/`. Quem editar direto na interface web
perde a alteração. Regra da equipe: **edite em `docs/`, gere com `gerar-wiki.py`, publique com
`publicar-wiki`.**
