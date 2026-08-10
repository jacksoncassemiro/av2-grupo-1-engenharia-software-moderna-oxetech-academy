# CLAUDE.md — Instruções do projeto

Contexto para qualquer agente de IA (Claude Code, Cowork, Antigravity, Copilot) que trabalhe neste repositório.
**Leia isto antes de escrever código.**

---

## 1. O que é este projeto

MVP de um **Sistema de Gestão de Clínica Médica**, entrega da **AV2** da disciplina
*Engenharia de Software Moderna* (Oxetech Academy) — **Equipe 01** (7 pessoas).
**Entrega: 10/08/2026.** Duas sprints curtas: 31/07–05/08 e 05/08–10/08.

**Escopo congelado** pelo [ADR-008](docs/adr/ADR-008-rebaseline-escopo.md): 14 User Stories
(US-00 a US-13) — as 13 funcionalidades dos dois perfis do enunciado mais autenticação.
Nada além disso entra sem aprovação do PO. O que ficou de fora está em
`docs/15-melhorias-futuras.md` com motivo e versão-alvo.

O projeto é avaliado pela **aplicação dos conceitos**, não pela quantidade de features.
Toda decisão técnica precisa ser justificável a partir dos módulos do curso
(`docs/material-aulas/`): Clean Code, SOLID, Design Patterns, Arquitetura em Camadas (MVC), CI/CD.

Idioma: **português** em domínio, código, commits, documentação e comentários.
Sem acentos em identificadores de código; com acentos em documentação e textos de UI.

---

## 2. Stack fixa (não trocar sem ADR)

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic |
| Banco | PostgreSQL 16 |
| Frontend | Next.js (App Router) + React + TypeScript + **Mantine v9** |
| Gerenciador de pacotes (front) | **yarn** (nunca npm/pnpm) |
| Testes backend | pytest + fakes de repositório |
| Testes frontend | **Vitest** + React Testing Library |
| CI | GitHub Actions |
| Ambiente | Docker Compose |

---

## 3. Duas aplicações, não uma

O repositório é um monorepo, mas `backend/` e `frontend/` são **aplicações separadas**, com
stacks, builds e arquiteturas internas diferentes. Não misture o vocabulário das duas.

| | Backend | Frontend |
|---|---|---|
| Estilo arquitetural | **MVC em camadas** (é o MVC que a AV2 avalia) | Componentes + rotas do App Router |
| View | `app/schemas/` — DTOs Pydantic | JSX dos componentes |
| Testes | pytest | Vitest |

**O app React não é "a View do MVC".** Ele tem roteamento, estado e build próprios, e apenas
consome a API. O MVC se fecha dentro de `backend/`, com os schemas Pydantic no papel de View —
mesma leitura do Django REST Framework. Ver `docs/03-arquitetura.md` §2 e §3.

---

## 4. Estrutura do repositório

```
backend/          # FastAPI — camadas Model / Controller / Service / Repository
frontend/         # Next.js App Router + Mantine
docs/             # Toda a documentação + material das aulas + ADRs
  adr/            # Decisões arquiteturais registradas
  evidencias/     # Evidências de teste do QA
  material-aulas/ # PDFs/PPTX do curso (fonte para justificar decisões)
wiki/             # Espelho das páginas do Wiki do GitHub
scripts/          # Automação (publicar wiki, popular o board)
.claude/skills/   # Skills de projeto para agentes de IA
```

Não crie pastas novas na raiz. Não recrie `documentation/` — foi unificada em `docs/`.

---

## 5. Arquitetura em camadas do backend — a regra mais importante

O fluxo é **sempre** nesta ordem, e **nunca** salta uma camada:

```
Router (Controller)  →  Service  →  Repository  →  Model  →  PostgreSQL
```

