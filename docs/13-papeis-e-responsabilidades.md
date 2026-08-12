# Papéis e responsabilidades

## Composição da equipe — 7 pessoas

| Papel | Pessoas |
|---|---|
| 👑 **Product Owner** | Jackson Cassemiro |
| 💻 **Engenharia de Software** | Antonio Júnior · João Vitor Lira · Ronaldo Filho |
| 🧪 **Quality Assurance** | Uanderson Silva · Felipe Araújo · Alyssandro Gouveia |

> **Nota sobre o enunciado.** O enunciado sugere *"2 para cada"* papel. A equipe tem
> **1 PO, 3 Engenharia e 3 QA** (Alyssandro Gouveia entrou depois, como reforço de QA). Isso
> não é problema desde que **todo entregável tenha um responsável nomeado** — é o que esta
> página faz. Se o avaliador cobrar a divisão 2/2/2 do PO, a resposta é a coluna "Apoio":
> **Antonio atua como PO de apoio** nos itens de processo (cerimônias e slides), o que dá dois
> nomes no papel de PO sem inflar o escopo de ninguém.

Combinado com o grupo: os papéis definem **responsabilidade pela entrega**, não fronteira
rígida. Quem terminar antes ajuda quem estiver com mais carga — desde que o responsável nomeado
continue sendo quem está na tabela, para não haver dúvida na avaliação.

---

## 👑 PO — Jackson

| # | Entregável avaliado | Responsável | Apoio | Onde |
|---|---|---|---|---|
| 1 | Escrita e documentação | **Jackson** | — | `docs/00`, `docs/01`, `docs/02`, Wiki |
| 2 | Ciclo de desenvolvimento | **Jackson** | Antonio | `docs/11-ciclo-desenvolvimento.md` |
| 3 | Verificar critérios de aceite | **Jackson** | — | Board (coluna UAT) + ata da Review |
| 4 | Avaliar e aprovar PRs de alteração do projeto | **Jackson** | — | Pull Requests no GitHub |
| 5 | Material de apresentação (slides) | **Antonio** | Jackson | `docs/apresentacao/` |

**Jackson — backlog e validação**

- Documento de visão do produto ([`00`](00-visao-do-produto.md)): objetivo, público, escopo
  dentro/fora, proposta de valor, métricas.
- Requisitos consolidados ([`01`](01-requisitos.md)): RF, RNF, RN e matriz de rastreabilidade.
- Backlog priorizado ([`02`](02-backlog.md)): US-00 a US-13 no formato *"Como… Quero… Para…"*
  com critérios de aceite em Gherkin.
- **Guardar o escopo.** Depois do rebaseline ([ADR-008](adr/ADR-008-rebaseline-escopo.md)),
  pedido novo que não esteja no enunciado vai para
  [`15-melhorias-futuras.md`](15-melhorias-futuras.md), não para a sprint.
- **Validação na coluna UAT:** percorrer cada critério de aceite da US entregue e aprovar ou
  rejeitar. Rejeição volta ao board com o motivo escrito.
- **Avaliação e aprovação de PRs:** como PO, revisa e aprova as Pull Requests de alteração do
  projeto antes do merge em `develop` — além (não em substituição) do code review cruzado entre
  Engenharia, que é responsabilidade compartilhada de todos.
- Manter a Wiki sincronizada com `docs/` (`.\scripts\gerar-wiki.ps1`, ou `python3 scripts/gerar-wiki.py`).

**Antonio — cerimônias e apresentação (PO de apoio)**

- Conduzir Planning, sincronizações, Review e Retrospectiva; registrar atas em
  [`11`](11-ciclo-desenvolvimento.md) §9.
- Manter o board: fazer o WIP ser respeitado, cobrar item parado.
- Montar os slides — roteiro na seção *Roteiro dos slides* abaixo.
- Apoia o Jackson (PO) nos itens de processo listados acima.

---

## 💻 Engenharia — Ronaldo, João Vitor, Antonio

Os 5 entregáveis de engenharia entre 3 pessoas. Cada um é **dono** de um pedaço verificável,
e não há dois donos para a mesma coisa.

