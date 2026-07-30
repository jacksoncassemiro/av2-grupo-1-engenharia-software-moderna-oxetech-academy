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

## `popular-board` — fechar as originais e recriar o board

Lê os itens de **`board-itens.json`** — fonte única compartilhada pelo `.ps1` e pelo `.sh`.

```powershell
.\scripts\popular-board.ps1 -Auditar             # o que existe vs. o planejado
.\scripts\popular-board.ps1 -Tudo -DryRun        # ⭐ confira antes de escrever
.\scripts\popular-board.ps1 -Tudo               # fecha as 41 e cria os 82
.\scripts\popular-board.ps1 -Fechar             # só fecha
.\scripts\popular-board.ps1 -Criar              # só cria
.\scripts\popular-board.ps1 -Criar -Secao processo   # só QA/INFRA/DOCS
.\scripts\popular-board.ps1 -Criar -Sprint 1
```

```bash
./scripts/popular-board.sh --auditar
./scripts/popular-board.sh --tudo --dry-run
./scripts/popular-board.sh --tudo
./scripts/popular-board.sh --criar --secao processo
```

Sem nenhuma flag, o script **não faz nada** e mostra as opções — de propósito.

### O que ele faz

**1. Fecha as 41 issues originais** (`#4` a `#45`, de @Lothriiik) com `--reason "not planned"`
e um **comentário de justificativa** explicando que foram _substituídas_, não descartadas, e
dando crédito pelo levantamento original. Nada é apagado: o histórico e a autoria ficam.

**2. Cria 82 itens** com rastreabilidade completa:

| Seção          | Qtd | O que é                                                                                        |
| -------------- | --- | ---------------------------------------------------------------------------------------------- |
| `user_stories` | 16  | Guarda-chuva `US-00:` a `US-15:` — é onde o PO valida os critérios de aceite na coluna **UAT** |
| `tarefas`      | 47  | Execução, no padrão `[US-XX] [ÁREA] Título` (mesma convenção da equipe)                        |
| `processo`     | 19  | **QA, INFRA e DOCS** — entregáveis avaliados que não existiam no board                         |

Cada item ganha: **US**, **RNs cobertas** (IDs de `docs/01-requisitos.md`), link do critério de
aceite, **Definition of Done** por área, e **label**.

### Por que recriar em vez de editar

As descrições originais estavam tecnicamente corretas. O que faltava era a cadeia
**requisito → código → teste → evidência**, que é o que a AV2 avalia — e label, sem a qual o
board não serve para WIP nem métricas.

Os títulos e as descrições técnicas foram **preservados**; a issue #44, por exemplo, mantém
"Criar rota PATCH /api/atendente/consultas/:id/cancelar…" e ganha `RN03, RN10`, o link do
critério de aceite e o DoD.

### Idempotência

Roda quantas vezes quiser: pula issue já fechada e título que já existe. Se algo falhar no meio,
rode de novo — ele continua de onde parou.

### Colunas reais do board

`To Do` · `In Dev` · `Code Review` · `In QA` · `UAT` · `Done`

O **UAT** separado de _Done_ é o que dá lugar ao entregável "verificar critérios de aceite" do
PO. Documentado em [`../docs/10-git-flow.md`](../docs/10-git-flow.md) §7.

### ⚠️ Ordem correta

```powershell
.\scripts\criar-labels.ps1          # 1º — senão as issues nascem sem label
.\scripts\popular-board.ps1 -Tudo -DryRun
.\scripts\popular-board.ps1 -Tudo
```

---

## `board-itens.json` — fonte única dos itens

Editar aqui muda o comportamento dos **dois** scripts. Estrutura:

```json
{
	"issues_a_fechar": [{ "numero": 4, "titulo": "..." }],
	"user_stories": [
		{ "sprint": "1", "tipo": "US", "titulo": "...", "corpo": "..." }
	],
	"tarefas": [
		{ "sprint": "1", "tipo": "BACKEND", "titulo": "...", "corpo": "..." }
	],
	"processo": [{ "sprint": "1", "tipo": "QA", "titulo": "...", "corpo": "..." }]
}
```

`tipo` define a label: `US` → `user-story` · `BACKEND`/`FRONTEND`/`QA`/`INFRA`/`DOCS` →
`tarefa` + área. O `corpo` aceita markdown.

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

## `verificar-sintaxe.py` — checa os scripts antes de rodar

Um `.ps1` com chave ou parêntese desbalanceado falha em tempo de execução — e no Windows, às
vezes **em silêncio**. Rode isto antes:

```powershell
python scripts\verificar-sintaxe.py
```

Valida balanceamento nos `.ps1` (tratando here-strings `@"..."@` e blocos `<# ... #>`
corretamente), `bash -n` nos `.sh` e `py_compile` nos `.py`. Não substitui um parser, mas pega a
classe de erro que trava o script.

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
- O script usa **HTTPS** por padrão (`https://github.com/...`). Se você preferir SSH, troque
  a variável `$WikiUrl` (no `.ps1`) ou `WIKI_URL` (no `.sh`) por
  `git@github.com:<owner>/<repo>.wiki.git`.

⚠️ O script **substitui** os `.md` do Wiki pelos de `wiki/`. Se alguém editou direto na
interface web, essas alterações são perdidas. Regra da equipe: **edite em `docs/`, gere com
`gerar-wiki.py`, publique com `publicar-wiki`.**

---

## Fluxo completo no Windows

```powershell
# 1. liberar scripts nesta sessão
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python scripts\verificar-sintaxe.py     # sanidade dos scripts

# 2. ver o estado atual
.\scripts\popular-board.ps1 -Auditar

# 3. labels PRIMEIRO, senão as issues nascem sem label
.\scripts\criar-labels.ps1

# 4. conferir e então executar
.\scripts\popular-board.ps1 -Tudo -DryRun
.\scripts\popular-board.ps1 -Tudo

# 5. wiki
python scripts\gerar-wiki.py
.\scripts\publicar-wiki.ps1 -DryRun
.\scripts\publicar-wiki.ps1
```
