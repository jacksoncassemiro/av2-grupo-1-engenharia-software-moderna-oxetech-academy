# Requisitos do sistema

Lista canônica. Qualquer código, teste ou caso de teste referencia os IDs daqui.
Divergências entre as fontes do enunciado estão analisadas em
[14-conflitos-e-decisoes.md](Conflitos-e-Decisoes).

---

## 1. Requisitos funcionais

| ID | Requisito | Perfil | US | Prioridade |
|---|---|---|---|---|
| RF01 | Autenticar com campo único "CPF ou E-mail" e devolver token JWT | Todos | US-00 | Alta |
| RF02 | Verificar se um CPF já tem cadastro e/ou login ativo | Público | US-00 | Alta |
| RF03 | Ativar o login de paciente já cadastrado (primeiro acesso por CPF) | Paciente | US-00 | Alta |
| RF04 | Permitir que um paciente sem cadastro se auto-cadastre e já obtenha login | Paciente | US-00 | Alta |
| RF05 | Restringir rotas e telas conforme o perfil do usuário autenticado | Sistema | US-00 | Alta |
| RF06 | Cadastrar especialidades médicas | Atendente | US-01 | Alta |
| RF07 | Listar especialidades ativas | Todos | US-06 | Média |
| RF08 | Cadastrar médicos com nome, e-mail, CRM e especialidade | Atendente | US-02 | Alta |
| RF09 | Listar médicos ativos, com filtro por especialidade | Todos | US-06 | Média |
| RF10 | Cadastrar pacientes (e-mail opcional) | Atendente | US-03 | Alta |
| RF11 | Permitir que o paciente atualize seus próprios dados | Paciente | US-04 | Média |
| RF12 | Cadastrar a grade de horários disponíveis de um médico | Atendente | US-05 | Alta |
| RF13 | Listar horários livres de um médico numa data | Todos | US-07 | Alta |
| RF14 | Permitir que o paciente solicite uma consulta em horário livre | Paciente | US-08 | Alta |
| RF15 | Permitir que o atendente agende consulta para um paciente | Atendente | US-09 | Alta |
| RF16 | Listar as consultas e o histórico do paciente autenticado | Paciente | US-10 | Média |
| RF17 | Exibir os detalhes de uma consulta específica | Paciente | US-10 | Média |
| RF18 | Permitir que o paciente cancele consulta respeitando a antecedência | Paciente | US-11 | Alta |
| RF19 | Permitir que o atendente cancele consulta sem restrição de prazo | Atendente | US-12 | Alta |
| RF20 | Liberar o horário na agenda quando a consulta é cancelada | Sistema | US-11/12 | Alta |
| RF21 | Permitir que o atendente confirme e finalize consultas | Atendente | US-13 | Alta |
| RF22 | Exibir a agenda geral consolidada da clínica | Atendente | US-14 | Desejável |
| RF23 | Permitir que um atendente cadastre outro atendente | Atendente | US-15 | Alta |
| RF24 | Rejeitar requisição sem token (401) ou com perfil inadequado (403) | Sistema | US-00 | Alta |

---

## 2. Requisitos não funcionais

| ID | Requisito | Categoria | Como é verificado |
|---|---|---|---|
| RNF01 | Arquitetura em camadas com separação MVC | Arquitetura | `docs/03-arquitetura.md` + revisão de PR |
| RNF02 | Aplicar ao menos 3 práticas de Clean Code e princípios SOLID | Manutenibilidade | `docs/05-clean-code.md` |
| RNF03 | Implementar ao menos 2 Design Patterns | Arquitetura | `docs/06-design-patterns.md` |
| RNF04 | Versionamento com Git Flow e Conventional Commits | Processo | `docs/10-git-flow.md` |
| RNF05 | Pipeline de CI automatizado no GitHub Actions | DevOps | `.github/workflows/ci.yml` |
| RNF06 | Mínimo de 5 testes unitários automatizados | Qualidade | `backend/tests/unit/` (20 entregues) |
| RNF07 | Subir em qualquer máquina com um comando | Portabilidade | `make bootstrap` + job `docker` do CI |
| RNF08 | Dois perfis de acesso com permissões distintas | Segurança | `core/deps.py` + CT11/CT12 |
| RNF09 | Validar dados de entrada antes de persistir | Segurança | Schemas Pydantic + `@mantine/form` |
| RNF10 | Banco de dados relacional com integridade referencial | Persistência | PostgreSQL 16 + FKs + constraints |
| RNF11 | Senha nunca armazenada nem transmitida em texto claro | Segurança | bcrypt via `passlib` |
| RNF12 | Esquema do banco versionado em migrações | Manutenibilidade | Alembic |
| RNF13 | API autodocumentada | Documentação | Swagger em `/docs`, ReDoc em `/redoc` |
| RNF14 | Resposta de leitura em até 3 s em condição normal | Performance | Verificação manual na Sprint Review |
| RNF15 | Interface acessível por teclado e com contraste adequado | Acessibilidade | Componentes Mantine (acessíveis por padrão) |

---

## 3. Regras de negócio

### 3.1 Obrigatórias do enunciado

