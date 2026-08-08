# CT08 — Bloquear alocação dupla do mesmo médico (RN05)

- **US:** US-05 · **RN:** RN05
- **Ambiente:** Docker local, seed aplicado, commit `a166bd2`
- **Executor:** Felipe · **Data:** 07/08/2026
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Confirmar pré-condição: `Dr. Silva` cadastrado e ativo | `01-medicos-cadastrados.png` — CRM12345, especialidade Clínica Geral, status ATIVO |
| 2 | Acessar *Agenda*, selecionar `Dr. Silva`, data `12/08/2026`, adicionar `14:00` e clicar *Gerar grade* | `02-lancado-14-00.png` — notificação "1 horário(s) criado(s) para 2026-08-12"; card "Horários criados nesta sessão" com `2026-08-12 · 14:00:00` |
| 3 | Adicionar `14:00` novamente e também `16:00` (duas pills) e clicar *Gerar grade* | `03-lancado-14-00-16-00.png` — notificação de erro "Não foi possível gerar a grade / Medico ja possui consulta agendada para este horario" |
| 4 | Verificar no banco se existe algum slot duplicado | `04-banco-correto.png` — pgAdmin, `SELECT medico_id, data, horario, COUNT(*) FROM horario_disponivel GROUP BY 1,2,3 HAVING COUNT(*) > 1;` → **0 linhas** |

## Verificação RN05 (médico não pode ter dois slots no mesmo dia/hora)

- O segundo lançamento (`14:00` + `16:00`) foi rejeitado por completo com a mensagem exata
  da regra de negócio: "Medico ja possui consulta agendada para este horario".
- `16:00` era um horário novo e válido, mas não foi criado junto — o lote inteiro é tratado
  como uma unidade, então a duplicidade em `14:00` impede que `16:00` seja salvo também. O card
  "Horários criados nesta sessão" não foi atualizado após o erro, e a consulta de duplicidade no
  banco (passo 4) retornou vazia, confirmando que nenhum registro extra ficou pendente.

## Observações

- Nenhum bug funcional encontrado neste CT.
- A mensagem de erro "Medico ja possui consulta agendada para este horario" (vista em
  `03-lancado-14-00-16-00.png`) está sem acentuação.
