# Apresentação final

`apresentacao-final-av2-equipe01.pptx` — **23 slides**, 16:9.

---

## Roteiro

| # | Slide |
|---|---|
| 1 | Capa — equipe e identificação |
| 2 | Visão do produto — o problema e a proposta |
| 3 | Escopo do MVP: dentro e fora ([ADR-008](../adr/ADR-008-rebaseline-escopo.md) · [ADR-009](../adr/ADR-009-inativacao-especialidade-medico.md)) |
| 4 | O que é uma User Story — a US-08 na prática |
| 5 | Duas sprints — o que entrou em cada uma |
| 6 | Prioridade — P0, P1 e P2 |
| 7 | Arquitetura: duas aplicações, o MVC no backend |
| 8 | Frontend: componentes, rotas e o contrato HTTP |
| 9 | Modelo de dados — RN garantida no banco |
| 10 | 3 práticas de Clean Code |
| 11 | 2 Design Patterns (Strategy e Repository) |
| 12 | Conflitos do enunciado e decisões (ADRs) |
| 13 | Git Flow — o modelo de branches |
| 14 | Conventional Commits e code review |
| 15 | O board — o que cada coluna significa |
| 16 | Plano de testes — pirâmide e cobertura das RNs |
| 17 | Gestão de defeitos — do bug encontrado ao bug fechado |
| 18 | GitHub Actions — três jobs, um portão (diagrama do pipeline) |
| 19 | O gate provado — o vermelho que virou verde ([IF03](../evidencias/IF03/README.md)) |
| 20 | Demonstração ao vivo |
| 21 | Métricas do projeto |
| 22 | Melhorias futuras |
| 23 | Retrospectiva |

O backlog ocupa três slides (4 a 6): conceito com exemplo real, sprints e priorização.
A estratégia de entrega ocupa três (13 a 15), a qualidade dois (16 e 17) e a integração
contínua dois (18 e 19): o pipeline em diagrama e a evidência real do quality gate barrando
o PR #21 e liberando o PR #25.

---

## Tema visual

16:9 (13,33 × 7,5 pol), fundo branco, tipografia Calibri.

Paleta derivada da cor da aplicação — `clinica` shade 8 (`#28726F`) em
[`frontend/src/theme.ts`](../../frontend/src/theme.ts):

| Uso | Cor |
|---|---|
| Primária | `#28726F` |
| Escura (destaque, títulos de cartão) | `#12635F` |
| Média (apoio) | `#44938F` |
| Clara (chips, níveis baixos) | `#B1D1CF` |
| Fundo de cartão | `#E7F5F4` · alternativo `#FAF4F4` |
| Alerta (severidade Alta / UAT) | `#F08C00` · `#C92A2A` |
| Texto | `#212529` (títulos) · `#495257` (corpo) · `#8A9399` (legendas) |

---

## Demonstração ao vivo

O slide 19 é **apenas o roteiro**. A demonstração acontece ao vivo contra o stack Docker local:
frontend em `localhost:3000`, Swagger em `localhost:8000/docs`.
Subir o ambiente: [`docs/17-como-rodar.md`](../17-como-rodar.md).

---

## De onde vem o conteúdo

Os números e os textos dos slides seguem os documentos canônicos — ao atualizar um deles,
confira se o slide correspondente continua verdadeiro:

- Escopo e regras — [`01-requisitos.md`](../01-requisitos.md), [`15-melhorias-futuras.md`](../15-melhorias-futuras.md)
- User Stories e priorização — [`02-backlog.md`](../02-backlog.md)
- Arquitetura — [`03-arquitetura.md`](../03-arquitetura.md), [`04-modelo-de-dados.md`](../04-modelo-de-dados.md)
- Clean Code e Design Patterns — [`05-clean-code.md`](../05-clean-code.md), [`06-design-patterns.md`](../06-design-patterns.md)
- Testes, defeitos e CI — [`07-plano-de-testes.md`](../07-plano-de-testes.md), [`09-ci-cd.md`](../09-ci-cd.md), [`evidencias/`](../evidencias/)
- Git Flow e board — [`10-git-flow.md`](../10-git-flow.md)
- Decisões — [`adr/`](../adr/)
