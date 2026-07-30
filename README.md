# 🏥 Sistema de Gestão de Clínica Médica (MVP)

**AV2 — Engenharia de Software Moderna · Oxetech Academy · Equipe 01**

Substitui o agendamento por telefone e planilhas de uma clínica médica por um sistema web com
as regras de integridade garantidas no próprio banco de dados.

[![CI](https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy/actions/workflows/ci.yml/badge.svg)](https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy/actions/workflows/ci.yml)

---

## 🚀 Rodar em 3 comandos

Requisitos: **Docker** e **Docker Compose**. Nada mais.

```bash
git clone git@github.com:jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy.git
cd av2-grupo-1-engenharia-software-moderna-oxetech-academy
cp .env.example .env        # não precisa editar nada
make bootstrap              # sobe + migra + seed
```

| Serviço | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API (Swagger) | http://localhost:8000/docs |
| API (ReDoc) | http://localhost:8000/redoc |
| PostgreSQL | `localhost:5433` |

**Login inicial (atendente):** `recepcao@clinica.com` / `admin123`

Sem `make` (Windows sem Git Bash/WSL):

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seeds.seed
```

<details>
<summary>Rodar o backend fora do Docker</summary>

```bash
docker compose up -d postgres
cd backend
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements-dev.txt
alembic upgrade head
python -m app.seeds.seed
uvicorn app.main:app --reload
```
</details>

<details>
<summary>Rodar o frontend fora do Docker</summary>

```bash
cd frontend
yarn install     # comite o yarn.lock gerado
yarn dev
```
</details>

---

## 👥 Equipe

| Papel | Pessoa | Foco |
|---|---|---|
| 👑 **Product Owner** | Uanderson Henrique Batista da Silva | Backlog, User Stories, critérios de aceite, ciclo de desenvolvimento |
| 💻 **Engenharia** | Jonatha da Silva Fernandes | Arquitetura MVC, Clean Code, Design Patterns |
| 💻 **Engenharia** | Antonio Andrade Gomes Júnior | Git Flow, autenticação, autorização, seed |
| 💻 **Engenharia** | João Vitor Mandu de Lira | Frontend Next.js + Mantine, testes unitários |
| 💻 **Engenharia** | Ronaldo de Melo Sabino Filho | Frontend, cerimônias Scrum, apresentação |
| 🧪 **QA** | Jackson Douglas da Silva Cassemiro | Plano e casos de teste, execução, evidências |
| 🧪 **QA** | Felipe da Silva Araújo | CI/CD, testes exploratórios, relatório final |

Alocação detalhada de cada entregável avaliado em
[`docs/13-papeis-e-responsabilidades.md`](docs/13-papeis-e-responsabilidades.md).

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2.0 · Alembic |
| Banco | PostgreSQL 16 |
| Frontend | Next.js (App Router) · React · TypeScript · **Mantine v9** |
| Pacotes (front) | **yarn** |
| Testes | pytest (backend) · **Vitest** + React Testing Library (frontend) |
| CI | GitHub Actions |
| Ambiente | Docker Compose |

---

## 🏗️ Arquitetura

Monólito modular em camadas, com o MVC mapeado assim:

```
View (Next.js) → Controller (routers) → Service → Repository → Model → PostgreSQL
```

A dependência é **sempre para dentro**: o Service não conhece HTTP nem SQL, o que torna as
regras de negócio testáveis sem banco. Diagramas e contratos em
[`docs/03-arquitetura.md`](docs/03-arquitetura.md).

```
backend/app/
├── core/           config · database · security (bcrypt + JWT) · deps (autorização)
├── models/         entidades + constraints das regras de negócio
├── schemas/        DTOs Pydantic (validação de formato)
├── repositories/   ── Design Pattern 2: Repository
├── services/       regra de negócio · cancelamento_strategy.py ── Design Pattern 1: Strategy
├── routers/        Controllers
├── exceptions/     exceções de domínio + handler HTTP
└── seeds/          bootstrap idempotente

