# Plano de testes

Entregável de QA. Base: *Módulo 5 — Qualidade, Testes e Segurança* (pirâmide de testes,
cobertura, quality gates).

---

## 1. Objetivo

Garantir que o MVP atende aos requisitos funcionais (RF01–RF24) e não funcionais (RNF01–RNF15),
com foco em **provar que as regras de negócio RN01–RN15 são efetivamente aplicadas** — inclusive
quando alguém tenta violá-las.

Critério norteador: **toda regra de negócio tem ao menos um teste que a viola e espera bloqueio.**
Teste que só verifica o caminho felizes não prova que a regra existe.

---

## 2. Escopo

| Dentro do escopo | Fora do escopo | Por quê |
|---|---|---|
| RF01–RF24 nos perfis Paciente e Atendente | Teste de carga e estresse | Sem requisito de volume no MVP |
| RN01–RN15, com casos positivos e negativos | Pentest / análise de vulnerabilidade | Fora do prazo e do escopo da AV2 |
| Autorização por perfil (401/403) | Compatibilidade cross-browser exaustiva | Testamos em Chrome/Edge, os alvos |
| Validação de formulários (front e back) | Teste de responsividade em todos os breakpoints | Verificação visual em desktop e mobile |
| Concorrência na reserva de horário | Recuperação de desastre / backup | Não há operação em produção |
| Migrações Alembic e idempotência do seed | Integração com sistemas externos | Não existe integração no MVP |
| Auditoria WCAG completa | | Mantine já é acessível por padrão (RNF15) |

---

## 3. Pirâmide de testes adotada

```
        ╱╲          Exploratório  ── sessões time-boxed (QA)
       ╱  ╲                          heurísticas, sem roteiro
      ╱────╲        Funcional     ── CT01–CT14 manuais com evidência (QA)
     ╱      ╲                        cobre a jornada ponta a ponta
    ╱────────╲      Integração    ── TestClient + PostgreSQL (Eng + QA)
   ╱          ╲                      contrato da API, autorização
  ╱────────────╲    Unitário      ── 20 pytest + Vitest (Engenharia)
                                     regras de negócio isoladas, sem banco
```

| Nível | Onde | Ferramenta | Responsável | Marcador | Quantidade |
|---|---|---|---|---|---|
| Unitário backend | `backend/tests/unit/` | pytest + fakes | Engenharia | `@pytest.mark.unit` | 17 |
| Unitário frontend | `frontend/__tests__/` | Vitest + RTL | Engenharia | — | 6 |
| Integração | `backend/tests/integration/` | pytest + TestClient | Eng + QA | `@pytest.mark.integration` | 3 |
| Funcional manual | `08-casos-de-teste.md` | roteiro + evidência | QA | CT01–CT14 | 14 |
| Exploratório | §6 deste documento | sessões por charter | QA | EXP-01… | 4 sessões |
| Regressão | CI | GitHub Actions | automático | — | toda push/PR |

O exigido pelo enunciado é **5 testes unitários** e **10 casos de teste**. Entregamos 20 e 14 —
porque a matriz de rastreabilidade da §4 exigiu cobrir RN07 a RN15, que o mínimo não alcançava.

---

## 4. Matriz de cobertura das regras

Nenhuma RN pode ficar sem linha aqui. Antes de fechar a sprint, o QA revalida esta tabela.

| RN | Teste unitário | Caso de teste | Positivo + negativo? |
|---|---|---|---|
| RN01 CPF único | CTU01 | CT02 | ✅ CT01 (positivo) / CT02 (negativo) |
| RN02 e-mail único | CTU02 | CT03 | ✅ inclui e-mail nulo duplicado permitido |
| RN03 horário ocupado | CTU03 | CT05 | ✅ CT04 (positivo) / CT05 (negativo) / CT10 (reagendar após cancelar) |
| RN04 24h antecedência | CTU04 | CT06, CT07 | ✅ 48h passa / 12h bloqueia |
| RN05 alocação dupla | CTU05 | CT08 | ✅ |
| RN06 status | CTU06 | CT09 | ✅ |
| RN07 CPF válido | CTU07 (front) | CT01 | ✅ |
| RN08 e-mail válido | Vitest | CT03 | ✅ |
| RN09 horário comercial | CTU08 | CT13 | ✅ |
| RN10 transição de status | CTU09 | CT09, CT10 | ✅ cancelar FINALIZADA bloqueia |
| RN11 hash de senha | CTU10 | CT04 | ✅ |
| RN12 perfil por rota | CTU11 | CT11, CT12 | ✅ 403 e 401 |
| RN13 expiração do token | — | CT12 | ⚠️ verificação manual |
| RN14 atendente cria atendente | — | CT14 | ✅ |
| RN15 fuso horário | CTU04 | CT06 | ✅ `agora` injetado |

