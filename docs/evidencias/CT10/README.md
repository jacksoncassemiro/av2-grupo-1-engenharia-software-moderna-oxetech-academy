# CT10 — Reagendar horário liberado por cancelamento (RN03 + RN10)

- **US:** US-08, US-11 · **RN:** RN03, RN10
- **Ambiente:** Docker local, seed aplicado
- **Executor:** Uanderson · **Data:** 08/08/2026
- **Resultado:** ✅ passou

## Pré-condição

CT06 executado — existe consulta CANCELADA de Carlos no slot `Dr. Silva / 2026-08-12 / 14:00`.

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Atendente lista horários livres do Dr. Silva em `2026-08-12` | `01-horario-14h-livre.png` — O horário `14:00` volta a aparecer disponível na interface |
| 2 | Agendar o segundo paciente de teste (Maria, CPF `111.444.777-35`) no mesmo horário (`14:00`) que foi cancelado | `02-novo-agendamento-sucesso.png` — Toast de "Consulta agendada" e status **CONFIRMADA** |
| 3 | Verificar a listagem de "Todas as consultas" no painel do atendente | `03-slot-reagendado-duas-linhas.png` — Duas linhas para o mesmo `14:00`: Carlos Souza **CANCELADA** + Maria **CONFIRMADA** |

## Prova do ADR-006

A listagem mostrando as duas linhas para o mesmo par médico/data/horário sem erro de
constraint é a prova empírica de que o índice parcial `uq_slot_ativo` (em vez de um `UNIQUE`
comum sobre `horario_disponivel_id`) está correto — com um `UNIQUE` simples, o passo 2 teria
falhado com violação de integridade.

## Observações

- Nenhum bug encontrado.