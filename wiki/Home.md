# 🏥 Sistema de Gestão de Clínica Médica (MVP)

**AV2 — Engenharia de Software Moderna · Oxetech Academy · Equipe 01**

Substitui o agendamento por telefone e planilhas de uma clínica médica por um sistema web com
as regras de integridade garantidas no próprio banco de dados.

| | |
|---|---|
| 📦 **Repositório** | [av2-grupo-1-engenharia-software-moderna-oxetech-academy](https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy) |
| 📋 **Quadro Kanban** | [Projects #3](https://github.com/users/jacksoncassemiro/projects/3) |
| ⚙️ **Pipeline** | [Actions](https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy/actions) |
| 🗓️ **Entrega** | **10/08/2026** · 2 sprints (31/07–05/08 e 05/08–10/08) |

---

## Por onde começar

| Se você é… | Comece por |
|---|---|
| **novo na equipe** | [Como Rodar](Como-Rodar) → [Visão do Produto](Visao-do-Produto) → [Arquitetura](Arquitetura) → [Git Flow](Git-Flow) |
| **avaliador** | [ADR-008 Rebaseline](ADR-008-Rebaseline-de-Escopo) → [Conflitos e Decisões](Conflitos-e-Decisoes) → [Clean Code](Clean-Code-e-SOLID) → [Design Patterns](Design-Patterns) |
| **PO** | [Requisitos](Requisitos) → [Backlog](Backlog-e-User-Stories) → [Ciclo de Desenvolvimento](Ciclo-de-Desenvolvimento) |
| **Engenharia** | [Arquitetura](Arquitetura) → [Modelo de Dados](Modelo-de-Dados) → [ADRs](ADR-001-Monorepo) |
| **QA** | [Plano de Testes](Plano-de-Testes) → [Casos de Teste](Casos-de-Teste) → [CI/CD](CI-CD) |

---

## Rodar o projeto

```bash
git clone https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy.git
cd av2-grupo-1-engenharia-software-moderna-oxetech-academy
cp .env.example .env                 # não precisa editar nada
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seeds.seed
```

Frontend em `localhost:3000` · Swagger em `localhost:8000/docs`
Login inicial: `recepcao@clinica.com` / `admin123`

🆘 **Travou?** [Como Rodar](Como-Rodar) tem o guia para Windows, os problemas conhecidos e o
checklist de ambiente.

---

## Índice

### Produto

- **[Visão do Produto](Visao-do-Produto)** — problema, escopo dentro/fora, proposta de valor, métricas, riscos
- **[Requisitos](Requisitos)** — RF01–RF22, RNF01–RNF15, RN01–RN15 e matriz de rastreabilidade
- **[Backlog e User Stories](Backlog-e-User-Stories)** — US-00 a US-13 com critérios de aceite em Gherkin
- **[Melhorias Futuras](Melhorias-Futuras)** — o que ficou fora do MVP, com motivo e versão-alvo

### Engenharia

- **[Arquitetura](Arquitetura)** — **duas aplicações**: MVC do backend (§2), arquitetura do frontend (§3), contrato entre elas (§4)
- **[Modelo de Dados](Modelo-de-Dados)** — ER, constraints por regra, migrações, SQL de verificação
- **[Clean Code e SOLID](Clean-Code-e-SOLID)** — 3 práticas com ruim/bom nas duas stacks
- **[Design Patterns](Design-Patterns)** — Strategy e Repository (backend) com diagramas e alternativas
- **[Git Flow](Git-Flow)** — branches, commits, PR, code review, release, board
- **[Como Rodar](Como-Rodar)** — subir o projeto, comandos do dia a dia, problemas conhecidos

### Qualidade

- **[Plano de Testes](Plano-de-Testes)** — pirâmide, escopo, exploratório, defeitos, critérios de saída
- **[Casos de Teste](Casos-de-Teste)** — CT01–CT14 e o mapa dos testes unitários
- **[CI/CD](CI-CD)** — quatro jobs, quality gate, troubleshooting

### Processo

- **[Ciclo de Desenvolvimento](Ciclo-de-Desenvolvimento)** — Scrum + Kanban, cerimônias, DoR/DoD, métricas
- **[Cronograma](Cronograma)** — calendário 31/07 a 10/08, 2 sprints por encontro, marcos, priorização
- **[Papéis e Responsabilidades](Papeis-e-Responsabilidades)** — equipe de 6 e entregáveis por pessoa

### Análise e decisões

- **[Conflitos e Decisões](Conflitos-e-Decisoes)** — 13 divergências no enunciado e como resolvemos
- [ADR-001 — Monorepo](ADR-001-Monorepo)
- [ADR-002 — Camadas MVC](ADR-002-Camadas-MVC)
- [ADR-003 — Autenticação](ADR-003-Autenticacao)
- [ADR-004 — Bootstrap do Atendente](ADR-004-Bootstrap-do-Atendente)
- [ADR-005 — Cadastro de Paciente](ADR-005-Cadastro-de-Paciente)
- [ADR-006 — Design Patterns](ADR-006-Design-Patterns)
- [ADR-007 — Vitest](ADR-007-Vitest)
- [**ADR-008 — Rebaseline de Escopo**](ADR-008-Rebaseline-de-Escopo)

---

## Resumo do MVP

### Perfis

**👤 Paciente** — ativa o primeiro acesso pelo CPF ou se auto-cadastra · atualiza seus dados ·
consulta médicos e especialidades · vê horários livres · solicita consulta · vê o histórico ·
cancela respeitando as 24h

**👩‍💻 Atendente** — cadastra pacientes, médicos, especialidades e a grade de horários ·
agenda consultas · confirma e finaliza · cancela sem restrição de prazo

> **Escopo congelado:** 14 User Stories (US-00 a US-13) — as 13 funcionalidades do enunciado
> mais autenticação. O que ficou de fora está em [Melhorias Futuras](Melhorias-Futuras), com
> motivo e versão-alvo. Justificativa: [ADR-008](ADR-008-Rebaseline-de-Escopo).

### Regras de negócio

| Obrigatórias do enunciado | | Adicionais da equipe | |
|---|---|---|---|
| RN01 | CPF único | RN07 | CPF válido por dígitos verificadores |
| RN02 | E-mail único | RN08 | E-mail em formato válido |
| RN03 | Horário ocupado bloqueado | RN09 | Horário comercial 08:00–18:00 |
| RN04 | Cancelamento com 24h | RN10 | Transições de status unidirecionais |
| RN05 | Sem alocação dupla de médico | RN11 | Senha com hash bcrypt |
| RN06 | Gestão dos 4 status | RN12 | Autorização por perfil no token |
| | | RN13 | Expiração do JWT |
| | | RN14 | Sem rota pública de cadastro de atendente |
| | | RN15 | Regras temporais em `America/Maceio` |

Detalhes em [Requisitos](Requisitos).

### Stack

Backend Python 3.12 + FastAPI + SQLAlchemy · PostgreSQL 16 ·
Frontend Next.js App Router + TypeScript + Mantine v9 (yarn) ·
Testes pytest + Vitest · CI GitHub Actions · Docker Compose

### Números

| | Entregue | Exigido |
|---|---|---|
| Testes unitários backend | **17** | 5 |
| Testes unitários frontend | **11** | 5 |
| Testes de integração | **11** | — |
| Casos de teste funcionais | **14** | 10 |
| Práticas de Clean Code | **3** por stack | 3 |
| Design Patterns (backend) | **2** | 2 |
| ADRs | 8 | — |

---

## Destaque: análise do enunciado

O documento [Conflitos e Decisões](Conflitos-e-Decisoes) confronta três fontes — o texto do
Case, a lista de funcionalidades e o backlog — e registra 13 divergências com a resolução de
cada uma. Os achados mais relevantes:

1. **O Case pede que o paciente se cadastre; a lista dá o cadastro só ao atendente.**
   Resolvido fazendo os dois caminhos convergirem em um endpoint —
   [ADR-005](ADR-005-Cadastro-de-Paciente).
2. **Nada no enunciado diz de onde vem o primeiro atendente**, e sem ele o sistema
   recém-instalado é inutilizável. Resolvido com seed idempotente + RN14 —
   [ADR-004](ADR-004-Bootstrap-do-Atendente).
3. **Um `UNIQUE` simples no slot travaria o horário para sempre após o primeiro
   cancelamento**, quebrando a US-11. Resolvido com índice parcial —
   [ADR-006](ADR-006-Design-Patterns).
4. **Nenhuma User Story levava a consulta a CONFIRMADA ou FINALIZADA**, o que deixaria a RN06
   sem cobertura. Resolvido criando a US-13.
5. **O planejamento inicial inflou para 82 itens** e não cabia no prazo real. Resolvido com um
   rebaseline documentado — [ADR-008](ADR-008-Rebaseline-de-Escopo).

---

> 📄 Esta wiki é gerada a partir de `docs/` no repositório.
> **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