---

## 5. Ambientes

| Ambiente | Como | Uso |
|---|---|---|
| **Local dev** | `make bootstrap` | Desenvolvimento e execução dos CTs |
| **CI** | GitHub Actions + serviço PostgreSQL 16 | Regressão automática em push/PR |
| **Demonstração** | `make bootstrap` na máquina do apresentador | Sprint Review e apresentação final |

Dados de teste vêm do seed idempotente: 1 atendente (`recepcao@clinica.com` / `admin123`) e 3
especialidades. Demais dados criados pelo próprio roteiro dos CTs — o que garante que o teste
exercita o cadastro de verdade.

Para demonstrar a RN04 sem esperar 24h reais, baixe `CANCELAMENTO_ANTECEDENCIA_HORAS` no `.env`.
Registre no relatório quando fizer isso.

---

## 6. Testes exploratórios

Time-boxed em **45 min** por sessão, com charter escrito **antes** de começar.

### Sessões planejadas

| ID | Charter | Área | Sprint |
|---|---|---|---|
| EXP-01 | Explorar cadastros buscando falhas de validação e duplicidade | US-01 a US-04 | 1 |
| EXP-02 | Explorar lançamento de agenda buscando conflito de horário | US-05, US-07 | 1 |
| EXP-03 | Explorar agendamento buscando falhas de estado e concorrência | US-08, US-09 | 2 |
| EXP-04 | Explorar cancelamento e limites da regra de 24h | US-11, US-12, US-13 | 2 |

### Heurísticas para este MVP

| Heurística | O que tentar |
|---|---|
| **Navegação fora do fluxo** | Voltar/avançar do browser no meio do agendamento; abrir URL de etapa direto |
| **Duplo envio** | Clicar duas vezes rápido em "Confirmar"; duas abas no mesmo slot |
| **Estado obsoleto** | Deixar a lista de horários aberta, cancelar em outra aba, tentar agendar |
| **Fronteira de tempo** | Cancelar com exatamente 24h00; 23h59; 24h01 |
| **Manipulação de identidade** | Trocar `paciente_id` no body; usar token de paciente em rota de atendente |
| **Token** | Requisição com token expirado, malformado, ausente, de outro perfil |
| **Entrada limite** | CPF com máscara/sem/incompleto; nome com 1 caractere; e-mail sem TLD; data no passado |
| **Horário limite** | Agenda às 07:59, 08:00, 17:59, 18:00, 18:01 |
| **Vazio** | Listar horários de médico sem agenda; histórico de paciente sem consulta |
| **Unicode** | Nome com acento, ç, emoji; e-mail em maiúsculas |

### Registro obrigatório

```markdown
### Sessão EXP-0X — <título>
- **Charter:** <o que explorar e por quê>
- **Duração:** 45 min · **Data:** DD/MM/AAAA · **Executor:** <nome>
- **Ambiente:** Docker local, seed aplicado, commit <sha>
- **Achados:**
  | # | Descrição | Severidade | Issue |
  |---|---|---|---|
- **Não testado / ficou de fora:** <o que faltou tempo>
- **Evidências:** `docs/evidencias/EXP-0X/`
```

Sessão sem achado também é registrada — a informação de que uma área foi explorada e está
estável tem valor.

---

## 7. Evidências

Estrutura em `docs/evidencias/`:

