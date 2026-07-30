# Estratégia de entrega — Git Flow

Entregável do Engenheiro de Software. Base: *Módulo 1 — Fundamentos da Engenharia Moderna*
(processos, versionamento e code review).

---

## 1. Modelo de branches

```
main ──────────●────────────────────────●────────▶  produção (protegida)
                ╲                      ╱
                 ╲   release/1.0 ──────●
                  ╲                   ╱
develop ──●───●────●────●────●───●───●──────────▶  integração (protegida)
           ╲  ╱     ╲  ╱      ╲ ╱
            ●●       ●●         ●●
       feature/us01  feature/us08  fix/us11-fuso
```

| Branch | Origem | Destino | Quem cria | Protegida |
|---|---|---|---|---|
| `main` | — | — | — | ✅ |
| `develop` | `main` | `main` (via release) | — | ✅ |
| `feature/*` | `develop` | `develop` | qualquer dev | ❌ |
| `fix/*` | `develop` | `develop` | qualquer dev | ❌ |
| `docs/*` | `develop` | `develop` | qualquer um | ❌ |
| `release/*` | `develop` | `main` + `develop` | ENG-A | ❌ |
| `hotfix/*` | `main` | `main` + `develop` | ENG-A | ❌ |

**Nomenclatura:** `<tipo>/us<NN>-<slug-curto>`

```
feature/us03-cadastro-paciente
feature/us08-solicitar-consulta
fix/us11-fuso-cancelamento
docs/adr-design-patterns
release/1.0
```

---

## 2. Proteção de branch (configurar no GitHub)

*Settings → Branches → Add rule* para `main` e `develop`:

- [x] Require a pull request before merging
- [x] Require approvals: **1**
- [x] Dismiss stale pull request approvals when new commits are pushed
- [x] Require status checks to pass before merging
  - Required check: **`Quality Gate`**
- [x] Require branches to be up to date before merging
- [x] Require conversation resolution before merging
- [ ] Allow force pushes — **desmarcado**
- [ ] Allow deletions — **desmarcado**

O `quality-gate` do CI agrega backend, frontend e docker. É ele que impede merge de código
quebrado — sem esse check, a proteção é decorativa.

---

## 3. Fluxo diário

```bash
# 1. partir de develop atualizado
git switch develop
git pull --ff-only

# 2. criar a branch da US
git switch -c feature/us08-solicitar-consulta

# 3. trabalhar em commits pequenos
git add backend/app/services/consulta_service.py backend/tests/unit/test_consulta_service.py
git commit -m "feat(consulta): impede reserva de horario ja ocupado (RN03)"

# 4. antes de abrir o PR, rebase em develop
git switch develop && git pull --ff-only
git switch -
git rebase develop

# 5. validar localmente
make lint && make test

# 6. publicar e abrir PR
git push -u origin feature/us08-solicitar-consulta
gh pr create --base develop --fill
```

Rebase (não merge) na feature: mantém o histórico linear e o `git log` legível para a
apresentação.

---

## 4. Conventional Commits

```
<tipo>(<escopo>): <o que mudou, imperativo, minúsculo> (<RN quando aplicável>)
```

| Tipo | Uso |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `test` | Teste (sem mudar comportamento) |
| `refactor` | Reestruturação sem mudar comportamento |
| `chore` | Dependência, configuração, tarefa auxiliar |
| `ci` | Pipeline |
| `perf` | Performance |

**Escopos:** `auth` `paciente` `medico` `especialidade` `agenda` `consulta` `ui` `ci` `docs` `infra`

### Bons

```
feat(consulta): impede reserva de horario ja ocupado (RN03)
feat(auth): adiciona verificacao de cpf no primeiro acesso
fix(consulta): corrige fuso no calculo das 24h (RN15) (#12)
test(agenda): cobre bloqueio de alocacao dupla (RN05)
refactor(paciente): extrai validacoes para metodos privados
docs(adr): registra escolha de Strategy para cancelamento
ci: adiciona job de docker compose ao pipeline
chore(front): fixa jest-dom em 6.9.1
```

### Ruins

