# IF03 — Validação do CI com quality gate (ci.yml)

- **Ambiente:** GitHub Actions · `ci.yml` em `feature/us02-tela-medicos` (PR #21 → falha / PR #25 → sucesso)
- **Executor:** JoaoVitorML-BR
- **Data:** 03/08/2026
- **Resultado:** ✅ quality gate barra na falha e libera na correção

## Jobs validados

| Job | O que executa |
| --- | --- |
| **Backend (FastAPI + pytest)** | `ruff check` + `ruff format --check` + `pytest` (unit + integration) com cobertura |
| **Frontend (Next.js + Vitest)** | Prettier + ESLint + `tsc` + Vitest com cobertura + `next build` |
| **Docker Compose sobe** | `docker compose up`, migrações Alembic, seed executado **2×** (prova idempotência — ADR-004) |
| **Quality Gate** | Agrega os três jobs; falha se qualquer um falhou — é o check obrigatório do branch protection |

## Passos e evidências

| # | Passo | Resultado observado | Evidência |
| --- | --- | --- | --- |
| 1 | PR #21 abre na `feature/us02-tela-medicos` com teste quebrado no frontend (`login.test.tsx`) | **Failure** — job `Frontend (Next.js + Vitest)` ❌ · `Quality Gate` ❌ · merge bloqueado | `01-teste-falha-ci.png` |
| 2 | Erro apontado pelo gate: `AssertionError` em `__tests__/login.test.tsx#L74` | 4 errors e 3 warnings nas annotations · saída mostra o assert exato que falhou | `01-teste-falha-ci.png` |
| 3 | Correção commitada na mesma branch (sync #62) · PR #25 re-roda o CI | **Success** — todos os 4 jobs ✅ · `Quality Gate` ✅ · merge liberado | `02-teste-sucesso-ci.png` |
| 4 | Duração total aprovada: 1m 38s · Backend 44s · Frontend 1m 16s · Docker 55s · Gate 4s | Apenas warnings de deprecação de Node.js 20 (não bloqueiam) | `02-teste-sucesso-ci.png` |

## Observações

- O job `Quality Gate` usa `needs: [backend, frontend, docker]` com `if: always()`, garantindo que roda mesmo quando os outros falham — é ele que o branch protection exige como status check obrigatório.
- O job **Docker** roda o seed **duas vezes de propósito** para validar a idempotência descrita no ADR-004 (`python -m app.seeds.seed` × 2).
- Os warnings de "Node.js 20 is deprecated" nos jobs de backend e docker (actions/checkout@v4, actions/setup-python@v5) são informativos e não bloqueiam o pipeline.
- A falha do PR #21 foi provocada propositalmente para validar que o quality gate barra de verdade — conforme exigido pela Definition of Done desta iteração.
