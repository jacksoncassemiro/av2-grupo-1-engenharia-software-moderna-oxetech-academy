# Melhorias futuras — backlog de evolução

Tudo que foi **conscientemente deixado de fora do MVP** está aqui. Não é lista de esquecimento:
cada item tem motivo de exclusão, esforço estimado e o que precisaria acontecer para entrar.

A decisão de escopo está registrada em [ADR-008](adr/ADR-008-rebaseline-escopo.md).

> **Como usar isto na apresentação.** Quando o avaliador perguntar *"e por que não fizeram X?"*,
> a resposta não é "não deu tempo" — é apontar este documento e mostrar que X foi analisado,
> priorizado e adiado com critério. Escopo controlado é competência de Engenharia de Software,
> não limitação.

---

## 1. Como um item entra ou sai daqui

```
Ideia nova ──▶ Refinamento com o PO ──▶ cabe no prazo? ──sim──▶ vira US no backlog
                                              │
                                              └──não──▶ entra aqui, com versão-alvo
```

Regra: **nada é implementado sem passar pelo backlog.** Se surgir durante uma sprint, vai para
`v1.1` aqui e é discutido na próxima Planning.

---

## 2. Retirado do MVP durante o rebaseline (30/07)

Estes itens **existiam** no planejamento anterior e foram removidos.

### MF01 — Agenda geral consolidada da clínica

- **Era:** US-14 · RF22 · classificada como *Desejável*
- **O que é:** tela do atendente com todas as consultas de todos os médicos numa visão de
  calendário, filtrável por médico, especialidade e período.
- **Por que saiu:** não consta na lista de funcionalidades do enunciado. É uma visualização
  agregada, não uma capacidade nova — todos os dados já são acessíveis pelas telas do MVP.
- **Esforço:** M (backend de agregação + componente de calendário)
- **Versão-alvo:** v1.1

### MF02 — Tela de cadastro de atendente

- **Era:** US-15 · RF23
- **O que é:** formulário no qual um atendente autenticado cria outro atendente.
- **Por que saiu:** não consta no enunciado. O primeiro atendente é criado pelo seed idempotente
  ([ADR-004](adr/ADR-004-bootstrap-atendente.md)), o que basta para a demonstração e para os
  testes. **A RN14 continua valendo** — não existe rota pública de cadastro de atendente, e o
  backend recusa a criação por quem não é atendente.
- **Esforço:** P
- **Versão-alvo:** v1.1

### MF03 — Edição e exclusão de especialidades — ⚠️ **parcialmente entregue no MVP**

> **A inativação saiu daqui e entrou no MVP** pelo
> [ADR-009](adr/ADR-009-inativacao-especialidade-medico.md): `PATCH /api/especialidades/{id}/status`
> e o botão ativar/inativar já estavam implementados e mergeados. Virou o **RF23**, coberto pelo
> CA4 da US-01.
>
> A pergunta que estava em aberto aqui — o que acontece com os **médicos vinculados** a uma
> especialidade inativada — foi respondida pela **RN17**, na mesma forma da RN16: eles
> continuam `ativo = true` e as consultas deles não mudam de status, mas nenhum agendamento
> novo é aceito e a agenda deles não é oferecida.
>
> **Continua fora:** editar o nome e excluir o registro.

- **Era:** parte da US-01
- **Por que o resto continua fora:** a exclusão física quebraria o histórico de consultas, que
  referencia a especialidade pelo médico. A inativação lógica já resolve o caso real.
- **Precisaria antes:** definir o que fazer com médicos vinculados a uma especialidade
  **excluída** — a RN17 responde só o caso da inativação.
- **Esforço:** P
- **Versão-alvo:** v1.1

### MF04 — Edição de médicos — ⚠️ **parcialmente entregue no MVP**

> **A inativação saiu daqui e entrou no MVP** pelo
> [ADR-009](adr/ADR-009-inativacao-especialidade-medico.md): `PATCH /api/medicos/{id}/status` e o
> botão ativar/inativar já estavam implementados e mergeados. Virou o **RF24**, coberto pelo CA5
> da US-02.
>
> A pergunta que estava em aberto aqui — o que acontece com a agenda e as consultas de um médico
> inativado — foi respondida pela **RN16**: o passado é preservado (nenhuma consulta muda de
> status) e o futuro é barrado (não se agenda com médico inativo, e a agenda dele não é
> oferecida). Cancelamento em cascata com aviso ao paciente virou a MF16.
>
> **Continua fora:** editar nome, e-mail, CRM ou especialidade de um médico.

- **Era:** parte da US-02
- **Esforço:** P
- **Versão-alvo:** v1.1

### MF05 — Edição de dados do paciente pelo atendente

- **Era:** parte da US-03
- **Por que saiu:** o enunciado atribui a atualização cadastral **ao paciente** (US-04), e essa
  permanece no MVP. O atendente editar dados de terceiros levanta questão de auditoria que o
  MVP não trata.
- **Precisaria antes:** log de auditoria de quem alterou o quê.
- **Esforço:** P
- **Versão-alvo:** v1.2

### MF06 — Exclusão de horário livre da grade

- **Era:** parte da US-05
- **Por que saiu:** não consta no enunciado. Grade lançada errada se resolve lançando a grade
  correta; slots livres extras não quebram nenhuma regra.
- **Esforço:** P
- **Versão-alvo:** v1.1

---

## 3. Identificado durante a análise, nunca entrou no MVP

### MF07 — Notificação de consulta por e-mail

