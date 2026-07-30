# Product Backlog

Entregável do PO. US-00 a US-12 vêm do backlog original da Wiki; **US-13** foi adicionada para
cobrir a lacuna dos quatro status da RN06, identificada em
[14-conflitos-e-decisoes.md](14-conflitos-e-decisoes.md).

Formato: _Como… Quero… Para…_ com critérios de aceite em Gherkin e tarefas marcadas
`[BACKEND]` / `[FRONTEND]` / `[QA]`.

> **Escopo do MVP (rebaseline de 30/07).** São **14 User Stories, US-00 a US-13** — exatamente
> as 13 funcionalidades dos dois perfis do enunciado, mais autenticação. As antigas US-14
> (agenda geral) e US-15 (cadastro de atendente pela interface) saíram do MVP e viraram MF01 e
> MF02 em [`15-melhorias-futuras.md`](15-melhorias-futuras.md). Justificativa completa no
> [ADR-008](adr/ADR-008-rebaseline-escopo.md).

---

## Priorização

| Sprint | US | Meta |
| ------ | -- | ---- |
| **1** (31/07 – 05/08) | US-00, US-01, US-02, US-03, US-05 | Acesso + cadastros base |
| **2** (05/08 – 10/08) | US-04, US-06, US-07, US-08, US-09, US-10, US-11, US-12, US-13 | Agendamento + cancelamento |

| Prioridade | US | Se o prazo apertar |
| ---------- | -- | ------------------ |
| **P0** | US-00, US-01, US-02, US-03, US-05, US-08, US-11 | Não corta — sustentam RN01–RN05 |
| **P1** | US-07, US-09, US-12, US-13 | Completam a RN06 e o fluxo do atendente |
| **P2** | US-04, US-06, US-10 | Corta primeiro; contornáveis na demonstração |

**Regra de corte:** a User Story sai **inteira**. Não se entrega backend sem tela — sem fluxo
navegável o QA não produz evidência, e evidência é entregável avaliado
([ADR-008](adr/ADR-008-rebaseline-escopo.md) §2).

---

## Convenção de login (decisão de produto)

A tela de login tem **um único campo: "CPF ou E-mail"**.

- **Paciente** entra com o **CPF** — essencial, porque paciente de balcão pode não ter e-mail.
- **Atendente** entra com o **e-mail** profissional.

**Contas separadas por papel.** Se um atendente for também paciente da clínica, ele terá duas
contas: uma com `login = silva@clinica.com` (ATENDENTE) e outra com `login = 12345678900`
(PACIENTE). Isso evita auto-atendimento e simplifica a autorização.

Detalhes em [ADR-003](adr/ADR-003-autenticacao.md).

---

# Épico 0 — Autenticação e acesso

## US-00 — Autenticação e vinculação de conta por CPF

> **Como** Paciente ou Atendente
> **Quero** fazer login ou ativar meu primeiro acesso usando meu CPF ou e-mail
> **Para** acessar a plataforma conforme o meu perfil

**Sprint 1 · P0 · Regras:** RN01, RN02, RN07, RN11, RN12, RN13

### Critérios de aceite

**CA1 — Login do paciente por CPF** — **Dado** que sou um paciente com CPF `529.982.247-25` e senha `senha123`, **quando** eu digitar `52998224725` no campo "CPF ou E-mail" e minha senha, **então** o sistema deve permitir o acesso e me redirecionar para o painel do paciente

**CA2 — CPF com máscara é aceito** — **Dado** que meu CPF cadastrado é `52998224725`, **quando** eu digitar `529.982.247-25`, **então** o sistema deve reconhecer como o mesmo login e permitir o acesso

**CA3 — Login do atendente por e-mail** — **Dado** que sou atendente com e-mail `recepcao@clinica.com` e senha `admin123`, **quando** eu digitar `Recepcao@Clinica.COM` e minha senha, **então** o sistema deve permitir o acesso, ignorando maiúsculas, e me levar ao painel do atendente

**CA4 — Primeiro acesso: vinculação por CPF** — **Dado** que o atendente me cadastrou no balcão com o CPF `529.982.247-25`, sem senha, **quando** eu acessar "Primeiro acesso" e digitar esse CPF, **então** o sistema deve constatar que o cadastro existe e não há login criado, **e** exibir `Encontramos seu cadastro, Carlos! Crie uma senha para ativar seu login.`, **e** ao salvar, criar o registro em `usuario` com `login = 52998224725` vinculado ao `paciente_id`