| Camada | Pasta | Pode | Não pode |
|---|---|---|---|
| **Router** | `backend/app/routers/` | Receber requisição, injetar dependências, chamar 1 service, dar `db.commit()`, montar resposta | Conter `if` de regra de negócio, montar query, importar `select` |
| **Service** | `backend/app/services/` | Regra de negócio, orquestrar repositories, levantar exceções de domínio | Importar `fastapi`, `HTTPException`, `Session` ou `select` |
| **Repository** | `backend/app/repositories/` | Query SQLAlchemy, `flush()` | Conter regra de negócio, decidir status HTTP |
| **Model** | `backend/app/models/` | Colunas, relacionamentos, constraints | Ter lógica de aplicação |
| **Schema** | `backend/app/schemas/` | Validação de formato (Pydantic) | Consultar o banco |

**Teste rápido de violação:**
- `grep -r "HTTPException" backend/app/services/` → deve ser vazio
- `grep -r "select(" backend/app/services/` → deve ser vazio
- `grep -rE "^\s+if .*(status ==|perfil ==)" backend/app/routers/` → deve ser vazio

Se uma regra de negócio parece precisar de HTTP, ela pertence a uma exceção em
`backend/app/exceptions/dominio.py` — que já carrega o `status_code`.

---

## 6. Regras de negócio — sempre referencie o ID

Toda regra tem um ID (`RN01`…`RN15`). Ao implementar ou testar uma regra, **cite o ID em comentário**
e no nome do teste. Isso é o que dá rastreabilidade requisito → código → teste → evidência.

Lista canônica: `docs/01-requisitos.md`. Resumo:

| ID | Regra |
|---|---|
| RN01 | CPF único por paciente |
| RN02 | E-mail único (quando não nulo) |
| RN03 | Slot já ocupado não pode ser reservado |
| RN04 | Paciente só cancela com ≥ 24h de antecedência |
| RN05 | Médico não pode ter dois slots no mesmo dia/hora |
| RN06 | Status: SOLICITADA, CONFIRMADA, CANCELADA, FINALIZADA |
| RN07 | CPF válido (dígitos verificadores) |
| RN08 | E-mail em formato válido |
| RN09 | Agenda só em horário comercial (08:00–18:00) |
| RN10 | Transições de status são unidirecionais |
| RN11 | Senha armazenada com hash bcrypt |
| RN12 | Rota restrita por perfil do token |
| RN13 | JWT expira (24h no MVP) |
| RN14 | Só ATENDENTE cadastra ATENDENTE |
| RN15 | Regras temporais no fuso `America/Maceio` |

Nunca hardcode `24` para o prazo de cancelamento — use
`settings.CANCELAMENTO_ANTECEDENCIA_HORAS`.

---

## 7. Clean Code — as 3 práticas que a AV2 exige

Estas três são **entregáveis avaliados**. Aplique e não desfaça:

1. **Nomes significativos** — `verificar_disponibilidade_horario()`, não `ver_disp()`.
   Sem números mágicos: `StatusConsulta.CANCELADA`, nunca `status = 3`.
2. **Funções pequenas com responsabilidade única** — ideal 1–5 linhas, limite 20.
   O método público orquestra; os `_privados` fazem uma coisa cada.
   Padrão do projeto: `cadastrar()` chama `_garantir_cpf_inedito()` + `_garantir_email_inedito()`.
3. **Exceções tipadas em vez de códigos de erro** — `raise CpfDuplicado`, nunca
   `return None` / `return -1` / `return {"erro": ...}`.

SOLID complementar: **SRP** (um service por domínio) e **DIP** (services dependem de
`RepositorioBase`, injetado — por isso os testes usam fakes sem subir banco).

Detalhes e exemplos ruim/bom: `docs/05-clean-code.md`.

---

## 8. Design Patterns — os 2 escolhidos (backend)

Não introduza um terceiro padrão "porque é bonito". Estes dois são os avaliados:

1. **Strategy** — `backend/app/services/cancelamento_strategy.py`
   `CancelamentoPorPaciente` (valida RN04) vs. `CancelamentoPorAtendente` (não valida).
   Se você estiver escrevendo `if perfil == ...` para decidir uma regra, **está errado** —
   crie uma Strategy.
2. **Repository** — `backend/app/repositories/`
   Isola SQLAlchemy das regras. É o que torna os testes unitários possíveis sem banco.

Justificativa: `docs/06-design-patterns.md` e `docs/adr/ADR-006-design-patterns.md`.

---

## 9. Frontend — regras do Mantine

