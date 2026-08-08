# CT09 — Ciclo de vida do status da consulta (RN06, RN10)

- **US:** US-08, US-13 · **RN:** RN06, RN10
- **Ambiente:** Docker local, seed aplicado
- **Executor:** Uanderson · **Data:** 08/08/2026
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Carlos (paciente) solicita consulta com Dr. Silva às `15:00` em `12/08/2026` | `01-consulta-solicitada.png` — Toast de notificação "Consulta com Dr. Silva solicitada..." |
| 2 | Verificar status exibido para o paciente | `02-status-solicitada.png` — Status exibe **SOLICITADA** (contraste com CT05, onde agendamento do atendente já nasce CONFIRMADA) |
| 3 | Atendente confirma a consulta | `03-status-confirmada.png` — Toast de sucesso e status muda para **CONFIRMADA** |
| 4 | Atendente finaliza a consulta | `04-lifecycle-finalizada.png` — Status passa para **FINALIZADA**; a UI oculta o botão de Cancelar (coluna Ações fica "—") |
| 5 | Tentar cancelar a consulta finalizada via API (bypass da UI) | `05-postman-422-transicao.png` — Requisição `PATCH` retorna erro **422**: `"Nao e permitido ir de FINALIZADA para CANCELADA"` |

## Observações

- No passo 5, a UI de `gerenciar-consultas` já esconde a ação de Cancelar para consultas
  FINALIZADA — bom sinal de UX, mas isso significa que a única forma de testar a defesa do
  *backend* (que é o que a RN10 realmente exige) é chamar a API diretamente, o que fiz.
- Nenhum bug encontrado.