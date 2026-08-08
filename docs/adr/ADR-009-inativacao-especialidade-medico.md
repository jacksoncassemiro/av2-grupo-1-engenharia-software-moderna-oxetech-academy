# ADR-009 — Inativação de especialidade e médico entra no MVP

**Status:** Aceito · **Data:** 2026-08-07 · **Decisores:** PO + Equipe 01
**Substitui:** [ADR-008](ADR-008-rebaseline-escopo.md) §1, **apenas** no ponto do corte de
MF03 e MF04. Todo o resto do ADR-008 continua valendo.

## Contexto

O [ADR-008](ADR-008-rebaseline-escopo.md) congelou o escopo em 14 User Stories (US-00 a US-13)
e mandou para `docs/15-melhorias-futuras.md` tudo o que não fosse estritamente o enunciado.
Entre os cortes estavam:

- **MF03 — Edição e exclusão de especialidades** (era parte da US-01)
- **MF04 — Edição e inativação de médicos** (era parte da US-02)

A auditoria de conformidade de 07/08 encontrou que **a metade de "inativação" desses dois itens
já foi implementada e mergeada na `develop`**, com backend, tela e teste:

| Rota | Arquivo | Tela |
|---|---|---|
| `PATCH /api/especialidades/{id}/status` | `especialidade_router.py` (`alternar_status`) | botão ativar/inativar em `(atendente)/especialidades` |
| `PATCH /api/medicos/{id}/status` | `medico_router.py` (`alternar_status`) | botão ativar/inativar em `(atendente)/medicos` |

Ou seja: o código entregue passou o escopo documentado. Ficar com a documentação dizendo
"melhoria futura v1.1" enquanto a funcionalidade está em produção na branch é pior do que
qualquer das duas alternativas — some com a rastreabilidade requisito → código → teste, que é
justamente o que a AV2 avalia.

A regra do projeto ([`docs/adr/README.md`](README.md)) é que ADR aceito não se edita. Daí este
ADR novo em vez de uma correção no ADR-008.

## Decisão

### 1. A inativação entra no MVP; a edição e a exclusão continuam fora

Esta é a parte que exige cuidado: **MF03 e MF04 não foram entregues por inteiro.** O que existe
é somente o liga/desliga do campo `ativo`.

| Item | Entra no MVP agora | Continua fora (v1.1) |
|---|---|---|
| MF03 — especialidades | Inativar e reativar | **Editar** o nome; **excluir** o registro |
| MF04 — médicos | Inativar e reativar | **Editar** nome, e-mail, CRM ou especialidade |

A exclusão física continua fora por um motivo de domínio, não de prazo: apagar uma
especialidade ou um médico quebraria o histórico de consultas já realizadas, que referencia
os dois. A inativação lógica resolve a necessidade real ("este médico não atende mais") sem
esse efeito colateral.

### 2. Inativar preserva o passado e barra o futuro (RN16)

A auditoria também descobriu que a inativação estava **pela metade**: o médico sumia das
listagens, mas a agenda dele continuava sendo oferecida e `POST /api/consultas` num slot seu
respondia **201**. Um paciente com a URL `/agendar?medico=<id>` aberta agendava normalmente
com um médico desativado.

A ficha do MF04 em `15-melhorias-futuras.md` dizia que faltava "definir o que acontece com os
horários futuros e as consultas já marcadas de um médico inativado". Fica definido:

- **Consultas já existentes não mudam de status.** Não há cancelamento em cascata. O histórico
  do paciente permanece íntegro, e uma consulta já confirmada continua valendo — quem decide
  desmarcar é o atendente, caso a caso, pela US-12.
- **Nenhuma consulta nova é criada para médico inativo**, venha de paciente (US-08) ou de
  atendente (US-09). A regra é do domínio, não da tela.
- **A agenda de médico inativo não é oferecida**: `GET /api/medicos/{id}/horarios-livres`
  devolve lista vazia.

Isso está registrado como **RN16** em [`docs/01-requisitos.md`](../01-requisitos.md) e é
aplicado em `ConsultaService._reservar_slot` e `AgendaService.listar_livres`.

Cancelamento em cascata com aviso ao paciente continua fora do MVP — vira **MF16**.

