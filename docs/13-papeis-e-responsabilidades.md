# Papéis e responsabilidades

## ⚠️ Pendência: composição da equipe

Há uma divergência que **precisa ser resolvida em Sprint Planning**:

| Fonte | Composição |
|---|---|
| Enunciado da AV2 | *"As funções, sendo **2 para cada**"* → 2 PO + 2 Eng + 2 QA = **6 pessoas** |
| `README.md` do repositório | **7 nomes**: 1 PO + 4 Engenharia + 2 QA |
| `Aula - Pratica 13-05.pdf` | "Grupo 2" com 6 nomes que **não coincidem** com o README |

A distribuição abaixo segue o enunciado (2 por papel) usando os nomes do README. **Confirmem e
corrijam o README** — a divisão de papéis é item avaliado, e um README desalinhado com o
enunciado é visível para o avaliador.

Combinado com o grupo: os papéis definem **responsabilidade pela entrega**, não uma fronteira
rígida. Quem terminar antes ajuda quem estiver com mais carga — desde que o **responsável pelo
entregável** continue sendo quem está na tabela, para não haver dúvida na avaliação.

---

## Distribuição proposta (2 por papel)

| Papel | Pessoa | Foco |
|---|---|---|
| **PO-A** | Uanderson Henrique | Backlog, User Stories, critérios de aceite, validação |
| **PO-B** | *(a definir — ver pendência)* | Cerimônias Scrum, board, slides da apresentação |
| **ENG-A** | Jonatha da Silva | Backend: arquitetura, Clean Code, Design Patterns, testes unitários |
| **ENG-B** | João Vitor | Frontend: Next.js + Mantine, testes Vitest |
| **QA-A** | Jackson Douglas | Plano de testes, casos de teste, execução, evidências |
| **QA-B** | Felipe da Silva | CI/CD no GitHub Actions, testes exploratórios, relatório final |

Nomes restantes do README (Ronaldo de Melo, Antonio Andrade) — alocar conforme a decisão do
grupo sobre a pendência. Sugestão: reforço em ENG-A/ENG-B (backend e frontend são as maiores
cargas) mantendo os responsáveis pelos entregáveis.

---

## PO — Product Owner

### Entregáveis avaliados

| # | Entregável | Onde | Responsável |
|---|---|---|---|
| 1 | Desenvolvimento da escrita e documentação | `docs/00`, `docs/01`, `docs/02`, Wiki | PO-A |
| 2 | Ciclo de desenvolvimento | `docs/11-ciclo-desenvolvimento.md` | PO-B |
| 3 | Verificação dos critérios de aceite | Board + ata da Sprint Review | PO-A |
| 4 | Material de apresentação (slides) | `docs/apresentacao/` | PO-B |

### PO-A — Backlog e critérios de aceite

- Documento de visão do produto ([`00-visao-do-produto.md`](00-visao-do-produto.md)): objetivo,
  público, escopo dentro/fora, proposta de valor, métricas de sucesso.
- Requisitos consolidados ([`01-requisitos.md`](01-requisitos.md)): RF, RNF, RN e a matriz de
  rastreabilidade.
- Backlog priorizado ([`02-backlog.md`](02-backlog.md)): US-00 a US-15 no formato
  *"Como… Quero… Para…"* com critérios de aceite em Gherkin.
- **Validação na Sprint Review**: percorrer cada critério de aceite da US entregue e
  aprovar ou rejeitar. Rejeição volta ao board com o motivo escrito.
- Manter a Wiki sincronizada com `docs/`.

Nota: o backlog atual da Wiki (US-00 a US-12) é obra do PO-A e resolveu o conflito de cadastro
do paciente (ver [ADR-005](adr/ADR-005-cadastro-paciente.md)). US-13, US-14 e US-15 foram
adicionadas para cobrir lacunas identificadas em
[`14-conflitos-e-decisoes.md`](14-conflitos-e-decisoes.md).

### PO-B — Cerimônias e apresentação

- Conduzir Planning, Daily, Review e Retrospectiva; registrar atas em
  `docs/11-ciclo-desenvolvimento.md`.
- Manter o board (GitHub Projects): fazer o WIP ser respeitado, cobrar item parado.
- Montar os slides. Roteiro sugerido:

| Slide | Conteúdo |
|---|---|
| 1 | Capa: projeto, equipe, papéis |
| 2 | Problema (telefone + planilha) e proposta |
| 3 | Escopo do MVP: dentro / fora |
| 4 | Backlog e priorização |
| 5 | Arquitetura em camadas (diagrama de `03-arquitetura.md`) |
| 6 | Modelo de dados (ER) |
| 7 | **3 práticas de Clean Code** com ruim/bom |
| 8 | **2 Design Patterns** com diagrama e justificativa |
| 9 | Conflitos do enunciado e decisões (ADRs) — diferencial |
| 10 | Git Flow e board |
| 11 | Plano de testes e cobertura |
| 12 | Pipeline de CI (print do quality gate verde) |
| 13 | **Demonstração ao vivo** |
| 14 | Métricas: 20 testes unitários, 14 CTs, CI verde |
| 15 | Retrospectiva: o que funcionou, o que faríamos diferente |

---

