# Casos de teste

14 casos funcionais (o enunciado exige 10) + 11 casos unitários mapeados.
Estratégia e critérios em [07-plano-de-testes.md](Plano-de-Testes).

**Ambiente padrão:** `make bootstrap` · atendente `recepcao@clinica.com` / `admin123`
**Evidências:** `docs/evidencias/<CT-ID>/`

---

## 1. Dados de teste

CPFs válidos (dígitos verificadores corretos — exigência da RN07):

| Apelido | CPF | Uso |
|---|---|---|
| CPF-A | `529.982.247-25` | Paciente Carlos (primeiro cadastro) |
| CPF-B | `111.444.777-35` | Paciente Maria |
| CPF-C | `123.456.789-09` | Paciente João (auto-cadastro) |
| CPF-INVÁLIDO | `111.111.111-11` | Deve ser rejeitado |

---

## 2. Casos de teste funcionais

### CT01 — Cadastrar paciente com dados válidos

| | |
|---|---|
| **Perfil** | Atendente · **US:** US-03 · **RN:** RN07, RN08 · **Prioridade:** Alta |
| **Pré-condição** | Logado como atendente. CPF-A não cadastrado. |

**Passos**

1. Acessar *Pacientes → Novo paciente*
2. Preencher: nome `Carlos Souza`, CPF `529.982.247-25`, telefone `82999990000`, e-mail `carlos@email.com`
3. Salvar
4. Tentar cadastrar outro paciente com CPF `111.111.111-11`

**Esperado**

- Passo 3: paciente criado, notificação de sucesso, aparece na listagem
- Passo 4: bloqueado com "CPF invalido" antes de enviar ao servidor (RN07)

---

### CT02 — Bloquear cadastro com CPF duplicado (RN01)

| | |
|---|---|
| **Perfil** | Atendente · **US:** US-03 · **RN:** RN01 · **Prioridade:** Alta |
| **Pré-condição** | CT01 executado (CPF-A já cadastrado) |

**Passos**

1. Acessar *Pacientes → Novo paciente*
2. Preencher nome `Carlos Duplicado`, CPF `529.982.247-25`, telefone `82988887777`, e-mail `outro@email.com`
3. Salvar

**Esperado** — HTTP **409**, mensagem `CPF ja cadastrado`, nenhum registro novo criado.
A listagem continua com um único Carlos.

---

### CT03 — Bloquear e-mail duplicado e permitir e-mail nulo (RN02)

| | |
|---|---|
| **Perfil** | Atendente · **US:** US-03 · **RN:** RN02, RN08 · **Prioridade:** Alta |
| **Pré-condição** | `carlos@email.com` já cadastrado |

**Passos**

1. Cadastrar paciente com CPF-B e e-mail `carlos@email.com` → salvar
2. Cadastrar paciente com CPF-B e e-mail `carlos@` → salvar
3. Cadastrar paciente com CPF-B, **deixando o e-mail vazio** → salvar
4. Cadastrar paciente com CPF-C, **também sem e-mail** → salvar

**Esperado**

- Passo 1: **409** `E-mail em uso`
- Passo 2: bloqueado no formulário, `E-mail invalido` (RN08)
- Passo 3: **criado** — e-mail é opcional
- Passo 4: **criado** — dois pacientes sem e-mail não colidem, porque `NULL` não conta como
  duplicidade em `UNIQUE`

> Passo 4 é o caso que pega implementação ingênua da RN02.

---

### CT04 — Primeiro acesso: ativar login de paciente cadastrado no balcão

| | |
|---|---|
| **Perfil** | Paciente · **US:** US-00 · **RN:** RN11 · **Prioridade:** Alta |
| **Pré-condição** | CPF-A cadastrado pelo atendente, sem login ativo |

**Passos**