- **Mantine v9**, App Router. `MantineProvider` + `ColorSchemeScript` já estão em
  `src/app/layout.tsx` — não duplicar.
- Componentes Mantine **não funcionam em Server Components**. Página com componente
  interativo precisa de `'use client'` no topo.
- **Compound components (`List.Item`, `Popover.Target`, `Table.Thead`) NÃO funcionam em Server
  Component.** Propriedades estáticas não atravessam a fronteira RSC: chegam como `undefined` e
  o `next build` quebra no prerender com *"Element type is invalid ... got: undefined"*.
  O erro **não** aparece no `tsc`, nem no ESLint, nem no Vitest — só no build.
  Solução: `'use client'` no topo, **ou** import nomeado (`ListItem`, `PopoverTarget`).
  `frontend/__tests__/server-components.test.ts` é a guarda que antecipa isso para o `yarn test`.
- **Não instale outra biblioteca de UI** (Tailwind, MUI, shadcn). Estilo pontual: CSS Modules
  com `postcss-preset-mantine`, ou props do Mantine (`mt`, `p`, `c`).
- Formulários: `@mantine/form` (`useForm` com `validate`). Datas: `@mantine/dates` + `dayjs`.
  Feedback: `@mantine/notifications`. Confirmação: `@mantine/modals`.
- Chamadas HTTP: **sempre** via `src/lib/api.ts`. Nunca `fetch` direto em componente.
- Testes: importe `render` de `@test-utils` (traz o `MantineProvider`), nunca de
  `@testing-library/react` direto.
- **`next lint` não existe mais** (removido no Next 16, junto com a opção `eslint` do
  `next.config`). O lint roda pela CLI: `yarn lint` → `eslint .`, configurado em
  `eslint.config.mjs` com `eslint-config-next/core-web-vitals` + `/typescript` em flat config.
- **Formatação é do Prettier**, configurado em `frontend/.prettierrc` para o estilo que o código
  já usava (aspas simples, 100 colunas, `trailingComma: es5`). `yarn format` escreve,
  `yarn format:check` confere — e o CI **reprova o PR** se algo estiver fora. Ligue o
  *format on save* apontando para o Prettier, senão seu editor formata com outro padrão e o
  PR quebra. Exceções deliberadas ficam em `.prettierignore` ou com `// prettier-ignore`.
- `yarn typecheck` é `next typegen && tsc --noEmit`. O `next typegen` gera `next-env.d.ts` e os
  tipos de rota — sem ele o `tsc` falha no CI.
- **`params` e `searchParams` são `Promise` no Next 16** (a compatibilidade síncrona da v15 foi
  removida). Use os helpers gerados: `PageProps<'/consultas/[id]'>`, `LayoutProps<'/(paciente)'>`.
  Vale também para `cookies()`, `headers()`, `draftMode()`.
- Guarda de rota fica no `layout.tsx` do route group. **Não** crie `middleware.ts` — no Next 16
  virou `proxy.ts`, e não precisamos dele.
- Turbopack é o bundler padrão: não passe `--turbopack` em `dev`/`build`.
- Setup do Vitest é `vitest.setup.ts` (**TypeScript**, não `.mjs`) — é o que faz o `tsc` ver os
  tipos dos matchers do jest-dom (`toBeInTheDocument`, `toHaveAttribute`).

Consulta de dúvida de API do Mantine: `https://mantine.dev/llms.txt`.

---

## 10. Git Flow e commits

- Branches: `main` (protegida) ← `release/*` ← `develop` ← `feature/*` | `fix/*` | `docs/*`
- Nunca commite direto em `main` ou `develop`. Sempre PR com ≥ 1 aprovação e CI verde.
- Nome da branch: `feature/us08-solicitar-consulta`
- **Conventional Commits**, em português:
  ```
  feat(consulta): impede reserva de horario ja ocupado (RN03)
  fix(auth): normaliza CPF com mascara no login
  test(agenda): cobre bloqueio de alocacao dupla (RN05)
  docs(adr): registra escolha de Strategy para cancelamento
  refactor(paciente): extrai validacoes para metodos privados
  chore(ci): adiciona job de docker compose
  ```
