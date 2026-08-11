[README.md](https://github.com/user-attachments/files/30952663/README.md)
# EXP-03 — Antecedência de cancelamento (RN15), transições de status e isolamento entre pacientes

- **Charter:** Explorar a regra de antecedência mínima de 24h para cancelamento pelo paciente
  (US-12, RN15), validando especificamente a fronteira do cálculo e o fuso horário considerado, as
  guardas de transição para estados terminais, o isolamento de dados entre pacientes e a exceção de
  antecedência concedida ao atendente.
- **Ambiente:** Docker local, seed aplicado
- **Data:** 11/08/2026
- **Resultado:** 1 achado a confirmar (RN15 / fuso horário) + 3 verificações de guarda (evidências
  de regressão, sem bug encontrado)

### Escopo desta sessão

| # | Cenário testado | Resultado |
|---|---|---|
| 1 | Consulta exatamente na fronteira: 24h00, 23h59 e 24h01 de antecedência |  Ver **Bug 1** |
| 2 | Cálculo respeita `America/Maceio` (RN15) e não UTC diferença de 3h |  Ver **Bug 1** |
| 3 | Cancelar consulta já cancelada; finalizar consulta cancelada; confirmar consulta finalizada |  Ver **Achado 2** |
| 4 | Paciente tentando cancelar consulta de outro paciente (trocar o `id` na URL) |  Ver **Achado 3** |
| 5 | Atendente cancelando consulta que começa em 1h (deve permitir) |  Ver **Achado 4** |

---

## Bug 1 — Fronteira de 24h (RN15): cálculo pode não respeitar `America/Maceio`, com desvio de ~3h **[a confirmar]**

- **US:** US-12 · **RN:** RN15 (antecedência mínima de 24h para cancelamento pelo paciente, em
  `America/Maceio`)
- **Severidade sugerida:** Major (se confirmado) · **Prioridade sugerida:** Alta
- **Evidências:** `bug1-consulta-com-23h59m-24h00m-de-antecedencia.png`,
  `bug1-consulta-com-24h01m-de-antecedencia.png`

### Passos

| # | Passo | Evidência |
|---|---|---|
| 1 | Criar três consultas CONFIRMADAS deliberadamente na fronteira de 24h de antecedência (≈23h59, ≈24h00, ≈24h01) e consultar `GET /api/atendente/consultas?status=CONFIRMADA` | `bug1-consulta-com-23h59m-24h00m-de-antecedencia.png` |
| 2 | Rolar a mesma resposta para o próximo registro (criado poucos segundos depois) e comparar o campo `pode_cancelar` | `bug1-consulta-com-24h01m-de-antecedencia.png` |

### Dados brutos das evidências

| Consulta | Criada em (UTC, campo `data_agendamento`) | Agendada para (`data` + `horario`) | Antecedência se `horario` for **UTC** | Antecedência se `horario` for **America/Maceio (UTC-3)** | `pode_cancelar` observado |
|---|---|---|---|---|---|
| id 16 | 2026-08-11T18:23:10Z | 2026-08-12 15:22:00 | ~20h58m | ~23h58m | `false` |
| id 17 | 2026-08-11T18:23:19Z | 2026-08-12 15:23:00 | ~20h59m | ~23h59m | `false` |
| id 18 | 2026-08-11T18:23:24Z | 2026-08-12 15:24:00 | ~21h00m | ~24h00m | `true` |

### Observado vs. esperado

- **Observado:** o `pode_cancelar` vira de `false` para `true` entre id 17 e id 18 uma janela de
  cerca de 1 minuto de diferença no horário agendado. Isso só faz sentido se o backend estiver, de
  fato, avaliando a antecedência a partir do horário local `America/Maceio` (coluna da direita na
  tabela acima), já que só nessa interpretação a fronteira de 24h cai exatamente nesse ponto pela
  interpretação em UTC puro (coluna do meio), nenhuma das três consultas chegaria perto de 24h de
  antecedência, e ainda assim `pode_cancelar` já teria virado `true` para id 18 com apenas ~21h.
- **Esperado (RN15):** a antecedência mínima de 24h deve ser sempre calculada em `America/Maceio`,
  de forma consistente em todos os pontos do sistema que dependem dela (endpoint de listagem que
  preenche `pode_cancelar`, validação do próprio `PATCH .../cancelar` no fluxo do paciente, e
  qualquer outro lugar que replique essa regra).
- **Por que ainda está como "a confirmar":** este conjunto específico de evidências é compatível com
  o cálculo já estar correto (usando `America/Maceio`) neste endpoint o resultado observado bate
  com a coluna certa da tabela. O ponto em aberto é justamente o que motivou este teste: confirmar
  se **todos** os pontos do sistema que usam essa regra (não só a listagem) fazem a mesma conversão
  de fuso, e não apenas alguns um mismatch de 3h entre `now` (UTC) e o horário salvo da consulta
  (local) é o tipo de bug que só aparece de forma intermitente, dependendo de qual código-caminho é
  exercitado. Recomenda-se repetir o mesmo teste de fronteira (a) diretamente no endpoint de
  cancelamento do paciente (`PATCH /api/consultas/{id}/cancelar`), não só na listagem do atendente, e
  (b) checar no código/logs qual função de "agora" (`utcnow()` vs. `now()` com timezone) é usada em
  cada ponto que aplica a RN15.

---

## Achado 2 — Guardas de transição para estados terminais (CANCELADA/FINALIZADA) ✅ funcionando

- **US:** US-13 · **RN:** máquina de transições de status (`TRANSICOES_PERMITIDAS`)
- **Classificação:** Não é bug evidência de regressão positiva
- **Evidências:** `bug02-01-finalizar-consulta-cancelada.png`, `bug2-02-confirmar-consulta-finalizada.png`,
  `bug2-cancelar-consulta-cancelada.png`

### Passos e evidências

| # | Passo | Resultado | Evidência |
|---|---|---|---|
| 1 | `PATCH /api/atendente/consultas/1/status` tentando ir de CANCELADA → FINALIZADA | `422 TransicaoDeStatusInvalida` | `bug02-01-finalizar-consulta-cancelada.png` |
| 2 | `PATCH /api/atendente/consultas/3/status` com `{"status":"FINALIZADA"}` numa consulta que já estava FINALIZADA | `422 TransicaoDeStatusInvalida` ("Nao e permitido ir de FINALIZADA para FINALIZADA") | `bug2-02-confirmar-consulta-finalizada.png` |
| 3 | `PATCH /api/atendente/consultas/1/cancelar` numa consulta que já estava CANCELADA | `422 TransicaoDeStatusInvalida` ("Nao e permitido ir de CANCELADA para CANCELADA") | `bug2-cancelar-consulta-cancelada.png` |

### Observado vs. esperado

- **Observado:** nos três casos a API rejeitou corretamente a transição inválida com `422` e mensagem
  específica (`TransicaoDeStatusInvalida`), tanto pelo endpoint genérico `/status` quanto pelo
  dedicado `/cancelar`.
- **Esperado:** exatamente esse comportamento estados terminais (CANCELADA, FINALIZADA) não devem
  aceitar novas transições.
- **Ponto de atenção (não bloqueante):** vale confirmar que a UI desabilita "Finalizar"/"Cancelar" na
  tabela antes dessas chamadas serem disparadas, para não depender só do `422` do backend para
  impedir o clique.

---

## Achado 3 — Paciente tentando cancelar consulta de outro paciente ✅ bloqueado

- **US:** US-08/US-09 · **RN:** isolamento de dados entre pacientes
- **Classificação:** Não é bug comportamento correto, com uma ressalva de padronização
- **Evidência:** `bug3-cancelar-consulta-outro-paciente.png`

### Passos e evidência

| # | Passo | Resultado | Evidência |
|---|---|---|---|
| 1 | Autenticado como um paciente, trocar o `id` na URL e chamar `PATCH /api/consultas/6/cancelar`, referenciando uma consulta que pertence a outro paciente | `404 RecursoNaoEncontrado` ("Consulta nao encontrada") | `bug3-cancelar-consulta-outro-paciente.png` |

### Observado vs. esperado

- **Observado:** a API não permitiu o cancelamento da consulta de outro paciente a consulta não foi
  encontrada no escopo do usuário autenticado, e nenhum dado da consulta de terceiros foi exposto.
- **Esperado:** acesso cruzado entre pacientes deve ser bloqueado, o que de fato aconteceu.
- **Ponto de atenção:** retornar `404` (em vez de `403 Forbidden`) para "existe mas não é seu" evita
  vazar a existência do recurso, o que é uma escolha de design válida mas vale confirmar se essa é
  a convenção adotada de forma consistente no resto da API, para não misturar `403`/`404` para o
  mesmo tipo de violação em endpoints diferentes.

---

## Achado 4 — Atendente cancela consulta que começa em 1h ✅ permitido, como esperado (US-12)

- **US:** US-12 · **RN:** exceção de antecedência mínima concedida ao atendente
- **Classificação:** Não é bug comportamento intencional, confirmado pela própria UI
- **Evidências:** `bug4-cancelar-consulta-1h-antecedencia.png`,
  `bug4-01-cancelar-consulta-1h-antecedencia-via-status.png`,
  `bug4-01-cancelar-consulta-1h-antecedencia.png`

### Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Em `/gerenciar-consultas`, atendente clica em "Cancelar" numa consulta CONFIRMADA que começa em ~1h; o modal de confirmação avisa explicitamente: *"O atendente pode cancelar mesmo com menos de 24h (US-12)"* | `bug4-cancelar-consulta-1h-antecedencia.png` |
| 2 | Confirma o cancelamento → `PATCH /api/atendente/consultas/9/cancelar` retorna `200`, consulta passa para `CANCELADA` | `bug4-01-cancelar-consulta-1h-antecedencia-via-status.png` |
| 3 | Lista "Todas as consultas" filtrada por `Confirmada` deixa de exibir a consulta cancelada, com notificação "Consulta cancelada" | `bug4-01-cancelar-consulta-1h-antecedencia.png` |

### Observado vs. esperado

- **Observado:** o atendente conseguiu cancelar uma consulta com bem menos de 24h de antecedência, e
  a própria interface avisa que essa é uma exceção permitida (US-12). Após o cancelamento, a lista
  filtrada por CONFIRMADA atualiza corretamente e não mostra mais a consulta.
- **Esperado:** exatamente esse comportamento a restrição de 24h (RN15) vale para o paciente, não
  para o atendente.
- **Contraste com o Bug 1:** este achado confirma que a exceção do atendente funciona; o que ainda
  precisa de confirmação é se o cálculo da janela de 24h em si (RN15) usa o fuso correto em todos os
  fluxos do lado do paciente.

---

## Observações gerais da sessão

- O único item com indício real de bug é o **Bug 1** (fronteira de 24h / RN15, possível mismatch
  UTC vs. `America/Maceio`); os achados 2, 3 e 4 são evidências de que as respectivas guardas
  (transição de status terminal, isolamento entre pacientes, exceção do atendente para <24h) estão
  funcionando como esperado, documentadas aqui como evidência de regressão.
- Para fechar o Bug 1, os próximos passos recomendados são: (a) repetir o teste de fronteira direto
  no endpoint de cancelamento do paciente, não só na listagem do atendente; e (b) checar no
  código/logs qual referência de "agora" é usada em cada ponto que aplica a RN15 (`utcnow()` vs.
  `now()` com timezone `America/Maceio`).
- Todas as evidências brutas (prints e respostas de API) estão em [`evidencias/`](./evidencias).

## Evidências

| Arquivo | Referente a |
|---|---|
| ![](evidencias/bug1-consulta-com-23h59m-24h00m-de-antecedencia.png) | Bug 1 — consulta ~23h59m–24h00m de antecedência |
| ![](evidencias/bug1-consulta-com-24h01m-de-antecedencia.png) | Bug 1 — consulta ~24h01m de antecedência |
| ![](evidencias/bug02-01-finalizar-consulta-cancelada.png) | Achado 2 — finalizar consulta cancelada |
| ![](evidencias/bug2-02-confirmar-consulta-finalizada.png) | Achado 2 — finalizar consulta já finalizada |
| ![](evidencias/bug2-cancelar-consulta-cancelada.png) | Achado 2 — cancelar consulta já cancelada |
| ![](evidencias/bug3-cancelar-consulta-outro-paciente.png) | Achado 3 — cancelar consulta de outro paciente |
| ![](evidencias/bug4-cancelar-consulta-1h-antecedencia.png) | Achado 4 — modal de confirmação (US-12) |
| ![](evidencias/bug4-01-cancelar-consulta-1h-antecedencia-via-status.png) | Achado 4 — chamada de cancelamento (200) |
| ![](evidencias/bug4-01-cancelar-consulta-1h-antecedencia.png) | Achado 4 — lista atualizada após cancelamento |