```
ajustes              ← o que foi ajustado?
wip                  ← não commite WIP em branch que vira PR
correções finais     ← não diz nada
update               ← nada
feat: várias coisas  ← um commit, uma ideia
```

Um commit = uma ideia. Se a mensagem precisa de "e", divida o commit.

---

## 5. Pull Request

Template em [`.github/pull_request_template.md`](https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy/blob/develop/.github/pull_request_template.md).
Obrigatório: US referenciada, RNs cobertas, link do item no board, CI verde, 1 aprovação.

**Tamanho:** PR acima de ~400 linhas alteradas deve ser dividido. Revisão de PR grande é
revisão superficial.

### Checklist de code review

Ordem de importância. Itens 1–4 justificam *Request changes*:

1. **Vazamento de camada** — `HTTPException`/`select` em service; `if` de regra em router
2. **`if perfil ==`** onde deveria haver Strategy
3. **RN sem teste**, ou teste cujo nome não cita a RN
4. **Paciente agindo sobre id que não veio do token** (vazamento entre pacientes)
5. Número mágico hardcoded em vez de `settings` / constante nomeada
6. `any` no TypeScript, `fetch` direto em componente, falta de `'use client'`
7. `print` / `console.log` esquecido

Comandos rápidos de verificação:

```bash
grep -rn "HTTPException\|select(" backend/app/services/   # deve ser vazio
grep -rn "\.commit()" backend/app/repositories/           # deve ser vazio
grep -rn "console.log" frontend/src/                      # deve ser vazio
```

---

## 6. Release

```bash
git switch -c release/1.0 develop
# ajustes finais, versão, CHANGELOG
git commit -m "chore(release): prepara v1.0.0"
git push -u origin release/1.0
# PR release/1.0 → main, revisado e aprovado

git switch main && git pull --ff-only
git merge --no-ff release/1.0
git tag -a v1.0.0 -m "MVP Clinica Medica - AV2 Equipe 01"

git switch develop
git merge --no-ff release/1.0

git push origin main develop --tags
git push origin --delete release/1.0
```

`--no-ff` no merge de release preserva o ponto de integração no histórico — o que mostra o
Git Flow no grafo durante a apresentação.

**Versionamento semântico:** `v1.0.0` = MVP entregue. Correção pós-entrega → `v1.0.1`.

---

## 7. Board (GitHub Projects)

| Coluna | Significado | WIP |
|---|---|---|
| **To Do** | Priorizado e refinado, ainda não iniciado | — |
| **In Dev** | Alguém desenvolvendo | **2 por pessoa** |
| **Code Review** | PR aberto aguardando revisão | 3 |
| **In QA** | QA executando o caso de teste | 5 |
| **UAT** | PO validando os critérios de aceite | — |
| **Done** | Merge em `develop` + critérios aprovados pelo PO | — |

O **UAT** separado de *Done* é útil: deixa visível o que a engenharia terminou mas o PO ainda
não aprovou — e é onde o entregável "verificar critérios de aceite" do PO acontece.

Regras:

- Item em *In Dev* tem responsável atribuído. Sem dono, volta para *To Do*.
- **WIP limit de 2 por pessoa.** O `Aula - Pratica - Metodologia Agil.pdf` aponta "muitas
  tarefas em paralelo (overload)" e "não há limite de WIP" como as causas dos atrasos no case
  da EdTech. É a regra mais fácil de furar e a que mais dói.
- *Done* só depois do merge **e** da validação do PO. "Está pronto no meu computador" não é Done.
- Débito técnico e antipadrão encontrado entram como item com label `tech-debt` — foi o que a
  *Aula Prática 13-05* pediu: *"documentar os antipadrões no quadro Kanban"*.

O board aceita **draft items** (só no board, sem Issue) ou **Issues** do repositório.
Para popular em lote, use `scripts/popular-board.sh` — ver `--help`.

---

## 8. Estado atual do repositório

```
main      716a0ba README
develop   d40decf feat: initialize Python (FastAPI) project with PostgreSQL and Docker
```

Próximo passo: PR da reorganização em monorepo → `develop`, e configurar as proteções da §2.


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