1. Sair da sessão do atendente
2. Acessar *Primeiro acesso* e informar `529.982.247-25`
3. Observar a resposta do sistema
4. Definir senha `senha123` e confirmar
5. Sair e fazer login com `52998224725` / `senha123`
6. Repetir o passo 2 com o mesmo CPF

**Esperado**

- Passo 3: `Encontramos seu cadastro, Carlos! Crie uma senha para ativar seu login.`
- Passo 4: login criado, redireciona ao painel do paciente
- Passo 5: login aceito **sem máscara** no CPF (normalização)
- Passo 6: informa que o CPF já tem login ativo e direciona ao login
- Em nenhum momento a senha aparece em texto claro na resposta da API (RN11 — conferir
  DevTools → Network)

---

### CT05 — Bloquear agendamento em horário já ocupado (RN03)

| | |
|---|---|
| **Perfil** | Atendente + Paciente · **US:** US-05, US-08, US-09 · **RN:** RN03 · **Prioridade:** Alta |
| **Pré-condição** | Especialidade e médico `Dr. Silva` cadastrados |

**Passos**

1. Como atendente, lançar agenda do Dr. Silva para `2026-08-12` com `14:00` e `15:00`
2. Como atendente, agendar Carlos com Dr. Silva às `14:00` → confirmar
3. Como paciente Carlos, acessar os horários livres do Dr. Silva em `2026-08-12`
4. Como atendente, tentar agendar Maria com Dr. Silva às `14:00`

**Esperado**

- Passo 2: consulta criada com status **CONFIRMADA** (agendada pelo atendente)
- Passo 3: **somente `15:00`** aparece na lista
- Passo 4: **409** `Horario indisponivel`

---

### CT06 — Paciente cancela com mais de 24h de antecedência (RN04)

| | |
|---|---|
| **Perfil** | Paciente · **US:** US-11 · **RN:** RN04, RN15, RN03 · **Prioridade:** Alta |
| **Pré-condição** | Carlos com consulta em data ≥ 48h à frente |

**Passos**

1. Logar como Carlos
2. Acessar *Minhas consultas* e abrir a consulta
3. Cancelar, informando motivo `Imprevisto`
4. Como atendente, consultar os horários livres daquele médico e data

**Esperado**

- Passo 3: cancelamento aceito, status muda para **CANCELADA**, motivo registrado
- Passo 4: o horário **volta a aparecer como livre** (RN03) — e pode ser reagendado

---

### CT07 — Bloquear cancelamento do paciente com menos de 24h (RN04)

| | |
|---|---|
| **Perfil** | Paciente · **US:** US-11 · **RN:** RN04, RN15 · **Prioridade:** Alta |
| **Pré-condição** | Carlos com consulta em ~12h. Ver nota abaixo. |

**Passos**

1. Logar como Carlos
2. Acessar a consulta e tentar cancelar

**Esperado** — **422** `Cancelamento indisponivel. Prazo de antecedencia menor que 24 horas`.
Status permanece o original.

> **Nota de execução:** para montar a pré-condição sem esperar, lance a agenda para
> hoje/amanhã de forma que faltem ~12h, ou reduza `CANCELAMENTO_ANTECEDENCIA_HORAS` no `.env`
> e ajuste o cenário. **Registre no relatório qual método usou.** O cálculo usa o fuso
> `America/Maceio` (RN15) — validar em máquina com outro fuso é um bom teste extra.

---

### CT08 — Bloquear alocação dupla do mesmo médico (RN05)

| | |
|---|---|
| **Perfil** | Atendente · **US:** US-05 · **RN:** RN05 · **Prioridade:** Alta |
| **Pré-condição** | Dr. Silva com `14:00` cadastrado em `2026-08-12` |

**Passos**

1. Lançar agenda do Dr. Silva para `2026-08-12` incluindo `14:00`
2. Lançar agenda do Dr. Silva para `2026-08-12` com `14:00` e `16:00`

**Esperado** — **409** `Medico ja possui consulta agendada para este horario`. Nenhum slot
duplicado é criado.

