# Documentação do projeto

Sistema de Gestão de Clínica Médica (MVP) — AV2 Engenharia de Software Moderna, Equipe 01.

---

## Leia primeiro

| Se você é… | Comece por |
|---|---|
| **novo na equipe** | [17 Como rodar](17-como-rodar.md) → [`../CLAUDE.md`](../CLAUDE.md) → [00 Visão](00-visao-do-produto.md) → [03 Arquitetura](03-arquitetura.md) |
| **avaliador** | [ADR-008 Rebaseline](adr/ADR-008-rebaseline-escopo.md) → [14 Conflitos e decisões](14-conflitos-e-decisoes.md) → [05 Clean Code](05-clean-code.md) → [06 Design Patterns](06-design-patterns.md) |
| **PO** | [01 Requisitos](01-requisitos.md) → [02 Backlog](02-backlog.md) → [11 Ciclo](11-ciclo-desenvolvimento.md) |
| **Engenharia** | [03 Arquitetura](03-arquitetura.md) → [04 Modelo de dados](04-modelo-de-dados.md) → [adr/](adr/) |
| **QA** | [07 Plano de testes](07-plano-de-testes.md) → [08 Casos de teste](08-casos-de-teste.md) → [09 CI/CD](09-ci-cd.md) |

---

## Índice

### Produto

| Doc | Conteúdo | Responsável |
|---|---|---|
| [00 — Visão do produto](00-visao-do-produto.md) | Problema, escopo dentro/fora, proposta de valor, métricas, riscos | Uanderson |
| [01 — Requisitos](01-requisitos.md) | RF01–RF22, RNF01–RNF15, RN01–RN15, matriz de rastreabilidade | Uanderson |
| [02 — Backlog](02-backlog.md) | US-00 a US-13 com critérios de aceite em Gherkin | Uanderson |
| [15 — Melhorias futuras](15-melhorias-futuras.md) | O que ficou fora do MVP, com motivo e versão-alvo | Uanderson |

### Engenharia

| Doc | Conteúdo | Responsável |
|---|---|---|
| [03 — Arquitetura](03-arquitetura.md) | **§2 MVC do backend · §3 arquitetura do frontend · §4 contrato entre as duas** | Ronaldo |
| [04 — Modelo de dados](04-modelo-de-dados.md) | ER, constraints por regra, migrações, SQL de verificação | Ronaldo |
| [05 — Clean Code](05-clean-code.md) | 3 práticas com ruim/bom nas duas stacks + SOLID | Ronaldo · João Vitor |
| [06 — Design Patterns](06-design-patterns.md) | Strategy e Repository (backend) com diagramas e alternativas | Ronaldo |
| [10 — Git Flow](10-git-flow.md) | Branches, commits, PR, code review, release, board | Ronaldo |
| [17 — Como rodar](17-como-rodar.md) | Subir o projeto, comandos do dia a dia, problemas conhecidos | Felipe |

### Qualidade

| Doc | Conteúdo | Responsável |
|---|---|---|
| [07 — Plano de testes](07-plano-de-testes.md) | Pirâmide, escopo, exploratório, defeitos, critérios de saída | Jackson |
| [08 — Casos de teste](08-casos-de-teste.md) | CT01–CT14 + mapa dos unitários por stack + relatório de execução | Jackson |
| [09 — CI/CD](09-ci-cd.md) | Quatro jobs, quality gate, troubleshooting | Felipe |

### Processo

| Doc | Conteúdo | Responsável |
|---|---|---|
| [11 — Ciclo de desenvolvimento](11-ciclo-desenvolvimento.md) | Scrum + Kanban, cerimônias, DoR/DoD, métricas, atas | Uanderson |
| [12 — Cronograma](12-cronograma.md) | Calendário 31/07 a 10/08, 2 sprints por encontro, marcos, priorização | Uanderson |
| [13 — Papéis](13-papeis-e-responsabilidades.md) | Equipe de 6, entregáveis por pessoa, matriz de avaliação | Antonio |

### Análise

| Doc | Conteúdo |
|---|---|
| [14 — Conflitos e decisões](14-conflitos-e-decisoes.md) | 13 divergências entre as fontes do enunciado e como foram resolvidas |
| [adr/](adr/) | 8 Architecture Decision Records |

### Apoio

| Pasta | Conteúdo |
|---|---|
| [`material-aulas/`](material-aulas/) | PDFs e PPTX do curso — fonte para justificar as decisões |
| [`evidencias/`](evidencias/) | Evidências de execução dos casos de teste |
| [`apresentacao/`](apresentacao/) | Slides da apresentação final |
| [`../.claude/skills/`](../.claude/skills/) | Skills de projeto para agentes de IA |

---

## Entregáveis da AV2 → onde estão

| Exigência | Documento |
|---|---|
| PO: escrita e documentação | [00](00-visao-do-produto.md), [01](01-requisitos.md), [02](02-backlog.md) |
| PO: ciclo de desenvolvimento | [11](11-ciclo-desenvolvimento.md) |
| PO: verificar critérios de aceite | [02](02-backlog.md) + atas em [11](11-ciclo-desenvolvimento.md) §9 |
| PO: material de slide | [`apresentacao/`](apresentacao/) + roteiro em [13](13-papeis-e-responsabilidades.md) |
| ENG: Git Flow e repositório | [10](10-git-flow.md) |
| ENG: arquitetura MVC documentada | [03](03-arquitetura.md) §2 (backend) |
| ENG: 3 práticas de Clean Code | [05](05-clean-code.md) |
| ENG: 2 padrões de projeto | [06](06-design-patterns.md) + [ADR-006](adr/ADR-006-design-patterns.md) |
| ENG: 5 testes unitários por stack | `backend/tests/unit/` (pytest) · `frontend/__tests__/` (Vitest) |
| QA: plano de testes | [07](07-plano-de-testes.md) |
| QA: 10 casos de teste | [08](08-casos-de-teste.md) — **14 entregues** |
| QA: exploratório + evidências | [07](07-plano-de-testes.md) §6 + [`evidencias/`](evidencias/) |
| QA: CI no GitHub Actions | [09](09-ci-cd.md) + `.github/workflows/ci.yml` |
| Quadro Kanban | [GitHub Projects](https://github.com/users/jacksoncassemiro/projects/3) + [10](10-git-flow.md) §7 |
| Cronograma | [12](12-cronograma.md) |

---

## Manutenção

- Alterou comportamento? Atualize o documento correspondente **no mesmo PR**.
- Nova regra de negócio? Registre em [01](01-requisitos.md) com ID `RNxx` e adicione à matriz.
- Decisão arquitetural? Novo ADR em [`adr/`](adr/). **ADR existente não se edita** — cria-se um
  que o substitui.
- A Wiki do GitHub espelha estes documentos. Publique com `scripts/publicar-wiki.sh`.