## Engenheiro de Software

### Entregáveis avaliados

| # | Entregável | Onde | Responsável |
|---|---|---|---|
| 1 | Estratégia de entrega — Git Flow e repositório | `docs/10-git-flow.md`, branch protection | ENG-A |
| 2 | Arquitetura MVC desenvolvida e documentada | `docs/03-arquitetura.md` + código | ENG-A |
| 3 | 3 práticas de Clean Code | `docs/05-clean-code.md` + código | ENG-A |
| 4 | 2 padrões de projeto | `docs/06-design-patterns.md` + código | ENG-A |
| 5 | 5 testes unitários (20 entregues) | `backend/tests/unit/` | ENG-A |

### ENG-A — Backend e conceitos avaliados

- Camadas Router → Service → Repository → Model; manter os contratos do
  [ADR-002](adr/ADR-002-camadas-mvc.md).
- Models com as constraints das RNs; migrações Alembic revisadas (o autogenerate não cria
  índice parcial — conferir sempre).
- **Strategy** em `cancelamento_strategy.py` e **Repository** em `repositories/`.
- Testes unitários com os fakes de `tests/conftest.py`.
- Configuração do Git Flow: proteção de `main` e `develop`, `quality-gate` como required check,
  PR obrigatório com 1 aprovação.
- Code review de todo PR do frontend.

### ENG-B — Frontend

- Telas conforme `frontend/src/app/README.md`, seguindo a skill `clinica-frontend`.
- Route groups `(paciente)` e `(atendente)` com guarda por perfil (RF05).
- Formulários com `@mantine/form` replicando as validações do backend (RN07, RN08).
- Erro da API traduzido em notificação — nunca `alert`, nunca erro cru.
- Testes Vitest das funções puras e dos componentes com estado.
- Code review de todo PR do backend.

---

## QA — Quality Assurance

### Entregáveis avaliados

| # | Entregável | Onde | Responsável |
|---|---|---|---|
| 1 | Plano de testes | `docs/07-plano-de-testes.md` | QA-A |
| 2 | 10 casos de teste (14 entregues) | `docs/08-casos-de-teste.md` | QA-A |
| 3 | Testes exploratórios com evidências | `docs/07` §6 + `docs/evidencias/` | QA-B |
| 4 | CI no GitHub Actions | `.github/workflows/ci.yml` | QA-B |

### QA-A — Plano e casos de teste

- Plano de testes: escopo, pirâmide, ambientes, critérios de entrada/saída.
- CT01–CT14 escritos **até o dia 3** — antes do código existir, para não enviesar o teste pela
  implementação.
- Manter a matriz de cobertura: **toda RN01–RN15 com pelo menos um caso negativo**.
- Executar os CTs e preencher o relatório de execução.
- Abrir Issue de bug com o template, com severidade e evidência.

### QA-B — CI/CD, exploratório e evidências

- Pipeline com quatro jobs (`backend`, `frontend`, `docker`, `quality-gate`).
  O job `docker` roda o seed **duas vezes** para provar a idempotência do
  [ADR-004](adr/ADR-004-bootstrap-atendente.md).
- Quatro sessões exploratórias (EXP-01 a EXP-04) com charter e registro.
- Organizar `docs/evidencias/` conforme o padrão da §7 do plano de testes.
- Relatório final de testes para a apresentação.

---

## Responsabilidades compartilhadas

| Responsabilidade | Quem |
|---|---|
| Daily de 15 min | Todos |
| Code review (mínimo 1 aprovação por PR) | Todos, cruzado |
| Manter o board atualizado | Quem está com o item |
| Manter `docs/` em sincronia com o código | Quem alterou o comportamento |
| Não quebrar `develop` | Todos |
| Ajudar quem estiver sobrecarregado | Todos |

---

## Matriz de entregáveis × avaliação

| Exigência do enunciado | Entregue em | Status |
|---|---|---|
| PO: escrita e documentação | `docs/00`, `01`, `02` + Wiki | ✅ estrutura pronta |
| PO: ciclo de desenvolvimento | `docs/11` | ✅ |
| PO: verificar critérios de aceite | Board + ata da Review | ⬜ durante as sprints |
| PO: material de slide | `docs/apresentacao/` | ⬜ Sprint 2 |
| ENG: Git Flow e repositório | `docs/10` + branch protection | ✅ documentado |
| ENG: arquitetura MVC documentada | `docs/03` + `backend/app/` | ✅ |
| ENG: 3 práticas de Clean Code | `docs/05` + código | ✅ |
| ENG: 2 padrões de projeto | `docs/06` + código | ✅ |
| ENG: 5 testes unitários | `backend/tests/unit/` | ✅ **20 entregues** |
| QA: plano de testes | `docs/07` | ✅ |
| QA: 10 casos de teste | `docs/08` | ✅ **14 entregues** |
| QA: exploratório + evidências | `docs/07` §6 + `docs/evidencias/` | ⬜ durante as sprints |
| QA: CI no GitHub Actions | `.github/workflows/ci.yml` | ✅ |
| Quadro Kanban | GitHub Projects | ⬜ popular com `scripts/popular-board.sh` |
| Cronograma | `docs/12-cronograma.md` | ✅ |
