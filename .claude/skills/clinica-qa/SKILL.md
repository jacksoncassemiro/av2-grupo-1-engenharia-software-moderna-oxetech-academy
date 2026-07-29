---
name: clinica-qa
description: Escreve e executa plano de testes, casos de teste, testes exploratorios, evidencias e pipeline de CI do MVP da clinica. Use quando a tarefa envolver QA, caso de teste CT, cobertura de regra de negocio, registro de bug, coleta de evidencia ou GitHub Actions deste projeto.
---

# QA da clínica — como trabalhar

Entregáveis avaliados na AV2: **plano de testes**, **10 casos de teste**, **testes
exploratórios com evidência**, **CI no GitHub Actions**.

## Pirâmide adotada

| Nível | Onde | Responsável | Marcador |
|---|---|---|---|
| Unitário | `backend/tests/unit/`, `frontend/__tests__/` | Engenharia | `@pytest.mark.unit` |
| Integração | `backend/tests/integration/` | Eng + QA | `@pytest.mark.integration` |
| Funcional / E2E manual | `docs/08-casos-de-teste.md` | QA | CT01–CT12 |
| Exploratório | `docs/07-plano-de-testes.md` §6 | QA | sessões por charter |

## Formato de caso de teste

Toda linha do CT precisa amarrar em uma US e uma RN — é a rastreabilidade que a
avaliação cobra.

```
| ID | Cenario | Perfil | US | RN | Pre-condicao | Passos | Resultado esperado |
```

Regra: **cada RN01–RN15 tem no mínimo 1 caso de teste**. Antes de fechar a sprint,
rode a matriz de rastreabilidade de `docs/08-casos-de-teste.md` §3 e confirme que
nenhuma RN está sem cobertura.

## Casos negativos são obrigatórios

Para cada RN existe o caso que **viola** a regra e espera bloqueio. É onde os bugs
aparecem. Mínimo por RN:

- RN01 → cadastrar 2 pacientes com o mesmo CPF → 409
- RN02 → mesmo e-mail em 2 usuários → 409; **e** 2 pacientes com e-mail nulo → deve passar
- RN03 → agendar em slot ocupado → 409; cancelar e reagendar o mesmo slot → deve passar
- RN04 → paciente cancela com 12h → 422; com 48h → 200
- RN05 → cadastrar 2x o mesmo dia/hora para o mesmo médico → 409
- RN06/RN10 → cancelar consulta FINALIZADA → 422
- RN09 → lançar agenda às 19:00 → 422
- RN12 → paciente chama rota de atendente → 403; sem token → 401

## Sessão exploratória — como registrar

Time-boxed em 45 min, com charter escrito antes:

```markdown
### Sessão EXP-01 — Fluxo de agendamento do paciente
- **Charter:** explorar o agendamento buscando falhas de estado e concorrência
- **Duração:** 45 min · **Data:** DD/MM · **Executor:** <nome>
- **Ambiente:** Docker local, seed aplicado
- **Achados:**
  | # | Descrição | Severidade | Issue |
  |---|---|---|---|
- **Evidências:** `docs/evidencias/EXP-01/`
```

Heurísticas para o MVP: voltar/avançar do browser no meio do fluxo; duplo clique em
Confirmar; token expirado; trocar o `paciente_id` no body; data no passado; slot
cancelado por outro em outra aba.

## Evidências

`docs/evidencias/<CT-ID ou EXP-ID>/` com `01-<passo>.png`, `02-….png` e um `README.md`
citando CT, US, RN, ambiente, data e executor. Print precisa mostrar a **mensagem de
erro exata** — é ela que prova que a RN foi aplicada.

## Bug

Abra Issue com o template `bug.yml`. Título `[BUG] <resumo>`. Sempre com: severidade,
CT de origem, passos, esperado vs. obtido, evidência. Vincule ao item do board.

Severidade: **Crítica** (bloqueia fluxo principal / viola RN) · **Alta** (RN
contornável) · **Média** (UX/validação) · **Baixa** (cosmético).

## CI (`.github/workflows/ci.yml`)

Quatro jobs: `backend` (ruff + alembic + pytest), `frontend` (eslint + tsc + vitest +
build), `docker` (compose sobe, healthcheck, migração, seed rodado 2x para provar
idempotência) e `quality-gate` (agrega — é o required status check da proteção de branch).

Ao mexer no CI: `docker compose config --quiet` local antes de commitar, e não remova
o `quality-gate` — ele é a regra de proteção de `main` e `develop`.

## Critérios de saída da sprint

- [ ] 100% dos CTs planejados executados
- [ ] 0 bug Crítico ou Alto em aberto
- [ ] Toda RN01–RN15 com ≥ 1 CT executado e evidência
- [ ] CI verde no último commit de `develop`
- [ ] Evidências commitadas em `docs/evidencias/`