- **O que é:** e-mail de confirmação ao agendar e lembrete 24h antes.
- **Por que não:** exige serviço de envio, fila e tratamento de falha. É a maior fonte de
  complexidade acidental que se pode adicionar a um MVP deste tamanho.
- **Esforço:** G
- **Versão-alvo:** v2.0

### MF08 — Reagendamento em uma operação

- **O que é:** trocar a consulta de horário sem cancelar e criar outra.
- **Por que não:** hoje o fluxo é cancelar + agendar de novo, e funciona (CT10 cobre a
  liberação do slot). Uma operação atômica exigiria transação envolvendo dois slots e uma RN
  nova sobre a antecedência aplicável.
- **Esforço:** M
- **Versão-alvo:** v1.2

### MF09 — Perfil de Médico

- **O que é:** terceiro perfil, com o médico vendo a própria agenda e finalizando consultas.
- **Por que não:** o enunciado define **dois** perfis, Paciente e Atendente. Adicionar um
  terceiro muda o modelo de autorização inteiro.
- **Esforço:** G
- **Versão-alvo:** v2.0

### MF10 — Prontuário e histórico clínico

- **O que é:** registrar anamnese, diagnóstico e prescrição na consulta finalizada.
- **Por que não:** fora do escopo declarado ("substituir o agendamento por telefone e
  planilhas"). Traz exigências legais (LGPD, dado sensível de saúde, retenção) que um MVP
  acadêmico não deve simular por alto.
- **Esforço:** G
- **Versão-alvo:** v2.0

### MF11 — Recuperação de senha

- **O que é:** fluxo "esqueci minha senha" por e-mail.
- **Por que não:** depende de MF07. No MVP, a senha é redefinida pelo suporte/seed.
- **Esforço:** M
- **Versão-alvo:** v1.2

### MF12 — Paginação e busca nas listagens

- **O que é:** paginar e filtrar as listas de pacientes, médicos e consultas.
- **Por que não:** com o volume de dados do seed e da demonstração, listas completas cabem numa
  tela. É otimização sem problema a resolver ainda.
- **Esforço:** P
- **Versão-alvo:** v1.1

### MF13 — Refresh token

- **O que é:** renovar o JWT sem novo login.
- **Por que não:** a RN13 define expiração de 24h, o que cobre uma sessão de uso e a
  apresentação inteira.
- **Esforço:** M
- **Versão-alvo:** v1.2

### MF14 — Testes end-to-end automatizados (Playwright)

- **O que é:** automatizar os fluxos que hoje o QA executa à mão.
- **Por que não:** o entregável avaliado é **caso de teste executado com evidência**, e o custo
  de montar e estabilizar E2E em 8 dias competiria com o próprio desenvolvimento.
- **Esforço:** G
- **Versão-alvo:** v1.2

### MF15 — Deploy em ambiente hospedado

- **O que é:** publicar o sistema numa nuvem com URL pública.
- **Por que não:** decisão da equipe de rodar **tudo localmente**, com o GitHub hospedando
  apenas código, Wiki, board e CI. Deploy exigiria conta, custo e segredos que não temos.
- **Esforço:** M
- **Versão-alvo:** v2.0

### MF16 — Cancelamento em cascata ao inativar um médico

- **O que é:** ao inativar um médico com consultas futuras, cancelá-las automaticamente e
  avisar cada paciente.
- **Por que não agora:** a **RN16** ([ADR-009](adr/ADR-009-inativacao-especialidade-medico.md))
  decidiu o mínimo seguro — inativar preserva as consultas existentes e apenas barra novos
  agendamentos. Cancelar em cascata exige uma política de aviso ao paciente, que depende da
  MF07 (notificações) para não deixar ninguém sabendo só ao chegar na clínica.
- **Precisaria antes:** MF07.
- **Esforço:** M
- **Versão-alvo:** v2.0

---

## 4. Resumo por versão

| Versão | Itens | Tema |
|---|---|---|
| **v1.0 (MVP — 10/08)** | US-00 a US-13 + RF23/RF24 (inativação, com RN16 e RN17 — [ADR-009](adr/ADR-009-inativacao-especialidade-medico.md)) | Agendamento funcionando ponta a ponta com os dois perfis |
| **v1.1** | MF01, MF02, MF03, MF04, MF06, MF12 | Completar o CRUD e a visão consolidada |
| **v1.2** | MF05, MF08, MF11, MF13, MF14 | Conveniência de uso e automação de testes |
| **v2.0** | MF07, MF09, MF10, MF15 | Notificações, terceiro perfil, prontuário, deploy |

---

## 5. Entrega parcial: o que fazer se uma US não couber

Se o prazo apertar, a regra é **cortar a User Story inteira**, não entregar metade dela
([ADR-008](adr/ADR-008-rebaseline-escopo.md) §2). Uma US com backend pronto e sem tela não
produz evidência de teste, e evidência de teste é entregável avaliado.

Quando isso acontecer:

1. O PO move a US para **"Fora do MVP"** no board, com comentário explicando o motivo.
2. Um item correspondente é criado **aqui**, com o que já existia aproveitado.
3. O item entra no slide de retrospectiva como decisão consciente de escopo.

Ordem de corte definida na Planning:

| Prioridade | User Stories | O que se perde |
|---|---|---|
| **P0 — não corta** | US-00, US-01, US-02, US-03, US-05, US-08, US-11 | RN01 a RN05 deixariam de ser demonstráveis |
| **P1** | US-07, US-09, US-12, US-13 | RN06 incompleta; fluxo do atendente pela metade |
| **P2 — corta primeiro** | US-04, US-06, US-10 | Conveniência; nenhuma RN obrigatória fica descoberta |