frontend/src/
├── app/            App Router · (paciente) e (atendente) com guarda por perfil
├── components/     componentes Mantine reutilizáveis
├── lib/            api.ts (cliente HTTP único) · cpf.ts (RN07)
└── theme.ts        tema Mantine da clínica
```

### Design Patterns

| # | Padrão | Onde | Problema resolvido |
|---|---|---|---|
| 1 | **Strategy** | `services/cancelamento_strategy.py` | A regra de cancelamento muda por perfil — sem Strategy seria `if perfil ==`, violando OCP |
| 2 | **Repository** | `repositories/` | Isola SQLAlchemy das regras — é o que permite 17 testes unitários em ~3s sem banco |

Justificativa completa, diagramas e alternativas recusadas em
[`docs/06-design-patterns.md`](docs/06-design-patterns.md).

### Clean Code

1. **Nomes significativos** — `verificar_disponibilidade_horario()`, `StatusConsulta.CANCELADA`,
   zero número mágico
2. **Funções pequenas com responsabilidade única** — método público orquestra, `_privados` fazem
   uma coisa cada; nenhum método passa de 12 linhas
3. **Exceções tipadas em vez de códigos de erro** — `raise CpfDuplicado`, nunca `return -1`

Com exemplos ruim/bom e SOLID em [`docs/05-clean-code.md`](docs/05-clean-code.md).

---

## ✨ Funcionalidades

### 👤 Paciente

- Ativar o primeiro acesso pelo CPF, **ou se auto-cadastrar** se ainda não tiver cadastro
- Atualizar seus dados cadastrais
- Consultar médicos disponíveis e especialidades oferecidas
- Visualizar horários realmente livres
- Solicitar consulta (nasce como `SOLICITADA`)
- Ver o histórico e os detalhes das próprias consultas
- Cancelar consulta respeitando as 24h de antecedência

### 👩‍💻 Atendente

- Cadastrar pacientes, médicos, especialidades e a grade de horários
- Agendar consultas para pacientes (nasce como `CONFIRMADA`)
- Confirmar e finalizar consultas
- Cancelar consultas sem restrição de prazo
- Cadastrar outros atendentes
- Gerenciar a agenda geral *(desejável)*

Detalhamento em [`docs/02-backlog.md`](docs/02-backlog.md).

---

## 📋 Regras de negócio

### Obrigatórias do enunciado

| ID | Regra | Garantida por |
|---|---|---|
| **RN01** | Bloqueio de paciente com CPF duplicado | `UNIQUE (cpf)` + validação no service |
| **RN02** | Bloqueio de usuário com e-mail duplicado | `UNIQUE` em e-mail/login (nulo é permitido) |
| **RN03** | Impedimento de reserva de horário ocupado | índice parcial `uq_slot_ativo` + `SELECT FOR UPDATE` |
| **RN04** | Cancelamento com no mínimo 24h de antecedência | Strategy `CancelamentoPorPaciente` |
| **RN05** | Bloqueio de alocação dupla do mesmo médico | `UNIQUE (medico_id, data, horario)` |
| **RN06** | Status SOLICITADA / CONFIRMADA / CANCELADA / FINALIZADA | `Enum` + máquina de estados |

### Adicionais definidas pela equipe

`RN07` CPF válido por dígitos verificadores · `RN08` e-mail em formato válido ·
`RN09` horário comercial 08:00–18:00 · `RN10` transições de status unidirecionais ·
`RN11` senha com hash bcrypt · `RN12` autorização por perfil no token ·
`RN13` expiração do JWT · `RN14` só ATENDENTE cria ATENDENTE ·
`RN15` regras temporais no fuso `America/Maceio`

Todas em [`docs/01-requisitos.md`](docs/01-requisitos.md), com matriz de rastreabilidade
requisito → código → teste → evidência.

---

## 🧪 Testes e qualidade

```bash
make test            # backend + frontend
make test-backend    # pytest --cov
make test-frontend   # vitest
make lint            # ruff + eslint + tsc
```

| Nível | Quantidade | Exigido | Onde |
|---|---|---|---|
| Unitário backend | **17** | 5 | `backend/tests/unit/` |
| Unitário frontend | 7 | — | `frontend/__tests__/` |
| Integração | **15** | — | `backend/tests/integration/` |
| Casos de teste funcionais | **14** | 10 | [`docs/08-casos-de-teste.md`](docs/08-casos-de-teste.md) |
| Sessões exploratórias | 4 | — | [`docs/07-plano-de-testes.md`](docs/07-plano-de-testes.md) §6 |

Toda regra RN01–RN15 tem no mínimo um teste que **viola** a regra e espera bloqueio — testar só
o caminho felizes não prova que a regra existe.

### CI — quatro jobs

| Job | Valida |
|---|---|
| `backend` | ruff · ruff format · alembic upgrade · pytest unit + integração + cobertura |
| `frontend` | eslint · tsc --noEmit · vitest --coverage · next build |
| `docker` | compose sobe · healthcheck · migração + checagem de revisão aplicada · **seed rodado 2× (prova a idempotência)** |
| `quality-gate` | Agrega os três — é o *required status check* de `main` e `develop` |

---

## 📚 Documentação

| Documento | Conteúdo |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Instruções para a equipe e para agentes de IA |
| [`docs/`](docs/README.md) | Índice completo da documentação |
| [`docs/14-conflitos-e-decisoes.md`](docs/14-conflitos-e-decisoes.md) | **13 divergências no enunciado e como resolvemos** |
| [`docs/adr/`](docs/adr/) | 7 Architecture Decision Records |
| [Wiki](https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy/wiki) | Espelho navegável da documentação |
| [Projects](https://github.com/users/jacksoncassemiro/projects/3) | Quadro Kanban |

### Destaque para o avaliador

O documento [`docs/14-conflitos-e-decisoes.md`](docs/14-conflitos-e-decisoes.md) analisa as
divergências entre o texto do Case, a lista de funcionalidades e o backlog — e registra as
decisões. Os achados mais relevantes:

- **O Case pede que o paciente se cadastre; a lista dá o cadastro só ao atendente.** Resolvido
  fazendo os dois caminhos convergirem em um endpoint ([ADR-005](docs/adr/ADR-005-cadastro-paciente.md)).
- **Nada no enunciado diz de onde vem o primeiro atendente** — sem ele o sistema recém-instalado
  é inutilizável. Resolvido com seed idempotente + RN14 ([ADR-004](docs/adr/ADR-004-bootstrap-atendente.md)).
- **Um `UNIQUE` simples no slot travaria o horário para sempre após o primeiro cancelamento**,
  quebrando a US-11. Resolvido com índice parcial ([ADR-006](docs/adr/ADR-006-design-patterns.md)).
- **Nenhuma User Story levava a consulta a CONFIRMADA ou FINALIZADA**, o que deixaria a RN06 sem
  cobertura. Resolvido criando a US-13.

---

## 🔀 Git Flow

```
main ← release/* ← develop ← feature/* | fix/* | docs/*
```

Conventional Commits em português, PR obrigatório com 1 aprovação e `quality-gate` verde.
Convenções e checklist de code review em [`docs/10-git-flow.md`](docs/10-git-flow.md).

---

## 🤖 Trabalhando com IA

O repositório traz [`CLAUDE.md`](CLAUDE.md) e quatro skills em [`.claude/skills/`](.claude/skills/):

| Skill | Para |
|---|---|
| `clinica-backend` | Endpoints, regras de negócio, models, migrações, pytest |
| `clinica-frontend` | Telas Next.js + Mantine, formulários, Vitest |
| `clinica-qa` | Plano e casos de teste, exploratório, evidências, CI |
| `clinica-fluxo-git` | Branch, commit, PR, code review, board |

Assim os seis membros produzem código com o mesmo padrão, independente da ferramenta de IA que
usarem. Para dúvidas de API do Mantine: `https://mantine.dev/llms.txt`.

---

## 📁 Estrutura

```
.
├── CLAUDE.md                 instruções do projeto
├── Makefile                  bootstrap · test · lint · seed
├── docker-compose.yml        postgres + backend + frontend
├── .env.example              copiar-e-rodar
├── backend/                  FastAPI + SQLAlchemy + Alembic
├── frontend/                 Next.js + TypeScript + Mantine
├── docs/                     documentação + ADRs + material das aulas
├── wiki/                     espelho do Wiki do GitHub
├── scripts/                  publicar wiki · popular board (.ps1 e .sh)
├── .claude/skills/           skills de projeto para IA
└── .github/                  CI, templates de PR e Issue
```

---

## 🪟 Windows

A maioria da equipe está no Windows. Os scripts de automação têm versão **PowerShell**:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   # 1x por sessão

.\scripts\popular-board.ps1 -Auditar     # audita o Kanban antes de mexer
.\scripts\criar-labels.ps1               # labels dos templates de Issue
.\scripts\publicar-wiki.ps1 -DryRun      # publica a Wiki
python scripts\gerar-wiki.py              # regenera wiki/ a partir de docs/
```

Rodar o `.sh` no PowerShell **não faz nada** — e sem o `Set-ExecutionPolicy` o `.ps1` falha em
silêncio. Detalhes e solução de problemas em [`scripts/README.md`](scripts/README.md).

Para `make`, use Git Bash ou WSL. Sem `make`, os comandos Docker equivalentes estão no início
deste README.

---

## 📖 Comandos

```bash
make help          # lista tudo
make bootstrap     # up + migrate + seed
make up / down     # sobe / derruba
make reset         # derruba e APAGA o volume do banco
make logs          # segue os logs
make migrate       # aplica migrações
make migration m="cria tabela x"
make seed          # idempotente
make test / lint
```