> Verificar no banco: `SELECT medico_id, data, horario, COUNT(*) FROM horario_disponivel
> GROUP BY 1,2,3 HAVING COUNT(*) > 1;` deve retornar vazio.

---

### CT09 — Ciclo de vida do status da consulta (RN06)

| | |
|---|---|
| **Perfil** | Paciente + Atendente · **US:** US-08, US-13 · **RN:** RN06, RN10 · **Prioridade:** Alta |
| **Pré-condição** | Horário livre do Dr. Silva |

**Passos**

1. Como paciente, solicitar consulta em horário livre
2. Verificar o status exibido
3. Como atendente, confirmar a consulta
4. Como atendente, finalizar a consulta
5. Como atendente, tentar cancelar a consulta finalizada

**Esperado**

- Passo 2: **SOLICITADA** (paciente solicitou — diferente do CT05, em que o atendente agendou)
- Passo 3: **CONFIRMADA**
- Passo 4: **FINALIZADA**
- Passo 5: **422** `Nao e permitido ir de FINALIZADA para CANCELADA` (RN10 — estado terminal)

---

### CT10 — Reagendar horário liberado por cancelamento (RN03 + RN10)

| | |
|---|---|
| **Perfil** | Atendente · **US:** US-08, US-11 · **RN:** RN03, RN10 · **Prioridade:** Alta |
| **Pré-condição** | CT06 executado — existe consulta CANCELADA num slot |

**Passos**

1. Como atendente, listar horários livres do médico naquela data
2. Agendar Maria no **mesmo horário** que foi cancelado no CT06
3. Verificar o banco

**Esperado**

- Passo 1: o horário aparece livre
- Passo 2: agendamento **aceito**, status CONFIRMADA
- Passo 3: existem duas linhas em `consulta` para o mesmo `horario_disponivel_id` — uma
  CANCELADA, uma CONFIRMADA — **sem violar** o índice `uq_slot_ativo`

> Este é o caso que prova que a decisão do ADR-006 (índice parcial em vez de `UNIQUE` simples)
> está correta. Com `UNIQUE` comum, o passo 2 falharia.

---

### CT11 — Paciente não acessa rota de atendente (RN12)

| | |
|---|---|
| **Perfil** | Paciente · **US:** US-00 · **RN:** RN12 · **Prioridade:** Alta |
| **Pré-condição** | Logado como Carlos (PACIENTE) |

**Passos**

1. Acessar diretamente pela URL uma tela de atendente (ex.: `/pacientes`)
2. Com o token de paciente, chamar `POST /api/pacientes` via Swagger ou `curl`
3. Chamar `GET /api/consultas` passando o `paciente_id` de **outro** paciente no lugar do seu

**Esperado**

- Passo 1: redirecionado, sem acesso à tela
- Passo 2: **403** `Acesso restrito ao perfil ATENDENTE`
- Passo 3: retorna apenas as consultas **do próprio** Carlos — o `paciente_id` vem do token,
  não do parâmetro

---

### CT12 — Requisição sem token e com token inválido (RN12, RN13)

| | |
|---|---|
| **Perfil** | Não autenticado · **US:** US-00 · **RN:** RN12, RN13 · **Prioridade:** Alta |
| **Pré-condição** | Nenhuma |

**Passos**

1. `curl http://localhost:8000/api/consultas` (sem header)
2. Mesma chamada com `Authorization: Bearer token-invalido`
3. Editar o token no armazenamento do navegador, corrompendo-o, e recarregar
4. Tentar login com senha errada

**Esperado**

- Passos 1–3: **401** `Nao autenticado`, com header `WWW-Authenticate: Bearer`
- Passo 4: **401** `Login ou senha invalidos` — a mensagem **não** revela se o login existe

---

### CT13 — Bloquear horário fora do funcionamento (RN09)

