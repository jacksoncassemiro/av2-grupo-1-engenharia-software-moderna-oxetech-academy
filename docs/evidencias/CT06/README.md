# CT06 — Paciente cancela com mais de 24h de antecedência (RN04)

- **US:** US-11 · **RN:** RN04, RN15, RN03
- **Ambiente:** Docker local, seed aplicado
- **Executor:** Uanderson · **Data:** 08/08/2026
- **Resultado:** ✅ passou

## Pré-condição

Carlos com consulta CONFIRMADA em `2026-08-12 14:00` (marcada pelo atendente em CT05) — a
data real do teste era `2026-08-08`, então a consulta estava a ~4 dias de distância, bem
acima do limiar padrão de 24h (`CANCELAMENTO_ANTECEDENCIA_HORAS=24`).

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Login como Carlos, *Minhas Consultas* → abrir a consulta de `14:00`, preencher motivo `Imprevisto` | `01-modal-cancelamento-motivo.png` — modal "Cancelar consulta" totalmente renderizado, sem blur de transição |
| 2 | Confirmar cancelamento | `02-consulta-cancelada.png` — status → **CANCELADA**, motivo `Imprevisto` exibido na listagem |
| 3 | Como atendente, consultar horários livres do Dr. Silva em `2026-08-12` | `03-horario-liberado.png` — `14:00` e `15:00` aparecem juntos na lista de livres |

## Observações

- Nenhum bug encontrado.
- A primeira tentativa de captura do modal de confirmação pegou a transição de saída
  sobreposta ao toast de sucesso (mesmo problema de timing relatado para os toasts) — resolvido
  aguardando o fechamento completo antes da captura final.
- Reaproveitado em seguida por CT09 (finalizar a segunda consulta) e CT10 (reagendar o horário
  liberado).