| # | Entregável avaliado | Responsável | Apoio | Onde |
|---|---|---|---|---|
| 1 | Estratégia de entrega — Git Flow e repositório | **Ronaldo** | Felipe | `docs/10-git-flow.md`, branch protection |
| 2 | Arquitetura MVC desenvolvida e documentada | **Ronaldo** | João Vitor | `docs/03-arquitetura.md` §2 + `backend/app/` |
| 3 | 3 práticas de Clean Code | **Ronaldo** (backend) · **João Vitor** (frontend) | Antonio | `docs/05-clean-code.md` + código |
| 4 | 2 padrões de projeto | **Ronaldo** | João Vitor | `docs/06-design-patterns.md` + `backend/app/` |
| 5 | 5 testes unitários por stack | **Ronaldo** (pytest) · **João Vitor** (Vitest) | Antonio | `backend/tests/unit/` · `frontend/__tests__/` |

> **Redistribuição após a saída de Jonatha.** Ele era o responsável nomeado pelos entregáveis
> 2, 3 e 4. **Ronaldo assume o backend e o domínio por inteiro** — arquitetura MVC, Clean Code
> do backend e os dois Design Patterns. Clean Code e testes unitários do frontend ficam com
> João Vitor, já que são práticas de outra stack e não fazem sentido concentradas numa pessoa
> só. Decisão registrada no [ADR-008](adr/ADR-008-rebaseline-escopo.md).

Divisão do trabalho de código:

| Pessoa | Frente | Escopo |
|---|---|---|
| **Ronaldo** | Backend inteiro | Models, migrações, Services, Strategy, Repository, auth, autorização por perfil, seed. Dono dos conceitos avaliados no backend (MVC, Clean Code, Patterns). Git Flow e branch protection. |
| **João Vitor** | Frontend — paciente | Telas do paciente (login, primeiro acesso, agendar, minhas consultas, meus dados), guardas de rota, testes Vitest, Clean Code do frontend. |
| **Antonio** | Frontend — atendente + processo | Telas do atendente (especialidades, médicos, pacientes, agenda, consultas), `src/lib/api.ts`, componentes compartilhados; cerimônias e slides como PO de apoio. |

Regras para todos:

- Camadas Controller → Service → Repository → Model; manter os contratos do
  [ADR-002](adr/ADR-002-camadas-mvc.md).
- **Backend e frontend são aplicações separadas** ([`03`](03-arquitetura.md)). O MVC avaliado é
  o do backend; o frontend tem arquitetura própria de componentes e rotas.
- Migração Alembic **sempre revisada à mão** — o autogenerate não cria índice parcial. Existe
  `backend/tests/integration/test_migracoes.py` para pegar divergência entre model e migração.
- Erro da API traduzido em notificação no frontend, nunca `alert` nem erro cru.
- Code review cruzado: quem escreveu backend revisa frontend e vice-versa.
- **Fatia vertical:** a US só entra em UAT com backend, frontend e teste prontos.

---

## 🧪 QA — Uanderson, Felipe e Alyssandro

| # | Entregável avaliado | Responsável | Apoio | Onde |
|---|---|---|---|---|
| 1 | Plano de testes | **Uanderson** | Felipe, Alyssandro | `docs/07-plano-de-testes.md` |
| 2 | 10 casos de teste (14 entregues) | **Uanderson** | Felipe, Alyssandro | `docs/08-casos-de-teste.md` |
| 3 | Testes exploratórios com evidências | **Felipe** | Uanderson, Alyssandro | `docs/07` §6 + `docs/evidencias/` |
| 4 | CI no GitHub Actions | **Felipe** | Ronaldo | `.github/workflows/ci.yml` |

**Uanderson — plano e casos de teste**

- Plano de testes: escopo, pirâmide, ambientes, critérios de entrada e saída.
- CT01–CT14 escritos **antes** do código da US existir, para não enviesar o teste pela
  implementação.
- Manter a matriz de cobertura: **toda RN01–RN15 com pelo menos um caso negativo**.
- Executar os CTs e preencher o relatório de execução.
- Abrir Issue de bug com o template `.github/ISSUE_TEMPLATE/bug.yml`, com severidade,
  prioridade e evidência.

**Felipe — CI/CD, exploratório e evidências**

- Pipeline com quatro jobs (`backend`, `frontend`, `docker`, `quality-gate`). O job `docker`
  roda o seed **duas vezes** para provar a idempotência do
  [ADR-004](adr/ADR-004-bootstrap-atendente.md).