**CA5 — Auto-cadastro de paciente novo** _(resolve o conflito do enunciado — ADR-005)_ — **Dado** que meu CPF `123.456.789-09` não está cadastrado, **quando** eu acessar "Primeiro acesso", informar o CPF e preencher nome, telefone e senha, **então** o sistema deve criar o cadastro do paciente **e** a credencial no mesmo passo, **e** eu já poder solicitar consulta em seguida

**CA6 — CPF que já tem login** — **Dado** que meu CPF já possui login ativo, **quando** eu tentar o primeiro acesso, **então** o sistema deve informar isso e me direcionar para a tela de login

**CA7 — Credencial inválida** — **Quando** eu informar login inexistente ou senha errada, **então** o sistema deve responder `Login ou senha invalidos`, **e** a mensagem **não** deve revelar se o login existe

**CA8 — Proteção de rotas** — **Dado** que estou logado como paciente, **quando** eu tentar acessar uma rota de atendente, **então** o sistema deve responder **403**, **e** requisição sem token deve responder **401**

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `POST /api/auth/login` — recebe `login` (CPF ou e-mail) e senha;
  normaliza (só dígitos se não tiver `@`, lowercase se tiver); devolve JWT com `tipo_usuario` e
  `paciente_id`
- `[BACKEND]` `[OBRIGATÓRIO]` `GET /api/auth/verificar-cpf/{cpf}` — devolve
  `{cadastro_existe, login_ativo, nome}`
- `[BACKEND]` `[OBRIGATÓRIO]` `POST /api/auth/vincular-ou-criar` — ativa login existente **ou**
  faz o auto-cadastro completo
- `[BACKEND]` `[OBRIGATÓRIO]` Hash bcrypt (RN11) e expiração de token (RN13)
- `[BACKEND]` `[OBRIGATÓRIO]` `usuario_atual`, `exigir_paciente`, `exigir_atendente` (RN12)
- `[FRONTEND]` `[OBRIGATÓRIO]` Tela de login com campo único + máscara dinâmica de CPF
- `[FRONTEND]` `[OBRIGATÓRIO]` Tela de primeiro acesso em duas etapas (verifica CPF → formulário
  condicional)
- `[FRONTEND]` `[OBRIGATÓRIO]` Guarda de rota nos route groups `(paciente)` e `(atendente)`
- `[QA]` CT04, CT11, CT12

---

# Épico 1 — Cadastros base

## US-01 — Gestão de especialidades

> **Como** Atendente
> **Quero** gerenciar as especialidades médicas da clínica
> **Para** organizar o portfólio de atendimento

**Sprint 1 · P0**

### Critérios de aceite

**CA1** — **Dado** que preenchi o nome como `Cardiologia`, **quando** eu salvar, **então** a
especialidade deve ser criada e aparecer como opção nos formulários

**CA2** — **Dado** que `Cardiologia` já existe, **quando** eu tentar cadastrar de novo,
**então** o sistema deve informar que já está cadastrada

**CA3** — **Quando** o paciente consultar as especialidades, **então** deve ver apenas as
`ativo = true`

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `POST /api/especialidades`
- `[BACKEND]` `[OBRIGATÓRIO]` `GET /api/especialidades` (ativas)
- `[FRONTEND]` `[OBRIGATÓRIO]` Tela de cadastro e listagem

> Editar e excluir especialidade **não** fazem parte do MVP — ver MF03 em
> [`15-melhorias-futuras.md`](15-melhorias-futuras.md).

---

## US-02 — Gestão de médicos

> **Como** Atendente
> **Quero** gerenciar os médicos da clínica
> **Para** incluí-los na grade de atendimento

**Sprint 1 · P0 · Regras:** RN02, RN08

### Critérios de aceite

**CA1** — **Dado** que estou cadastrando o Dr. Silva, **quando** eu tentar salvar sem selecionar
especialidade, **então** o sistema deve impedir informando `Selecione uma especialidade`

**CA2 (RN02)** — **Dado** que `silva@email.com` já está cadastrado, **quando** eu tentar
cadastrar com esse e-mail, **então** o sistema deve recusar com `E-mail em uso`

