# Integração contínua (CI)

Entregável de QA. Arquivo: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
Base: *Módulo 6 — CI/CD e Operação* (pipelines build/test/deploy, quality gates).

---

## 1. Quando roda

```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

`concurrency` com `cancel-in-progress` cancela execução obsoleta quando há push novo na mesma
branch — evita fila e consumo desnecessário de minutos.

---

## 2. Jobs

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   backend    │  │   frontend   │  │    docker    │   ← paralelos
│              │  │              │  │              │
│ ruff check   │  │ eslint       │  │ compose      │
│ ruff format  │  │ tsc --noEmit │  │   config     │
│ alembic      │  │ vitest       │  │ up --build   │
│ pytest unit  │  │ next build   │  │ healthcheck  │
│ pytest integ │  │              │  │ migrate      │
│ coverage     │  │ coverage     │  │ seed × 2     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       └─────────────────┼─────────────────┘
                         ▼
                ┌──────────────────┐
                │  quality-gate    │  ← required status check
                └──────────────────┘
```

### `backend` — FastAPI + pytest

Python 3.12, serviço PostgreSQL 16 com healthcheck, cache de pip.

| Passo | Comando | Reprova se |
|---|---|---|
| Lint | `ruff check .` | Erro de lint ou import desordenado |
| Formatação | `ruff format --check .` | Código fora do padrão |
| Migrações | `alembic upgrade head` | Cadeia de migração quebrada |
| Unitários | `pytest tests/unit -m unit --cov=app` | Qualquer RN quebrada |
| Integração | `pytest tests/integration -m integration` | Contrato da API mudou sem intenção |
| Cobertura | upload de `coverage.xml` | — (informativo) |

Rodar `alembic upgrade head` no CI valida a cadeia inteira do zero — o que um `create_all()`
nunca validaria.

### `frontend` — Next.js + Vitest

Node 22.

| Passo | Comando | Reprova se |
|---|---|---|
| Lint | `yarn lint` → `eslint .` | Erro de ESLint |
| Tipos | `yarn typecheck` (`next typegen && tsc --noEmit`) | Erro de tipo — inclusive `any` implícito |
| Testes | `yarn test --coverage` | Teste falhou |
| Build | `yarn build` | Build de produção quebrado |

O `typecheck` separado importa: `next build` não falha em todo erro de tipo, mas `tsc --noEmit`
falha. E o `next typegen` antes dele é obrigatório: é o que gera `next-env.d.ts` e os tipos de
rota que o `tsc` precisa.

> **`next lint` foi removido no Next 16.** Usar `next lint` faz o Next interpretar `lint` como
> nome de diretório e falhar com
> `Invalid project directory provided, no such directory: .../frontend/lint`.
> O substituto oficial é a CLI do ESLint (`eslint .`) com `eslint-config-next` em flat config.

> **Nota:** o passo de instalação usa `--frozen-lockfile` quando existe `yarn.lock`.
> Rodem `yarn install` localmente e **comitem o `yarn.lock`** — sem ele o CI emite um warning
> e a instalação não é reprodutível.

### `docker` — o stack sobe em qualquer máquina

Este job é o que dá substância ao RNF07. Sem ele, "funciona na minha máquina" é uma promessa.

| Passo | O que valida |
|---|---|
| `docker compose config --quiet` | YAML e interpolação de variáveis válidos |
| `cp .env.example .env` + `up -d --build` | O `.env.example` é realmente copiar-e-rodar |
| Loop de `curl /health` (até 150s) | API sobe e responde de fato |
| `alembic upgrade head` + `alembic current` | Migração funciona **e** alguma revisão foi realmente aplicada |
| `python -m app.seeds.seed` | Seed cria o atendente inicial |
| **`python -m app.seeds.seed` de novo** | **Seed é idempotente** — prova a promessa do ADR-004 |
| `docker compose down -v` | Limpeza (roda com `if: always()`) |

Rodar o seed duas vezes não é redundância: é o teste da idempotência. Se a segunda execução
estourar violação de `UNIQUE`, o job falha.