```
docs/evidencias/
├── CT02/
│   ├── README.md            # CT, US, RN, ambiente, data, executor, resultado
│   ├── 01-cadastro-inicial.png
│   ├── 02-tentativa-cpf-duplicado.png
│   └── 03-mensagem-de-erro.png
└── EXP-03/
    ├── README.md
    └── ...
```

Requisitos da evidência:

- O print precisa mostrar a **mensagem de erro exata** — é ela que prova que a RN foi aplicada.
- Nome do arquivo numerado na ordem do passo.
- `README.md` da pasta cita CT/EXP, US, RN, ambiente, data, executor e veredito.
- Sem dado pessoal real. Use os dados fictícios dos CTs.

---

## 8. Gestão de defeitos

### Severidade

| Nível | Definição | SLA na sprint |
|---|---|---|
| **Crítica** | Bloqueia fluxo principal ou viola RN obrigatória (RN01–RN06) | Corrigir no mesmo dia |
| **Alta** | Viola RN, mas há contorno; ou quebra fluxo secundário | Corrigir na sprint |
| **Média** | Validação, UX ou mensagem incorreta sem violar RN | Backlog priorizado |
| **Baixa** | Cosmético, texto, alinhamento | Backlog |

### Fluxo

```
QA encontra → Issue com template bug.yml → item no board (Backlog)
    → Eng move para In progress → PR com fix + teste de regressão
    → CI verde → QA reexecuta o CT → In review → Done
```

Todo bug corrigido ganha um **teste automatizado de regressão**. Sem isso, o bug volta.
O commit do fix referencia a Issue: `fix(consulta): corrige fuso no calculo de 24h (#12)`.

---

## 9. Critérios de entrada e saída

### Entrada (para começar a testar uma US)

- [ ] PR aberto para `develop` com CI verde
- [ ] Critérios de aceite da US disponíveis no board
- [ ] Ambiente sobe com `make bootstrap`
- [ ] Migração aplicada e seed executado

### Saída (para fechar a sprint)

- [ ] 100% dos casos de teste planejados executados
- [ ] **0** defeito Crítico ou Alto em aberto
- [ ] Toda RN01–RN15 com ≥ 1 CT executado e evidência anexada
- [ ] Todas as sessões exploratórias da sprint registradas
- [ ] Cobertura de testes ≥ 80% no backend
- [ ] CI verde no último commit de `develop`
- [ ] Evidências commitadas em `docs/evidencias/`
- [ ] Critérios de aceite validados pelo PO na Sprint Review

---

## 10. Quality gate no CI

`.github/workflows/ci.yml` — quatro jobs:

| Job | O que valida | Reprova se |
|---|---|---|
| `backend` | `ruff check`, `ruff format --check`, `alembic upgrade head`, pytest unit + integração com cobertura | Lint, formatação, migração ou teste falha |
| `frontend` | `eslint`, `tsc --noEmit`, `vitest --coverage`, `next build` | Lint, tipo, teste ou build falha |
| `docker` | `docker compose config`, sobe o stack, healthcheck, migração, **seed rodado 2×** | Stack não sobe, API não responde, ou seed não é idempotente |
| `quality-gate` | Agrega os três | Qualquer um falhou |

`quality-gate` é o **required status check** da proteção de `main` e `develop`. É o que impede
merge de código quebrado.

O seed rodar duas vezes no CI não é redundância: é o teste da idempotência prometida no ADR-004.

---

## 11. Riscos do plano

| Risco | Mitigação |
|---|---|
| Testar RN04 exige esperar 24h | `CANCELAMENTO_ANTECEDENCIA_HORAS` configurável; nos unitários `agora` é injetado |
| Concorrência é difícil de reproduzir manualmente | CT com duas abas + validação por código (índice parcial + `FOR UPDATE`) |
| Cobertura alta com teste fraco | Revisão de PR olha se o teste tem asserção significativa, não só se passou |
| Fake de repository divergir do real | Testes de integração exercitam o caminho real |
| Evidência sem valor probatório | Checklist da §7 exige mensagem de erro visível no print |
| QA sobrecarregado no fim da sprint | CTs escritos no dia 2–3, execução distribuída ao longo da sprint |
