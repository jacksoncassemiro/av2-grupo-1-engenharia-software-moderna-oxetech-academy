# CT13 — Bloquear horário fora do funcionamento (RN09)

- **US:** US-05 · **RN:** RN09
- **Ambiente:** Docker local, seed aplicado, commit `4cfc485`
- **Executor:** Felipe · **Data:** 07/08/2026
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Acessar *Agenda*, selecionar médico `Dr. Silva` e data `11/08/2026` | `01-estado-inicial.png` — formulário vazio |
| 2 | Informar horário `07:59` e clicar em *Adicionar* | `02-tentativa-07-59.png` — notificação "Horário fora do expediente / A agenda funciona das 08:00 às 18:00", horário **não** entra na lista |
| 3 | Informar horário `08:00` e clicar em *Adicionar* | `03-tentativa-08-00.png` — aceito, pill `08:00` adicionada |
| 4 | Informar horário `17:59` e clicar em *Adicionar* | `04-tentativa-17-59.png` — aceito, pill `17:59` adicionada (mantendo `08:00`) |
| 5 | Informar horário `18:00` e clicar em *Adicionar* | `05-tentativa-18-00.png` — notificação "Horário fora do expediente", lista continua só com `08:00` e `17:59` |
| 6 | Informar horário `19:00` e clicar em *Adicionar* | `06-tentativa-19-00.png` — notificação "Horário fora do expediente", lista inalterada |
| 7 | Clicar em *Gerar grade* com os horários válidos acumulados | `07-grade-gerada.png` — notificação "2 horário(s) criado(s) para 2026-08-11"; card "Horários criados nesta sessão" lista `2026-08-11 · 08:00:00` e `2026-08-11 · 17:59:00` |

## Verificação RN09 (agenda só em horário comercial 08:00–18:00)

- `07:59`, `18:00` e `19:00` foram bloqueados **antes de qualquer envio à API** — o front-end
  (`AgendaPage`) valida o intervalo `08:00 <= horário < 18:00` no cliente e nunca chega a
  disparar o `POST /medicos/{id}/agenda` para esses valores.
- `08:00` e `17:59` foram aceitos no formulário e, ao gerar a grade, **persistidos** com sucesso
  (confirmado pela resposta `2 horário(s) criado(s)` e pelos badges com os horários exatos).
- `18:00` fica de fora por design: a validação é `08:00 <= h < 18:00`, então a última consulta
  do dia começa às 17:59.

## Observações

- Nenhum bug funcional encontrado neste CT.
- As datas são mostradas ao usuário no formato ISO 8601, o que não é incorreto, mas é raro para GUIs