### `quality-gate` — o portão

```yaml
needs: [backend, frontend, docker]
if: always()
```

Falha se qualquer um dos três não terminou em `success`. Configurado como **required status
check** na proteção de `main` e `develop` (ver [10-git-flow.md](10-git-flow.md) §2).

É o gate único: em vez de exigir três checks na proteção de branch, exige-se um. Se um job
novo entrar no pipeline, basta adicioná-lo ao `needs` — a configuração do GitHub não muda.

---

## 3. Rodar localmente antes do push

```bash
make lint          # ruff + eslint + tsc
make test          # pytest + vitest
docker compose config --quiet   # valida o compose
```

CI é rede de segurança, não substituto de rodar o teste antes do commit. Push que quebra
`develop` bloqueia os outros cinco.

---

## 4. Artifacts

| Artifact | Conteúdo | Uso |
|---|---|---|
| `backend-coverage` | `coverage.xml` | Acompanhar cobertura ≥ 80% |
| `frontend-coverage` | `coverage/` (HTML) | Ver linhas descobertas |

Publicados com `if: always()`, então existem mesmo quando o teste falha — o que é justamente
quando você precisa olhar.

Baixar em *Actions → run → Artifacts*.

---

## 5. Evidência para a apresentação

Felipe (QA/CI) deve capturar, para os slides:

1. Lista de runs verdes em `develop`
2. Detalhe de um run mostrando os quatro jobs em verde
3. Log do job `docker` mostrando o **seed rodando duas vezes** com a segunda em no-op
4. Print do PR bloqueado por `quality-gate` vermelho (vale mais que o verde — prova que o
   gate funciona)
5. Relatório de cobertura

Guardar em `docs/evidencias/CI/`.

---

## 6. O que deliberadamente ficou fora

| Prática | Por que fora |
|---|---|
| Deploy automático (CD) | Não há ambiente de produção; a demonstração é local |
| Blue-green / canary / rollback | Pressupõem produção — Módulo 6 trata, mas sem aplicação aqui |
| SonarQube / SonarCloud | Exigiria conta e configuração externa; `ruff` + cobertura cobrem o essencial no prazo |
| Observabilidade (logs/metrics/traces) | Sem produção para observar |
| Dependabot | Projeto de 11 dias; sem janela para atualização de dependência |
| Matriz de versões (3.11/3.12, Node 20/22) | Versão única fixada pelo Docker; matriz só consumiria minutos |

Registrado para deixar claro que a ausência é escolha, não esquecimento — as práticas do
Módulo 6 que não se aplicam a um MVP local ficam como evolução futura.

---

## 7. Troubleshooting

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ruff format --check` falha | Código não formatado | `ruff format .` e commitar |
| `alembic upgrade head` falha no CI, passa local | Migração não commitada, ou duas heads | `alembic heads`; commitar a migração |
| Seed falha com `UndefinedTable: relation "usuario" does not exist` | `alembic/versions/` vazia ou sem a tabela. **Alembic passa em silêncio quando não há revisão.** | `pytest tests/integration/test_migracoes.py` mostra o que falta; gere/revise a migração |
| `yarn lint` falha com `no such directory: frontend/lint` | Script usando `next lint`, removido no Next 16 | Trocar por `eslint .` |
| `yarn install` com warning de lockfile | `yarn.lock` não commitado | `yarn install` local e commitar o lockfile |
| `tsc --noEmit` falha, `next build` passa | Erro de tipo que o build ignora | Corrigir o tipo — não use `any` |
| Job `docker` falha no healthcheck | API não subiu | Ler `docker compose logs backend` no output do job |
| Seed falha na 2ª execução | Idempotência quebrada | Revisar `existe_atendente()` / `buscar_por_nome()` |
| Teste passa local e falha no CI | Dependência de fuso ou de dado local | Injetar `agora`; não depender de estado prévio |
| Vitest: `x is not a function` | API do browser ausente no jsdom | Adicionar mock em `vitest.setup.mjs` |
