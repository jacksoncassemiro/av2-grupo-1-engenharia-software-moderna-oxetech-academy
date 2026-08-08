# CT07 — Bloquear cancelamento do paciente com menos de 24h (RN04)

- **US:** US-11 · **RN:** RN04, RN15
- **Ambiente:** Docker local, seed aplicado
- **Executor:** Uanderson · **Data:** 08/08/2026
- **Resultado:** ✅ passou

## Método usado (nota de execução exigida pelo plano)

Sem alterar `.env` nem o relógio do servidor: aproveitei que o horário real do teste era
`2026-08-08 16:34` (fuso `America/Maceio`) e lancei um horário para o dia seguinte às `08:00`
(`2026-08-09 08:00`), ficando a ~11h de antecedência — dentro da janela "menos de 24h" com
folga suficiente para não depender de segundos de execução.

## Pré-condição

Carlos com consulta CONFIRMADA em `Dr. Silva / 2026-08-09 08:00` (agendada pelo atendente).

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Login como Carlos, acessar *Minhas Consultas* | `01-acoes-bloqueadas-menos-24h.png` — a linha das `08:00` mostra **"—"** em Ações: a própria UI já esconde o botão Cancelar (`pode_cancelar: false`) |
| 2 | Tentar cancelar mesmo assim, via API direta (bypass da UI) | ver resposta abaixo |

## Resposta exata do servidor

```
PATCH /api/consultas/{id}/cancelar → 422
{"detail":"Cancelamento indisponivel. Prazo de antecedencia menor que 24 horas","erro":"CancelamentoNaoPermitido"}
```

## Observações

- RN15 (fuso `America/Maceio`) confirmado indiretamente: o cálculo de "11h de antecedência" bateu
  com o relógio local da máquina de teste, que está no mesmo fuso — o backend usa
  `agora_da_clinica()`, coberto também pelos testes unitários `CTU04`/`CTU04b`.
- Verificado também em EXP-03 (probe C) o lado oposto da fronteira: consulta a ~34h45 de
  distância foi cancelada com sucesso (`200`), confirmando que o limiar de 24h é respeitado nos
  dois sentidos, não só bloqueando.