| ID | Regra | Onde é aplicada | Teste |
|---|---|---|---|
| **RN01** | Bloquear cadastro de paciente com CPF já existente | `UNIQUE paciente.cpf` + `PacienteService._garantir_cpf_inedito` | CTU01, CT02 |
| **RN02** | Bloquear usuário duplicado com o mesmo e-mail | `UNIQUE` em `paciente.email`, `medico.email`, `usuario.login` + validação no service | CTU02, CT03 |
| **RN03** | Impedir reserva de horário já ocupado | `disponivel` + índice parcial `uq_slot_ativo` + `SELECT FOR UPDATE` | CTU03, CT05 |
| **RN04** | Cancelamento pelo paciente só com ≥ 24h de antecedência | `CancelamentoPorPaciente` (Strategy) | CTU04, CT06, CT07 |
| **RN05** | Bloquear alocação dupla do mesmo médico no mesmo horário | `UniqueConstraint(medico_id, data, horario)` + `AgendaService._criar_slot` | CTU05, CT08 |
| **RN06** | Gerir os status SOLICITADA, CONFIRMADA, CANCELADA, FINALIZADA | Enum `StatusConsulta` + `ConsultaService.mudar_status` | CT09 |

### 3.2 Adicionais definidas pela equipe

| ID | Regra | Motivo | Onde é aplicada |
|---|---|---|---|
| **RN07** | CPF deve ser válido pelos dígitos verificadores | Sem isso a RN01 aceita `00000000000` | `PacienteCriar` (Pydantic) + `src/lib/cpf.ts` |
| **RN08** | E-mail deve ter formato válido | Complementa a RN02 | `EmailStr` + `@mantine/form` |
| **RN09** | Horário de atendimento restrito a 08:00–18:00 | Realismo do domínio | `GradeHorariaCriar` |
| **RN10** | Status só transita para frente; CANCELADA e FINALIZADA são terminais | Torna a RN06 verificável | `TRANSICOES_PERMITIDAS` |
| **RN11** | Senha armazenada com hash bcrypt, nunca em texto claro | Segurança | `core/security.py` |
| **RN12** | Cada rota exige o perfil correto, extraído do JWT | RNF08 | `core/deps.py` |
| **RN13** | Token JWT expira (24h no MVP, configurável) | Segurança | `JWT_EXPIRE_MINUTES` |
| **RN14** | Apenas ATENDENTE cria ATENDENTE; não há rota pública para isso | Evita escalonamento de privilégio | `exigir_atendente` + seed |
| **RN15** | Regras temporais avaliadas em `America/Maceio` | Evita erro de 3h em UTC | `settings.TIMEZONE` |

### 3.3 Detalhamento das regras sensíveis

**RN02 — e-mail único com valor nulo permitido.**
`paciente.email` é *nullable* porque paciente de balcão pode não ter e-mail. Em PostgreSQL,
`UNIQUE` permite múltiplos `NULL` — o que é o comportamento desejado. A validação do service
retorna imediatamente quando o e-mail é `None`, sem consultar o banco.

**RN03 — por que índice parcial e não `UNIQUE` simples.**
Um `UNIQUE` comum em `consulta.horario_disponivel_id` tornaria o slot inutilizável para
sempre depois do primeiro cancelamento, porque a linha CANCELADA continuaria no índice.
O índice parcial (`WHERE status IN ('SOLICITADA','CONFIRMADA')`) libera o slot.
Análise completa em [14-conflitos-e-decisoes.md](Conflitos-e-Decisoes) §C03.

**RN04 — referência de tempo.**
A antecedência é medida entre "agora" e `horario_disponivel.data + horario`, ambos no fuso
da RN15. O valor 24 vem de `settings.CANCELAMENTO_ANTECEDENCIA_HORAS` — nunca hardcoded.
Para demonstrar o cancelamento sem esperar, basta baixar essa variável no `.env`.

**RN06/RN10 — máquina de estados.**

```
                 ┌──────────────────┐
   agendado ────▶│    SOLICITADA    │  (paciente solicitou — US-08)
   pelo          └────────┬─────────┘
   paciente               │ atendente confirma (US-13)
                          ▼
   agendado ────▶┌──────────────────┐
   pelo          │    CONFIRMADA    │  (US-09 nasce aqui)
   atendente     └────────┬─────────┘
                          │ consulta realizada (US-13)
                          ▼
                 ┌──────────────────┐
                 │    FINALIZADA    │  ← terminal
                 └──────────────────┘

   SOLICITADA ou CONFIRMADA ──▶ CANCELADA (US-11 com RN04 / US-12 sem restrição) ← terminal
```

Transição fora deste grafo levanta `TransicaoDeStatusInvalida` (HTTP 422).

---

## 4. Matriz de rastreabilidade

| RN | RF | US | Constraint de banco | Teste unitário | Caso de teste |
|---|---|---|---|---|---|
| RN01 | RF10 | US-03 | `UNIQUE paciente.cpf` | CTU01 | CT02 |
| RN02 | RF08, RF10, RF11 | US-02, US-03, US-04 | `UNIQUE` em e-mail/login | CTU02 | CT03 |
| RN03 | RF13, RF14, RF20 | US-07, US-08, US-11 | `uq_slot_ativo` (parcial) | CTU03 | CT05 |
| RN04 | RF18 | US-11 | — (regra de aplicação) | CTU04 | CT06, CT07 |
| RN05 | RF12 | US-05 | `uq_medico_data_horario` | CTU05 | CT08 |
| RN06 | RF21 | US-13 | `Enum status_consulta` | CTU06 | CT09 |
| RN07 | RF10 | US-03 | — | CTU07 | CT01 |
| RN08 | RF08, RF10 | US-02, US-03 | — | — | CT03 |
| RN09 | RF12 | US-05 | — | CTU08 | CT13 |
| RN10 | RF21 | US-13 | — | CTU09 | CT09, CT10 |
| RN11 | RF01 | US-00 | — | CTU10 | CT04 |
| RN12 | RF05, RF24 | US-00 | — | CTU11 | CT11, CT12 |
| RN13 | RF01 | US-00 | — | — | CT12 |
| RN14 | RF23 | US-15 | — | — | CT14 |
| RN15 | RF18 | US-11 | `TIMESTAMPTZ` | CTU04 | CT06 |


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