| | |
|---|---|
| **Perfil** | Atendente · **US:** US-05 · **RN:** RN09 · **Prioridade:** Média |
| **Pré-condição** | Dr. Silva cadastrado |

**Passos**

1. Lançar agenda com `07:59`
2. Lançar agenda com `08:00`
3. Lançar agenda com `17:59`
4. Lançar agenda com `18:00`
5. Lançar agenda com `19:30`

**Esperado**

- Passos 1, 4 e 5: **422**, mensagem informando o intervalo `08:00-18:00`
- Passos 2 e 3: aceitos

> `18:00` é rejeitado porque a validação é `08:00 <= h < 18:00` — a última consulta começa
> às 17:59. Se a clínica quiser incluir 18:00, é mudança em `HORA_FECHAMENTO`.

---

### CT14 — Não existe caminho público para virar atendente (RN14)

| | |
|---|---|
| **Perfil** | Sistema · **US:** US-00 · **RN:** RN14, RN12 · **Prioridade:** Alta |
| **Pré-condição** | Sistema no ar; seed executado; um paciente cadastrado |

> **Nota de escopo.** A *tela* de cadastro de atendente saiu do MVP
> ([ADR-008](ADR-008-Rebaseline-de-Escopo), MF02). A **RN14 continua valendo** e este caso
> passou a testá-la pelo lado que importa: provar que **não existe** forma de um não-atendente
> obter esse perfil.

**Passos**

1. Abrir `http://localhost:8000/docs` e procurar por qualquer rota pública que crie usuário
   com perfil `ATENDENTE`
2. Sem token, chamar `POST /api/auth/vincular-ou-criar` tentando forçar
   `{"tipo_usuario": "ATENDENTE"}` no corpo
3. Logado como **paciente**, chamar qualquer rota sob `/api/atendente/*`
4. Sem token, chamar qualquer rota sob `/api/atendente/*`
5. Rodar `docker compose exec backend python -m app.seeds.seed` uma segunda vez

**Esperado**

- Passo 1: **nenhuma** rota pública cria atendente. As únicas rotas públicas são `login`,
  `verificar-cpf` e `vincular-ou-criar`
- Passo 2: o campo é ignorado — o usuário nasce `PACIENTE`. O schema de entrada não expõe
  `tipo_usuario`
- Passo 3: **403**
- Passo 4: **401**
- Passo 5: seed idempotente — nenhum atendente duplicado ([ADR-004](ADR-004-Bootstrap-do-Atendente))

---

## 3. Casos de teste unitários (automatizados)

Duas suítes independentes, uma por aplicação. Ambas rodam no CI a cada push.

| Stack | Pasta | Ferramenta | Comando | Mínimo exigido | Hoje |
|---|---|---|---|---|---|
| Backend | `backend/tests/unit/` | pytest + fakes de repositório | `make test-backend` | 5 | **73** |
| Frontend | `frontend/__tests__/` | Vitest + Testing Library | `make test-frontend` | 5 | **109** |

Os testes de backend rodam **sem banco** — é o que o padrão Repository torna possível
([`06-design-patterns.md`](Design-Patterns)). Os de frontend usam o `render` de
`@test-utils`, que já traz o `MantineProvider`.

