# Papéis e responsabilidades

## Composição real da equipe — 7 pessoas

| Papel | Pessoas |
|---|---|
| 👑 **Product Owner** | Uanderson Henrique Batista da Silva |
| 💻 **Engenharia de Software** | Ronaldo de Melo Sabino Filho · Jonatha da Silva Fernandes · João Vitor Mandu de Lira · Antonio Andrade Gomes Júnior |
| 🧪 **Quality Assurance** | Jackson Douglas da Silva Cassemiro · Felipe da Silva Araújo |

> **Nota sobre o enunciado.** O enunciado da AV2 sugere *"2 para cada"* papel. A equipe tem
> **1 PO, 4 Engenharia e 2 QA**. Isso não é problema desde que **todo entregável tenha um
> responsável nomeado** — é o que esta página faz. Se o avaliador cobrar a divisão 2/2/2, a
> resposta é a coluna "Apoio" das tabelas abaixo: um engenheiro atua como **PO de apoio**
> (cerimônias e slides), o que dá dois nomes em cada papel sem inflar o escopo de ninguém.

Combinado com o grupo: os papéis definem **responsabilidade pela entrega**, não uma fronteira
rígida. Quem terminar antes ajuda quem estiver com mais carga — desde que o responsável nomeado
continue sendo quem está na tabela, para não haver dúvida na avaliação.

---

## Alocação por entregável

### 👑 PO — Uanderson

O PO acumula 4 entregáveis avaliados. Para não virar gargalo, **Ronaldo atua como PO de apoio**
nos itens de processo (cerimônias e slides), enquanto Uanderson mantém a propriedade do backlog.

| # | Entregável | Responsável | Apoio | Onde |
|---|---|---|---|---|
| 1 | Escrita e documentação | **Uanderson** | — | `docs/00`, `docs/01`, `docs/02`, Wiki |
| 2 | Ciclo de desenvolvimento | **Uanderson** | Ronaldo | `docs/11-ciclo-desenvolvimento.md` |
| 3 | Verificar critérios de aceite | **Uanderson** | — | Board + ata da Sprint Review |
| 4 | Material de apresentação (slides) | **Ronaldo** | Uanderson | `docs/apresentacao/` |

**Uanderson — backlog e validação**

- Documento de visão do produto ([`00`](Visao-do-Produto)): objetivo, público, escopo
  dentro/fora, proposta de valor, métricas.
- Requisitos consolidados ([`01`](Requisitos)): RF, RNF, RN e matriz de rastreabilidade.
- Backlog priorizado ([`02`](Backlog-e-User-Stories)): US-00 a US-15 no formato *"Como… Quero… Para…"*
  com critérios de aceite em Gherkin.
- **Validação na Sprint Review:** percorrer cada critério de aceite da US entregue e aprovar ou
  rejeitar. Rejeição volta ao board com o motivo escrito.
- Manter a Wiki sincronizada com `docs/`.

O backlog atual da Wiki (US-00 a US-12) é obra dele e resolveu o conflito de cadastro do
paciente (ver [ADR-005](ADR-005-Cadastro-de-Paciente)). US-13, US-14 e US-15 foram
adicionadas para cobrir lacunas de [`14-conflitos-e-decisoes.md`](Conflitos-e-Decisoes).

**Ronaldo — cerimônias e apresentação**

- Conduzir Planning, Daily, Review e Retrospectiva; registrar atas em
  [`11`](Ciclo-de-Desenvolvimento) §9.
- Manter o board: fazer o WIP ser respeitado, cobrar item parado.
- Montar os slides — roteiro na seção *Roteiro dos slides* abaixo.

---

### 💻 Engenharia — Ronaldo, Jonatha, João Vitor, Antonio

Os 5 entregáveis de engenharia dividem bem entre 4 pessoas. Cada um é **dono** de um pedaço
verificável, e não há dois donos para a mesma coisa.

| # | Entregável | Responsável | Apoio | Onde |
|---|---|---|---|---|
| 1 | Estratégia de entrega — Git Flow e repositório | **Antonio** | Jonatha | `docs/10-git-flow.md`, branch protection |
| 2 | Arquitetura MVC desenvolvida e documentada | **Jonatha** | João Vitor | `docs/03-arquitetura.md` + `backend/app/` |
| 3 | 3 práticas de Clean Code | **Jonatha** | Ronaldo | `docs/05-clean-code.md` + código |
| 4 | 2 padrões de projeto | **Jonatha** | Antonio | `docs/06-design-patterns.md` + código |
| 5 | 5 testes unitários | **João Vitor** | Jonatha | `backend/tests/unit/` |

Divisão do trabalho de código:

| Pessoa | Frente | Escopo |
|---|---|---|
| **Jonatha** | Backend — domínio | Models, migrações, Services, Strategy, Repository. É o dono dos conceitos avaliados (MVC, Clean Code, Patterns). |
| **Antonio** | Backend — plataforma | Auth (US-00), autorização por perfil, seed, Git Flow, branch protection, code review. |
| **João Vitor** | Frontend | Telas Next.js + Mantine, formulários, guardas de rota, testes Vitest. |
| **Ronaldo** | Frontend + processo | Telas do atendente, `src/lib/api.ts`, componentes compartilhados; cerimônias e slides como PO de apoio. |

Regras para todos:

- Camadas Router → Service → Repository → Model; manter os contratos do
  [ADR-002](ADR-002-Camadas-MVC).
- Migração Alembic **sempre revisada à mão** — o autogenerate não cria índice parcial. Existe
  `backend/tests/integration/test_migracoes.py` para pegar divergência entre model e migração.
- Erro da API traduzido em notificação no frontend, nunca `alert` nem erro cru.
- Code review cruzado: quem escreveu backend revisa frontend e vice-versa.

---

### 🧪 QA — Jackson e Felipe

| # | Entregável | Responsável | Apoio | Onde |
|---|---|---|---|---|
| 1 | Plano de testes | **Jackson** | Felipe | `docs/07-plano-de-testes.md` |
| 2 | 10 casos de teste (14 entregues) | **Jackson** | Felipe | `docs/08-casos-de-teste.md` |
| 3 | Testes exploratórios com evidências | **Felipe** | Jackson | `docs/07` §6 + `docs/evidencias/` |
| 4 | CI no GitHub Actions | **Felipe** | Antonio | `.github/workflows/ci.yml` |

**Jackson — plano e casos de teste**

- Plano de testes: escopo, pirâmide, ambientes, critérios de entrada/saída.
- CT01–CT14 escritos **até o dia 3** — antes do código existir, para não enviesar o teste pela
  implementação.
- Manter a matriz de cobertura: **toda RN01–RN15 com pelo menos um caso negativo**.
- Executar os CTs e preencher o relatório de execução.
- Abrir Issue de bug com o template, com severidade e evidência.

**Felipe — CI/CD, exploratório e evidências**

- Pipeline com quatro jobs (`backend`, `frontend`, `docker`, `quality-gate`). O job `docker` roda
  o seed **duas vezes** para provar a idempotência do
  [ADR-004](ADR-004-Bootstrap-do-Atendente).
- Quatro sessões exploratórias (EXP-01 a EXP-04) com charter e registro.
- Organizar `docs/evidencias/` conforme a §7 do plano de testes.
- Relatório final de testes para a apresentação.

---

## Roteiro dos slides

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
| 12 | Pipeline de CI (print do quality gate verde **e** de um PR bloqueado) |
| 13 | **Demonstração ao vivo** |
| 14 | Métricas: 32 testes automatizados, 14 CTs, CI verde |
| 15 | Retrospectiva: o que funcionou, o que faríamos diferente |

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

| Exigência do enunciado | Responsável | Entregue em | Status |
|---|---|---|---|
| PO: escrita e documentação | Uanderson | `docs/00`, `01`, `02` + Wiki | ✅ estrutura pronta |
| PO: ciclo de desenvolvimento | Uanderson | `docs/11` | ✅ |
| PO: verificar critérios de aceite | Uanderson | Board + ata da Review | ⬜ durante as sprints |
| PO: material de slide | Ronaldo | `docs/apresentacao/` | ⬜ Sprint 2 |
| ENG: Git Flow e repositório | Antonio | `docs/10` + branch protection | ✅ documentado |
| ENG: arquitetura MVC documentada | Jonatha | `docs/03` + `backend/app/` | ✅ |
| ENG: 3 práticas de Clean Code | Jonatha | `docs/05` | ✅ |
| ENG: 2 padrões de projeto | Jonatha | `docs/06` + [ADR-006](ADR-006-Design-Patterns) | ✅ |
| ENG: 5 testes unitários | João Vitor | `backend/tests/unit/` | ✅ **17 entregues** |
| QA: plano de testes | Jackson | `docs/07` | ✅ |
| QA: 10 casos de teste | Jackson | `docs/08` | ✅ **14 entregues** |
| QA: exploratório + evidências | Felipe | `docs/07` §6 + `docs/evidencias/` | ⬜ durante as sprints |
| QA: CI no GitHub Actions | Felipe | `.github/workflows/ci.yml` | ✅ |
| Quadro Kanban | Ronaldo | [GitHub Projects](https://github.com/users/jacksoncassemiro/projects/3) | ⬜ popular com `scripts/popular-board.sh` |
| Cronograma | Uanderson | `docs/12-cronograma.md` | ✅ |


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