### 3. O mesmo furo existia pelo lado da especialidade (RN17)

A revisão seguinte encontrou que a RN16 fechou só metade do buraco. Ela pergunta
`medico.ativo` — e nada mais. Inativar a **especialidade** deixava intacto o caminho todo:

| Passo | Antes da RN17 |
|---|---|
| `PATCH /api/especialidades/2/status` → `Cardiologia` inativa | os médicos dela continuam `ativo = true` |
| `GET /api/medicos?apenas_ativos=true` | ainda devolve os cardiologistas — é a lista de `/buscar-medicos` e de `/agendar` |
| `GET /api/medicos/{id}/horarios-livres` | ainda devolve a grade |
| `POST /api/consultas` | **201** |

Ou seja: dava para marcar consulta numa especialidade que a clínica acabou de desativar. Havia
ainda um efeito colateral de tela — como `/buscar-medicos` carrega só as especialidades ativas
para montar o rótulo, o card do médico aparecia com o `Badge` de especialidade **em branco**.

Fica decidido, no mesmo espírito da RN16 — **preservar o passado, barrar o futuro**:

- **Nada cascateia.** Inativar a especialidade não inativa os médicos dela e não muda o status
  de consulta alguma. O médico continua `ativo = true` e continua visível para o atendente em
  `Ativos` (com a especialidade rotulada `(inativa)`), senão ele sumiria da gestão — não
  estaria nem em `Ativos` nem em `Inativos` — e ninguém saberia como reativá-lo.
- **Nenhuma consulta nova**, venha de paciente (US-08) ou de atendente (US-09).
- **A agenda não é oferecida**: `horarios-livres` devolve lista vazia, inclusive para quem
  chega por `/agendar?medico=<id>` com a URL na mão.

Isso é a **RN17**. As duas regras têm o mesmo formato e por isso vivem juntas, em
`backend/app/services/disponibilidade_medico.py` — escrever a condição de novo dentro de cada
service é o que produziu a divergência em primeiro lugar. `pode_receber_consulta()` responde a
pergunta; `garantir_que_recebe_consulta()` levanta `MedicoInativo` (RN16) ou
`EspecialidadeInativa` (RN17), para que o 409 diga qual dos dois lados barrou.

A listagem ganhou `GET /api/medicos?apenas_agendaveis=true` — quem vai marcar consulta pergunta
por essa, não por `apenas_ativos`. Os dois filtros coexistem de propósito: `apenas_ativos` é a
visão de gestão do atendente, `apenas_agendaveis` é a visão de quem agenda.

## Consequências

**Positivas**

- Documentação volta a descrever o que o código faz. A rastreabilidade US → RN → código →
  teste fecha de novo.
- Fecha dois furos reais: era possível agendar com médico desativado (RN16) e com médico de
  especialidade desativada (RN17).
- A condição de "pode receber consulta" passa a existir em **um** lugar. Foi a duplicata dela
  entre `ConsultaService` e `AgendaService` que deixou a RN16 passar pela metade.
- Os critérios de aceite de US-01 e US-02 passam a cobrir o botão que já existe nas telas, o
  que dá ao QA o que testar.

**Negativas / custo aceito**

- O escopo do MVP cresce em relação ao ADR-008. É crescimento **reconhecido a posteriori**, não
  planejado: não há trabalho novo de implementação, só de documentação e do reparo da RN16.
- Abre precedente de "implementou primeiro, documentou depois". Mitigação: este ADR existe
  justamente para tornar o precedente visível; o fluxo continua sendo o do ADR-008 (escopo novo
  passa pelo PO em Planning).

## Alternativas consideradas

1. **Remover o código e manter o ADR-008 intacto.** Rejeitada: joga fora funcionalidade que já
   passou por PR, revisão e teste, e que o PO considera útil. Custo real sem ganho real.
2. **Deixar como está, código à frente da documentação.** Rejeitada: é exatamente a divergência
   que a auditoria existe para eliminar, e a rastreabilidade é entregável avaliado.
3. **Trazer MF03 e MF04 inteiros (com edição e exclusão).** Rejeitada: edição não está
   implementada, e a exclusão física tem o problema de integridade descrito acima. Entrar com
   elas agora seria escopo novo de verdade, a 3 dias da entrega.
