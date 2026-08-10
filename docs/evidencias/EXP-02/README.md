# EXP-02 — Agendamento e concorrência

- **Charter:** Explorar o agendamento buscando falhas de estado e concorrência (US-07, US-08, US-09)
- **Ambiente:** Docker local, seed aplicado, commit `0db12dd`
- **Executor:** Felipe · **Data:** 09/08/2026
- **Resultado:** ❌ 3 bugs encontrados

Massa de dados usada na sessão: médico "Dra. Ana Souza" (Clinica Geral), agenda em 15/08/2026
com horários 09:00, 10:00, 11:00 e 14:00, paciente "Maria Oliveira" (auto-cadastro, CPF-B) e
paciente "Carlos" (auto-cadastro, CPF-A).

---

## Bug 1 — `PATCH /atendente/consultas/{id}/status` cancela sem liberar o slot (viola RN03)

- **US:** US-13 · **RN:** RN03, RN06, RN10
- **Severidade sugerida:** Major · **Prioridade sugerida:** Alta
- **Alcançável pelo frontend:** Não — só via chamada direta à API (demonstrado pelo Swagger).
  Na tela `http://localhost:3000/gerenciar-consultas`, a tabela "Todas as consultas" só envia
  `CONFIRMADA`/`FINALIZADA` para esse endpoint; o cancelamento na tela sempre usa o endpoint
  dedicado `/cancelar`.

### Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Login como atendente no Swagger (`/api/auth/login`) e autorizar | `bug1-01-swagger-autorizado.png` |
| 2 | `POST /api/atendente/consultas` com `horario_disponivel_id=3` (11:00) e `paciente_id` da Maria → consulta nasce **CONFIRMADA** | `bug1-02-criar-consulta-confirmada.png` |
| 3 | `GET /api/medicos/1/horarios-livres?data=2026-08-15` → 11:00 corretamente ausente (ocupado) | `bug1-03-horario-ocupado.png` |
| 4 | Em vez de `PATCH /consultas/{id}/cancelar`, executar `PATCH /api/atendente/consultas/{id}/status` com `{"status": "CANCELADA"}` → 200 | `bug1-04-cancelar-via-status.png` |
| 5 | Repetir o passo 3 → **11:00 continua ausente da lista**, mesmo com a consulta cancelada | `bug1-05-horario-ainda-bloqueado.png` |

### Observado vs. esperado

- **Observado:** o horário fica bloqueado permanentemente. `mudar_status()` (`consulta_service.py`)
  nunca toca `horario_disponivel.disponivel`; só `cancelar()` faz isso. Como `TRANSICOES_PERMITIDAS`
  aceita `SOLICITADA/CONFIRMADA → CANCELADA`, o endpoint genérico de status aceita cancelar sem
  passar pela liberação do slot.
- **Esperado (RN03):** cancelar uma consulta, por qualquer rota, deve liberar o horário para novo
  agendamento.

---

## Bug 2 — Lost update entre confirmar (atendente) e cancelar (paciente) concorrentes

- **US:** US-08, US-09, US-13 · **RN:** RN03, RN06, RN10
- **Severidade sugerida:** Major · **Prioridade sugerida:** Média
- **Alcançável pelo frontend:** Sim — são os botões reais "Confirmar" (atendente) e "Cancelar"
  (paciente) na mesma consulta, sem manipular requisição.

### Observação sobre o método

Em ambiente local, o round-trip de cada requisição é da ordem de milissegundos, o que torna a
janela de corrida real quase impossível de acertar clicando manualmente (sequência de cliques em
duas abas é, na prática, serializada pelas próprias ferramentas de automação/click). Para conseguir
a evidência de forma confiável, um `time.sleep()` temporário foi inserido em
`ConsultaService.mudar_status()` (entre a leitura e a escrita) só durante a sessão de teste, para
alargar a janela — a mesma técnica de qualquer teste de condição de corrida. **A alteração foi
revertida após a coleta**; nenhum código de produção ficou modificado. O bug em si não depende
dessa alteração — ela só compensa a lentidão da interação manual, o que em produção aconteceria
naturalmente sob carga real (dois requests processados por workers/threads diferentes).

### Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Paciente Maria solicita consulta às 15/08/2026 10:00 (fica **SOLICITADA**) | `bug2-01-paciente-solicita-10h.png` |
| 2 | Atendente clica **Confirmar** nessa consulta (`PATCH /atendente/consultas/{id}/status`) | — |
| 3 | Antes da resposta do passo 2 chegar, a própria Maria clica **Cancelar** na mesma consulta (`PATCH /consultas/{id}/cancelar`) — a chamada de cancelamento lê o estado ainda como SOLICITADA e comita primeiro | `bug2-02-corrida-confirmar-e-cancelar.png` |
| 4 | A chamada de confirmação (que já tinha lido SOLICITADA antes do cancelamento) comita depois, sobrescrevendo só a coluna `status` para **CONFIRMADA** | `bug2-03-consulta-confirmada-apos-cancelamento.png` |
| 5 | `GET /medicos/1/horarios-livres` mostra o horário 10:00 como **livre**, apesar de existir uma consulta **CONFIRMADA** ocupando-o | `bug2-04-horario-aparece-livre.png` |

### Observado vs. esperado

- **Observado:** `mudar_status()` não usa `SELECT ... FOR UPDATE` (diferente de `_reservar_slot()`,
  que usa exatamente para evitar este tipo de corrida). Sob concorrência real, uma leitura obsoleta
  permite que a confirmação sobrescreva um cancelamento já commitado, sem tocar
  `horario_disponivel.disponivel` — o slot fica marcado como livre mesmo ocupado por uma consulta
  ativa.
- **Esperado:** o estado final de `consulta.status` e `horario_disponivel.disponivel` deveria ser
  sempre consistente entre si — nunca uma consulta CONFIRMADA com o próprio horário listado como
  disponível.
- **Contorno:** o índice único parcial `uq_slot_ativo` impede uma *segunda* consulta ativa de ser
  criada para o mesmo horário (a tentativa de reservar cai em `existe_ativa_no_slot()` e falha com
  409), então o bug não gera duas consultas ativas — só o dado inconsistente entre as duas tabelas.

---

## Bug 3 — Grade de horários do atendente não atualiza após 409 (estado obsoleto)

- **US:** US-09 · **RN:** RN03
- **Severidade sugerida:** Minor · **Prioridade sugerida:** Baixa/Média
- **Alcançável pelo frontend:** Sim — nenhuma manipulação de requisição, só duas sessões de
  atendente disputando o mesmo horário.

### Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Duas sessões de atendente (logins independentes) abrem "Agendar para paciente" para o mesmo médico/data e marcam o horário 14:00 | `bug3-01-grade-obsoleta-14h-ainda-marcada.png` |
| 2 | Sessão B clica "Agendar consulta" primeiro → sucesso, paciente Maria fica CONFIRMADA às 14:00 | — |
| 3 | Sessão A (sem recarregar a tela) clica "Agendar consulta" para o mesmo 14:00 → API responde 409 `HorarioIndisponivel` | `bug3-02-erro-mas-grade-nao-atualiza.png` |

### Observado vs. esperado

- **Observado:** o chip "14:00" continua marcado/clicável e o botão "Agendar consulta" continua
  habilitado na Sessão A depois do erro. Em `http://localhost:3000/gerenciar-consultas` (seção
  "Agendar para paciente"), o erro só mostra a notificação, sem recarregar `horarios-livres` —
  diferente do fluxo do paciente em `http://localhost:3000/agendar`, que recarrega a grade no
  `catch`.
- **Esperado:** mesmo comportamento do fluxo do paciente — recarregar a grade após falha, removendo
  o horário que acabou de ser ocupado.

---

## Observações gerais da sessão

- Nenhum dos três bugs foi encontrado pelos casos de teste funcionais (CT01–CT14), que cobrem o
  caminho feliz e as regras de negócio isoladamente — os três só aparecem sob concorrência ou uso
  de rota fora do fluxo padrão da UI, exatamente o que EXP-02 se propõe a explorar.
- Bug 2 e bug 3 têm a mesma causa-raiz de fundo: os fluxos de troca de status/cancelamento pelo
  atendente não foram escritos com a mesma atenção a estado obsoleto/concorrência que o fluxo de
  reserva original (`_reservar_slot`) recebeu.