- Todo PR referencia a US e as RNs (ver `.github/pull_request_template.md`).

---

## 11. Comandos

```bash
make bootstrap      # sobe tudo + migra + seed → sistema navegável
make test           # pytest + vitest
make lint           # ruff + eslint + tsc
make migration m="cria tabela consulta"
make seed           # idempotente, pode rodar quantas vezes quiser
```

**Windows sem `make`** (a maioria da equipe): use o Docker direto — ver README §"Rodar em 3
comandos". Os scripts de automação têm versão PowerShell: `scripts\*.ps1`. Antes de rodar:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Sem isso o `.ps1` falha **em silêncio** — e rodar o `.sh` no PowerShell também não faz nada.
Detalhes em `scripts/README.md`.

Frontend: http://localhost:3000 · Swagger: http://localhost:8000/docs
Login inicial: `recepcao@clinica.com` / `admin123` (do `.env`)

Guia completo de execução, com os problemas conhecidos: `docs/17-como-rodar.md`.

**Board (GitHub Projects):** a fonte dos itens é `scripts/gerar-board-itens.py`, que gera
`scripts/board-itens.json`. **Não edite o JSON à mão.**

```powershell
# Windows — os .ps1 localizam o Python sozinhos
.\scripts\gerar-board-itens.ps1
.\scripts\popular-board.ps1 -Auditar
.\scripts\popular-board.ps1 -Tudo -DryRun
.\scripts\popular-board.ps1 -Tudo
```

```bash
# Linux / macOS / Git Bash
python3 scripts/gerar-board-itens.py
python3 scripts/popular-board.py --auditar
python3 scripts/popular-board.py --tudo --dry-run
python3 scripts/popular-board.py --tudo
```

⚠️ **Windows:** se aparecer `Python was not found; run without arguments to install from the
Microsoft Store`, o que está no PATH é o atalho falso da loja, não o Python. Rode
`winget install --id Python.Python.3.12` e confira com `py -3 --version`.
Detalhes em `scripts/README.md`.

---

## 12. Coisas que NÃO fazer

- ❌ Criar rota pública de cadastro de atendente (RN14 — falha de segurança).
- ❌ Adicionar funcionalidade fora das US-00 a US-13. O escopo está congelado (ADR-008).
  Ideia nova vai para `docs/15-melhorias-futuras.md`, não para o código.
- ❌ Chamar o app React de "View do MVC" na documentação ou nos slides.
- ❌ Duplicar regra de negócio no frontend. As 24h da RN04 são calculadas no backend, que
  devolve `pode_cancelar`; o React só obedece.
- ❌ Usar `npm` ou `pnpm` no frontend.
- ❌ Adicionar biblioteca de UI além do Mantine.
- ❌ Colocar regra de negócio em router ou em componente React.
- ❌ Usar `Base.metadata.create_all()` — o esquema é gerenciado por Alembic.
- ❌ Criar model sem a migração correspondente. `alembic upgrade head` **passa em silêncio**
  quando `alembic/versions/` está vazia ou desatualizada — o erro só aparece depois, no seed,
  como `UndefinedTable: relation "usuario" does not exist`.
  `backend/tests/integration/test_migracoes.py` compara model × migração e falha no PR.
- ❌ Usar `next lint` (não existe no Next 16) ou `npm`/`pnpm` no frontend.
- ❌ Commitar `.env`, `node_modules/`, `.next/`, `coverage/`.
- ❌ Deletar ou reescrever ADRs existentes — para mudar de decisão, escreva um ADR novo
  que **supersede** o anterior.
- ❌ Inventar RN nova sem registrar em `docs/01-requisitos.md`.

---

## 13. Ao encerrar uma tarefa

1. `make lint && make test` passando.
2. Regras tocadas têm teste citando o ID (`RN0X`).
3. `docs/` atualizado se o comportamento mudou; migração revisada à mão se mexeu em model
   (o autogenerate não cria índice parcial).
4. Item movido no board (GitHub Projects) e PR aberto com o template preenchido.
5. A User Story só vai para UAT quando o fluxo funciona **ponta a ponta pela interface** —
   backend sem tela não conta (ADR-008 §2).
