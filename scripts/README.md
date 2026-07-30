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
./scripts/popular-board.sh --dry-run       # só lista o que criaria
./scripts/popular-board.sh                 # draft items (padrão)
./scripts/popular-board.sh --issues        # Issues no repo + board
./scripts/popular-board.sh --sprint 1      # só a Sprint 1
```

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
