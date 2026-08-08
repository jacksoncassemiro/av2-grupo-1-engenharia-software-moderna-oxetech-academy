# CT05 — Bloquear agendamento em horário já ocupado (RN03)

- **US:** US-05, US-08, US-09 · **RN:** RN03
- **Ambiente:** Docker local, seed aplicado
- **Executor:** Uanderson · **Data:** 08/08/2026
- **Resultado:** ✅ passou

## Pré-condição

Dr. Silva (Clínica Geral) com `14:00` e `15:00` cadastrados em `2026-08-12` — confirmado pelo
toast "2 horário(s) criado(s) para 2026-08-12".

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Atendente busca Carlos (CPF `529.982.247-25`) e agenda com Dr. Silva às `14:00` | `01-consulta-confirmada-atendente.png` — "Consulta agendada para Carlos Souza", status **CONFIRMADA** |
| 2 | Atendente busca Carlos novamente, calendário mostra só `15:00` livre | `02-apenas-15h-livre.png` — `14:00` corretamente ausente da lista de horários livres |
| 3 | Login como Carlos, *Agendar Consulta* → Dr. Silva, `12/08/2026` | `03-paciente-ve-apenas-15h.png` — "Horários livres" mostra apenas **15:00**, confirmado do lado do próprio paciente |
| 4 | (Teste de API) Requisição `POST /api/atendente/consultas` forçando o `horario_disponivel_id: 1` já ocupado | `04-postman-409-conflito.png` — Retorno da API com Status **409 Conflict** e erro `HorarioIndisponivel` |

## Resposta exata do servidor (tentativa de conflito, RN03 em profundidade)

A UI nunca oferece um horário já ocupado como opção clicável — a tela filtra a lista antes de
renderizar. Para provar que o **backend** também recusa (não só a tela), chamei
`POST /api/atendente/consultas` diretamente com o `horario_disponivel_id` do slot das 14:00 já
ocupado:

```
POST /api/atendente/consultas {"paciente_id": 2, "horario_disponivel_id": 1} → 409
{"detail":"Horario indisponivel","erro":"HorarioIndisponivel"}
```

## Observações

- O fato de a UI nunca expor um horário ocupado como clicável é um comportamento de segurança
  correto, mas por si só não prova a defesa do servidor — daí a chamada de API direta acima.