**CA3** — **Dado** que o CRM `CRM12345` já existe, **quando** eu tentar cadastrar de novo,
**então** o sistema deve recusar informando `CRM ja cadastrado`

**CA4** — Médico desativado não aparece nas listagens do paciente, mas o histórico de consultas
dele permanece

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `POST /api/medicos` com validação de e-mail e CRM únicos
- `[FRONTEND]` `[OBRIGATÓRIO]` Formulário com `Select` de especialidade

> Editar e inativar médico **não** fazem parte do MVP — ver MF04 em
> [`15-melhorias-futuras.md`](15-melhorias-futuras.md).

---

## US-03 — Cadastro de pacientes

> **Como** Atendente
> **Quero** cadastrar novos pacientes no sistema
> **Para** viabilizar seus futuros agendamentos

**Sprint 1 · P0 · Regras:** RN01, RN02, RN07, RN08

### Critérios de aceite

**CA1** — **Quando** eu preencher nome, CPF válido e telefone, **então** o paciente deve ser
criado

**CA2 (RN01)** — **Dado** que o CPF `529.982.247-25` pertence ao paciente Carlos, **quando** eu
tentar cadastrar outro paciente com esse CPF, **então** o sistema deve exibir
`CPF ja cadastrado` **e** impedir o salvamento

**CA3 (RN02)** — **Dado** que `carlos@email.com` já está cadastrado e não é nulo, **quando** eu
tentar cadastrar outro paciente com esse e-mail, **então** o sistema deve impedir com
`E-mail em uso`

**CA4** — **Quando** eu deixar o e-mail em branco, **então** o cadastro deve ser aceito —
e-mail é opcional

**CA5** — **Dado** que existe paciente sem e-mail, **quando** eu cadastrar outro também sem
e-mail, **então** ambos devem coexistir (`NULL` não conta como duplicidade)

**CA6 (RN07)** — **Quando** eu informar `111.111.111-11`, **então** o sistema deve rejeitar com
`CPF invalido`

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `POST /api/pacientes` — salva em `paciente`, e-mail opcional.
  **Não cria credencial** — o login é ativado pelo fluxo de primeiro acesso da US-00
- `[FRONTEND]` `[OBRIGATÓRIO]` Formulário com máscara e validação de CPF

> Editar dados do paciente pelo atendente **não** faz parte do MVP — ver MF05 em
> [`15-melhorias-futuras.md`](15-melhorias-futuras.md). O paciente atualiza os próprios
> dados na US-04.
- `[QA]` CT01, CT02, CT03

---

## US-04 — Atualização cadastral pelo paciente

> **Como** Paciente
> **Quero** atualizar meus dados cadastrais
> **Para** manter meu perfil correto

**Sprint 2 · P2 · Regras:** RN02, RN08, RN12

### Critérios de aceite

**CA1** — **Quando** eu alterar telefone e salvar, **então** os dados devem ser atualizados

**CA2 (RN02)** — **Dado** que sou o paciente João com e-mail `joao@email.com` **e**
`maria@email.com` pertence à paciente Maria, **quando** eu tentar mudar meu e-mail para
`maria@email.com`, **então** o sistema deve exibir `E-mail em uso` **e** meus dados não devem
ser alterados

**CA3** — **Quando** eu salvar mantendo o meu próprio e-mail sem alteração, **então** não deve
haver erro de duplicidade

**CA4 (RN12)** — Só posso alterar **meus** dados. O paciente alvo é resolvido pelo
`paciente_id` do token, nunca por parâmetro da requisição

**CA5** — CPF **não** é editável pelo paciente

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `PUT /api/pacientes/me` usando o `paciente_id` do token
- `[FRONTEND]` `[OBRIGATÓRIO]` Tela de perfil com CPF em modo leitura

---

# Épico 2 — Agenda

## US-05 — Cadastro de agenda e horários disponíveis

> **Como** Atendente
> **Quero** cadastrar a grade horária de atendimento de um médico
> **Para** disponibilizar horários para agendamento

**Sprint 1 · P0 · Regras:** RN05, RN09

### Critérios de aceite

**CA1** — **Dado** que selecionei o Dr. Silva para `2026-08-10` **e** defini `09:00`, `10:00` e
`11:00`, **quando** eu salvar a grade, **então** os 3 horários devem ficar disponíveis na agenda
dele