- Três sessões exploratórias (EXP-01 a EXP-03) com charter e registro.
- Organizar `docs/evidencias/` conforme a §7 do plano de testes.
- Relatório final de testes para a apresentação.

**Alyssandro — reforço de QA**

Entrou depois do resto da equipe, como apoio geral de Uanderson e Felipe nos dois entregáveis
de QA (não tem entregável próprio nomeado ainda — ver nota acima). Ajuda a executar CTs
pendentes e a registrar evidência, priorizando o que estiver mais atrasado no board.

---

## Roteiro dos slides

| Slide | Conteúdo |
|---|---|
| 1 | Capa: projeto, equipe, papéis |
| 2 | Problema (telefone + planilha) e proposta |
| 3 | Escopo do MVP: dentro / fora — e **por que** cortamos ([ADR-008](adr/ADR-008-rebaseline-escopo.md)) |
| 4 | Backlog e priorização |
| 5 | **Arquitetura: duas aplicações**, não uma. MVC do backend em detalhe |
| 6 | Arquitetura do frontend (componentes + rotas) e o contrato entre as duas |
| 7 | Modelo de dados (ER) |
| 8 | **3 práticas de Clean Code**, com exemplo ruim/bom nas duas stacks |
| 9 | **2 Design Patterns** do backend, com diagrama e justificativa |
| 10 | Conflitos do enunciado e decisões (ADRs) — diferencial |
| 11 | Git Flow e board |
| 12 | Plano de testes e cobertura das RNs |
| 13 | Pipeline de CI (print do quality gate verde **e** de um PR bloqueado) |
| 14 | **Demonstração ao vivo** |
| 15 | Métricas: testes automatizados por stack, CTs executados, CI verde |
| 16 | Melhorias futuras: o que ficou fora e por quê |
| 17 | Retrospectiva: o que funcionou, o que faríamos diferente |

---

## Responsabilidades compartilhadas

| Responsabilidade | Quem |
|---|---|
| Atualizar o board ao começar e ao terminar um item | Quem está com o item |
| Code review (mínimo 1 aprovação por PR) | Todos, cruzado |
| Manter `docs/` em sincronia com o código | Quem alterou o comportamento |
| Não quebrar `develop` | Todos |
| Ajudar quem estiver sobrecarregado | Todos |

---

## Matriz de entregáveis × avaliação

| Exigência do enunciado | Responsável | Entregue em | Status |
|---|---|---|---|
| PO: escrita e documentação | Jackson | `docs/00`, `01`, `02` + Wiki | ✅ estrutura pronta |
| PO: ciclo de desenvolvimento | Jackson | `docs/11` | ✅ |
| PO: verificar critérios de aceite | Jackson | Board (UAT) + ata da Review | ⬜ durante as sprints |
| PO: avaliar e aprovar PRs | Jackson | Pull Requests no GitHub | ⬜ durante as sprints |
| PO: material de slide | Antonio | `docs/apresentacao/` | ⬜ 09/08 |
| ENG: Git Flow e repositório | Ronaldo | `docs/10` + branch protection | ✅ documentado |
| ENG: arquitetura MVC documentada | Ronaldo | `docs/03` §2 + `backend/app/` | ✅ |
| ENG: 3 práticas de Clean Code | Ronaldo (back) · João Vitor (front) | `docs/05` | ✅ backend · ⬜ frontend |
| ENG: 2 padrões de projeto | Ronaldo | `docs/06` + [ADR-006](adr/ADR-006-design-patterns.md) | ✅ |
| ENG: 5 testes unitários por stack | Ronaldo · João Vitor | `backend/tests/unit/` · `frontend/__tests__/` | ✅ backend · ⬜ frontend |
| QA: plano de testes | Uanderson | `docs/07` | ✅ |
| QA: 10 casos de teste | Uanderson | `docs/08` | ✅ **14 escritos** |
| QA: exploratório + evidências | Felipe | `docs/07` §6 + `docs/evidencias/` | ⬜ durante as sprints |
| QA: CI no GitHub Actions | Felipe | `.github/workflows/ci.yml` | ✅ |
| Quadro Kanban | Antonio | [GitHub Projects](https://github.com/users/jacksoncassemiro/projects/3) | ⬜ recriar com `scripts/popular-board` |
| Cronograma | Jackson | `docs/12-cronograma.md` | ✅ |
