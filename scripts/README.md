# Scripts

## `criar-labels.sh`

Cria as labels usadas pelos templates de Issue e pelo `popular-board.sh --issues`.

```bash
./scripts/criar-labels.sh
```

## `popular-board.sh`

Popula o [quadro Kanban](https://github.com/users/jacksoncassemiro/projects/3) com as 16 User
Stories e as tarefas de backend, frontend, QA, infra e documentação — 61 itens no total.

```bash
./scripts/popular-board.sh --auditar       # ⭐ comece por aqui: o que já existe vs. o planejado
./scripts/popular-board.sh --dry-run       # só lista o que criaria
./scripts/popular-board.sh                 # draft items (padrão)
./scripts/popular-board.sh --issues        # Issues no repo + board
./scripts/popular-board.sh --sprint 1      # só a Sprint 1
```

### ⚠️ O board já está populado

A equipe já criou **41 issues** a partir das tarefas da Wiki (US-00 a US-12), com títulos no
padrão `[US-00] [BACKEND] Endpoint de Login`. O script é **idempotente** (pula título repetido),
mas os títulos planejados aqui usam outra convenção — então rodar direto criaria itens
*parecidos*, não idênticos.

**Rode `--auditar` primeiro.** Ele lista as issues existentes, mostra a cobertura de cada US-XX
e diz quais itens planejados não têm correspondente exato. Aí você decide: ajustar os títulos do
array `ITENS` para o padrão da equipe, ou criar só o que realmente falta.

O que o planejamento tem e a Wiki não tinha, e portanto provavelmente **falta** no board:
US-13 (confirmar/finalizar consulta), US-14 (agenda geral), US-15 (cadastro de atendente), e as
tarefas de QA (CTs, sessões exploratórias, branch protection), INFRA (migração, yarn.lock) e
DOCS (slides, release).

### Colunas reais do board

`To Do` · `In Dev` · `Code Review` · `In QA` · `UAT` · `Done` — documentadas em
[`../docs/10-git-flow.md`](../docs/10-git-flow.md) §7.

### Draft item ou Issue?

| | Draft item (`--draft`) | Issue (`--issues`) |
|---|---|---|
| Aparece no board | ✅ | ✅ |
| Cria Issue no repositório | ❌ | ✅ |
| Aceita responsável | ✅ | ✅ |
| Aceita label | ❌ | ✅ |
| Referenciável em PR (`#12`) | ❌ | ✅ |
| Conversível depois | ✅ *(Convert to issue)* | — |

**Recomendação:** `--draft` para as tarefas granulares (mantém a aba Issues limpa) e `--issues`
para as User Stories, que você vai querer referenciar nos PRs. Para isso:

```bash
./scripts/popular-board.sh --issues --dry-run   # confira a lista
# edite o array ITENS deixando só os itens tipo US, ou crie as US pela interface
```

### Autenticação

O `gh` precisa do escopo `project`:

```bash
gh auth login
gh auth refresh -s project,read:project
```

## `gerar-wiki.py`

Gera as páginas de `wiki/` a partir de `docs/`, convertendo os links relativos do markdown nos
links de página que o Wiki do GitHub espera.

```bash
python scripts/gerar-wiki.py           # gera / atualiza
python scripts/gerar-wiki.py --check   # falha se wiki/ estiver desatualizado
```

`Home.md`, `_Sidebar.md`, `_Footer.md` e `README.md` são escritos à mão e preservados — o resto
é gerado. Páginas geradas que não correspondem mais a nenhum documento são removidas.

**Fluxo:** editar `docs/` → `python scripts/gerar-wiki.py` → `./scripts/publicar-wiki.sh`

## `publicar-wiki.sh`

Publica as páginas de `wiki/` no Wiki do GitHub. O Wiki é um repositório git separado
(`<repo>.wiki.git`) — o script clona, sincroniza e faz push.

```bash
./scripts/publicar-wiki.sh --dry-run
./scripts/publicar-wiki.sh
```

**Antes do primeiro uso:** o Wiki precisa ter ao menos uma página criada pela interface web.
Neste repositório já existe (Home), então o clone funciona.

⚠️ O script **substitui** os `.md` do Wiki pelos de `wiki/`. Se alguém editou direto na
interface web, essas alterações são perdidas. Regra da equipe: **edite em `wiki/`, publique pelo
script.**