**CA2 (RN05)** — **Dado** que o Dr. Silva já tem `14:00` em `2026-08-12`, **quando** eu tentar
cadastrar `14:00` nessa data de novo, **então** o sistema deve recusar
`Medico ja possui consulta agendada para este horario`

**CA3 (RN09)** — **Quando** eu tentar lançar `19:30`, **então** o sistema deve recusar informando
o intervalo `08:00-18:00`

**CA4** — **Quando** eu lançar a grade para um médico inexistente, **então** o sistema deve
responder **404**

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `POST /api/medicos/{id}/agenda` recebendo lista de horários
- `[BACKEND]` `[OBRIGATÓRIO]` `UniqueConstraint(medico_id, data, horario)` na migração
- `[FRONTEND]` `[OBRIGATÓRIO]` Painel com `DatePickerInput` + múltiplos `TimeInput`

> Excluir slot livre **não** faz parte do MVP — ver MF06 em
> [`15-melhorias-futuras.md`](15-melhorias-futuras.md).
- `[QA]` CT08, CT13

---

## US-06 — Consulta de médicos e especialidades

> **Como** Paciente
> **Quero** pesquisar os médicos e as especialidades da clínica
> **Para** encontrar o profissional correto

**Sprint 2 · P2**

### Critérios de aceite

**CA1** — **Dado** que existem `Dr. Silva (Cardiologia)` e `Dra. Souza (Pediatria)`, **quando**
eu filtrar por `Cardiologia`, **então** apenas o Dr. Silva deve aparecer

**CA2** — **Quando** eu não aplicar filtro, **então** todos os médicos ativos devem aparecer

**CA3** — Médicos e especialidades **inativos** não aparecem

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `GET /api/especialidades`
- `[BACKEND]` `[OBRIGATÓRIO]` `GET /api/medicos?especialidade_id=X`
- `[FRONTEND]` `[OBRIGATÓRIO]` Tela com filtro por especialidade

---

## US-07 — Visualização de horários disponíveis

> **Como** Paciente
> **Quero** ver os horários de consulta disponíveis de um médico
> **Para** escolher a melhor data para mim

**Sprint 2 · P1 · Regras:** RN03

### Critérios de aceite

**CA1 (RN03)** — **Dado** que o Dr. Silva tem `14:00` e `15:00` na agenda **e** `14:00` já foi
reservado, **quando** eu acessar a agenda dele, **então** apenas `15:00` deve aparecer como
disponível

**CA2** — **Dado** que a consulta das `14:00` foi cancelada, **quando** eu recarregar,
**então** `14:00` deve voltar a aparecer

**CA3** — **Quando** o médico não tiver agenda naquela data, **então** deve aparecer estado
vazio com mensagem clara, não erro

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `GET /api/medicos/{id}/horarios-livres?data=AAAA-MM-DD`
- `[FRONTEND]` `[OBRIGATÓRIO]` Calendário com horários livres e estado vazio

---

# Épico 3 — Consultas

## US-08 — Solicitação de consulta pelo paciente

> **Como** Paciente
> **Quero** escolher médico, data e horário disponível para solicitar uma consulta
> **Para** agendar meu atendimento

**Sprint 2 · P0 · Regras:** RN03, RN06

### Critérios de aceite

**CA1** — **Dado** que escolhi o Dr. Silva em `2026-08-10 às 15:00`, **quando** eu confirmar a
solicitação, **então** a consulta deve ser salva **e** o status definido como `SOLICITADA`

**CA2 (RN03 — concorrência)** — **Dado** que `15:00` estava livre, **quando** dois pacientes
confirmarem exatamente ao mesmo tempo, **então** o primeiro deve ter sucesso **e** o segundo
deve receber `Horario indisponivel`

**CA3** — **Quando** eu tentar agendar em horário já ocupado, **então** o sistema deve responder
**409**

**CA4** — Após o agendamento, o horário deixa de aparecer como livre

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `POST /api/consultas` com `paciente_id` vindo do token
- `[BACKEND]` `[OBRIGATÓRIO]` Reserva com `SELECT ... FOR UPDATE` (`buscar_para_reserva`)
- `[BACKEND]` `[OBRIGATÓRIO]` Índice parcial `uq_slot_ativo` na migração
- `[FRONTEND]` `[OBRIGATÓRIO]` Fluxo de confirmação com `modals.openConfirmModal`
- `[QA]` CT05 · `[QA]` EXP-03 com duas abas