| ID | Arquivo | Teste | RN |
|---|---|---|---|
| CTU01 | `test_paciente_service.py` | `test_ctu01_deve_bloquear_cadastro_com_cpf_duplicado` | RN01 |
| CTU02 | `test_paciente_service.py` | `test_ctu02_deve_bloquear_cadastro_com_email_duplicado` | RN02 |
| CTU02b | `test_paciente_service.py` | `test_email_nulo_nao_colide_com_outro_email_nulo` | RN02 |
| CTU03 | `test_consulta_service.py` | `test_ctu03_deve_bloquear_agendamento_em_horario_ja_ocupado` | RN03 |
| CTU04 | `test_consulta_service.py` | `test_ctu04_deve_bloquear_cancelamento_do_paciente_com_menos_de_24h` | RN04, RN15 |
| CTU04b | `test_consulta_service.py` | `test_paciente_pode_cancelar_com_mais_de_24h_e_slot_e_liberado` | RN04, RN03 |
| CTU04c | `test_consulta_service.py` | `test_atendente_cancela_ignorando_a_regra_de_24h` | US-12 |
| CTU05 | `test_agenda_service.py` | `test_ctu05_deve_bloquear_slot_duplicado_para_o_mesmo_medico` | RN05 |
| CTU06 | `test_consulta_service.py` | `test_status_inicial_depende_de_quem_agenda` | RN06 |
| CTU09 | `test_consulta_service.py` | `test_nao_permite_cancelar_consulta_ja_finalizada` | RN10 |
| CTU10 | `test_auth_service.py` | `test_paciente_loga_com_cpf_formatado` | RN11 |
| CTU10b | `test_auth_service.py` | `test_atendente_loga_com_email_case_insensitive` | RN11 |
| CTU10c | `test_auth_service.py` | `test_primeiro_acesso_ativa_login_de_paciente_cadastrado_pelo_atendente` | US-00 |
| CTU10d | `test_auth_service.py` | `test_auto_cadastro_cria_paciente_e_credencial_no_mesmo_fluxo` | ADR-005 |
| CTU12 | `test_consulta_service.py` | `test_rn16_nao_agenda_com_medico_inativado` | RN16 |
| CTU12b | `test_agenda_service.py` | `test_rn16_medico_inativado_nao_oferece_horario` | RN16 |
| CTU13 | `test_consulta_service.py` | `test_ctu13_rn17_nao_agenda_com_medico_de_especialidade_inativada` | RN17 |
| CTU13b | `test_agenda_service.py` | `test_rn17_medico_de_especialidade_inativada_nao_oferece_horario` | RN17 |
| CTU13c | `test_medico_service.py` | `test_rn17_medico_de_especialidade_inativada_sai_da_lista_agendavel` | RN17 |
| CTU13d | `test_especialidade_service.py` | `test_rn17_inativar_especialidade_nao_cascateia_nos_medicos` | RN17 |
| CTU07 | `__tests__/cpf.test.ts` | `aceita CPF valido` / `rejeita digito verificador errado` | RN07 |
| CTU11 | `test_api_smoke.py` | `test_rota_protegida_rejeita_sem_token` | RN12 |

Execução:

```bash
make test-backend      # pytest --cov
make test-frontend     # vitest
```

---

## 4. Relatório de execução (preencher a cada sprint)

| CT | Sprint | Executor | Data | Resultado | Bug | Evidência |
|---|---|---|---|---|---|---|
| CT01 | 1 | | | ⬜ | | `evidencias/CT01/` |
| CT02 | 1 | | | ⬜ | | `evidencias/CT02/` |
| CT03 | 1 | | | ⬜ | | `evidencias/CT03/` |
| CT04 | 1 | | | ⬜ | | `evidencias/CT04/` |
| CT08 | 1 | | | ⬜ | | `evidencias/CT08/` |
| CT13 | 1 | | | ⬜ | | `evidencias/CT13/` |
| CT14 | 1 | | | ⬜ | | `evidencias/CT14/` |
| CT05 | 2 | | | ⬜ | | `evidencias/CT05/` |
| CT06 | 2 | | | ⬜ | | `evidencias/CT06/` |
| CT07 | 2 | | | ⬜ | | `evidencias/CT07/` |
| CT09 | 2 | | | ⬜ | | `evidencias/CT09/` |
| CT10 | 2 | | | ⬜ | | `evidencias/CT10/` |
| CT11 | 2 | | | ⬜ | | `evidencias/CT11/` |
| CT12 | 2 | | | ⬜ | | `evidencias/CT12/` |

Legenda: ⬜ não executado · ✅ passou · ❌ falhou · ⚠️ passou com observação


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