---

## US-09 — Cadastro de consultas pelo atendente

> **Como** Atendente
> **Quero** cadastrar consultas diretamente para os pacientes
> **Para** preencher a agenda da clínica imediatamente

**Sprint 2 · P1 · Regras:** RN03, RN05, RN06

### Critérios de aceite

**CA1** — **Dado** que agendei uma consulta para o paciente José com o Dr. Silva, **quando** eu
concluir, **então** a consulta deve ser salva com status `CONFIRMADA` — diferente da US-08,
porque aqui é a própria clínica agendando

**CA2 (RN03)** — **Dado** que o Dr. Silva tem consulta em `2026-08-10 às 14:00`, **quando** eu
tentar agendar outra nesse horário, **então** o sistema deve exibir
`Medico ja possui consulta agendada para este horario` **e** o agendamento deve falhar

**CA3** — Só posso agendar em horário existente na grade do médico

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `POST /api/atendente/consultas` com `paciente_id` no corpo
- `[FRONTEND]` `[OBRIGATÓRIO]` Tela com busca de paciente + seleção de médico/horário
- `[QA]` CT05

---

## US-10 — Visualização de consultas e histórico

> **Como** Paciente
> **Quero** ver minhas consultas agendadas e passadas
> **Para** acompanhar meu histórico de atendimento

**Sprint 2 · P2 · Regras:** RN12

### Critérios de aceite

**CA1** — **Dado** que possuo consultas em `CONFIRMADA`, `CANCELADA` e `FINALIZADA`, **quando**
eu acessar minhas consultas, **então** todas devem aparecer identificadas com seus status

**CA2** — **Quando** eu abrir uma consulta, **então** devo ver médico, especialidade, data,
horário, status e, se cancelada, o motivo

**CA3 (RN12)** — Vejo apenas as **minhas** consultas. O `paciente_id` vem do token

**CA4** — **Quando** eu não tiver consulta alguma, **então** deve aparecer estado vazio com
convite para agendar

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `GET /api/consultas` filtrando pelo token
- `[FRONTEND]` `[OBRIGATÓRIO]` Lista com `Badge` por status (SOLICITADA amarelo, CONFIRMADA
  verde-água, FINALIZADA cinza, CANCELADA vermelho)

---

## US-11 — Cancelamento de consulta pelo paciente

> **Como** Paciente
> **Quero** cancelar uma consulta agendada
> **Para** liberar o horário

**Sprint 2 · P0 · Regras:** RN03, RN04, RN10, RN15

### Critérios de aceite

**CA1 (RN04 — bloqueio)** — **Dado** que minha consulta está marcada para `2026-08-10 14:00`
**e** agora é `2026-08-09 15:00` (faltam menos de 24h), **quando** eu tentar cancelar, **então**
o sistema deve exibir
`Cancelamento indisponivel. Prazo de antecedencia menor que 24 horas`
**e** a consulta deve permanecer com o status original

**CA2 (RN04 — permitido)** — **Dado** que minha consulta está marcada para `2026-08-12 14:00`
**e** agora é `2026-08-10 14:00` (faltam mais de 24h), **quando** eu solicitar o cancelamento,
**então** o sistema deve confirmar, alterar o status para `CANCELADA` (RN06) **e** o slot em
`horario_disponivel` deve voltar a `disponivel = true` (RN03)

**CA3 (RN10)** — **Quando** eu tentar cancelar consulta já `CANCELADA` ou `FINALIZADA`,
**então** o sistema deve recusar com **422**

**CA4 (RN15)** — O cálculo das 24h usa o fuso `America/Maceio`, independentemente do fuso da
máquina do servidor

**CA5** — Posso informar um motivo opcional, que fica registrado

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `PATCH /api/consultas/{id}/cancelar`
- `[BACKEND]` `[OBRIGATÓRIO]` `CancelamentoPorPaciente` (Strategy) com prazo de `settings`
- `[FRONTEND]` `[OBRIGATÓRIO]` Ação de cancelar com modal de confirmação e campo de motivo
- `[QA]` CT06, CT07 · `[QA]` EXP-03

---

## US-12 — Cancelamento de consultas pelo atendente

> **Como** Atendente
> **Quero** cancelar consultas registradas
> **Para** manter a agenda atualizada em caso de imprevistos

**Sprint 2 · P1 · Regras:** RN03, RN10

### Critérios de aceite

**CA1** — **Dado** que a consulta do paciente José é daqui a 2 horas **e** estou logado como
atendente, **quando** eu comandar o cancelamento, **então** o sistema deve permitir (ignorando
a restrição das 24h), alterar o status para `CANCELADA` (RN06) **e** liberar o slot (RN03)

**CA2 (RN10)** — Consulta `FINALIZADA` não pode ser cancelada, nem pelo atendente

**CA3** — O motivo do cancelamento é registrado e visível para o paciente

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `PATCH /api/atendente/consultas/{id}/cancelar`
- `[BACKEND]` `[OBRIGATÓRIO]` `CancelamentoPorAtendente` (Strategy, sem validação de prazo)
- `[FRONTEND]` `[OBRIGATÓRIO]` Ação de cancelamento administrativo
- `[QA]` EXP-03

---

## US-13 — Confirmação e finalização de consultas

> **Como** Atendente
> **Quero** confirmar consultas solicitadas e finalizar as realizadas
> **Para** que o status da agenda reflita a realidade da clínica

**Sprint 2 · P1 · Regras:** RN06, RN10 · **Origem:** conflito C04

> **Por que esta US existe:** sem ela, uma consulta solicitada pelo paciente (US-08) ficaria
> eternamente `SOLICITADA`, e o status `FINALIZADA` da RN06 seria código morto. A RN06 não
> estaria demonstrável.

### Critérios de aceite

**CA1** — **Dado** que existe consulta `SOLICITADA`, **quando** eu confirmar, **então** o status
deve ir para `CONFIRMADA`

**CA2** — **Dado** que existe consulta `CONFIRMADA`, **quando** eu finalizar, **então** o status
deve ir para `FINALIZADA`

**CA3 (RN10)** — **Quando** eu tentar ir de `SOLICITADA` direto para `FINALIZADA`, **então** o
sistema deve recusar com `Nao e permitido ir de SOLICITADA para FINALIZADA`

**CA4 (RN10)** — `CANCELADA` e `FINALIZADA` são terminais: nenhuma transição sai delas

**CA5** — A lista de consultas do atendente permite filtrar por status para achar as pendentes
de confirmação

### Tarefas

- `[BACKEND]` `[OBRIGATÓRIO]` `PATCH /api/atendente/consultas/{id}/status`
- `[BACKEND]` `[OBRIGATÓRIO]` Validação por `TRANSICOES_PERMITIDAS`
- `[FRONTEND]` `[OBRIGATÓRIO]` Ações de confirmar e finalizar na lista do atendente
- `[QA]` CT09, CT10

---

## Resumo

| US    | Título                               | Sprint | Prior. | Regras                      |
| ----- | ------------------------------------ | ------ | ------ | --------------------------- |
| US-00 | Autenticação e vinculação por CPF    | 1      | P0     | RN01, RN02, RN07, RN11–RN13 |
| US-01 | Gestão de especialidades             | 1      | P0     | —                           |
| US-02 | Gestão de médicos                    | 1      | P0     | RN02, RN08                  |
| US-03 | Cadastro de pacientes                | 1      | P0     | RN01, RN02, RN07, RN08      |
| US-05 | Agenda e horários disponíveis        | 1      | P0     | RN05, RN09                  |
| US-04 | Atualização cadastral                | 2      | P2     | RN02, RN08, RN12            |
| US-06 | Consulta de médicos e especialidades | 2      | P2     | —                           |
| US-07 | Horários disponíveis                 | 2      | P1     | RN03                        |
| US-08 | Solicitação de consulta              | 2      | P0     | RN03, RN06                  |
| US-09 | Cadastro de consultas (atendente)    | 2      | P1     | RN03, RN05, RN06            |
| US-10 | Consultas e histórico                | 2      | P2     | RN12                        |
| US-11 | Cancelamento (paciente)              | 2      | P0     | RN03, RN04, RN10, RN15      |
| US-12 | Cancelamento (atendente)             | 2      | P1     | RN03, RN10                  |
| US-13 | Confirmar e finalizar                | 2      | P1     | RN06, RN10                  |
