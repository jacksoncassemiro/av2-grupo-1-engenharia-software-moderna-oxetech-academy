# Como rodar o projeto

Guia único para subir o sistema na sua máquina. Escrito para **Windows**, que é o que a maior
parte da equipe usa, com as variações de Linux e macOS marcadas.

Tudo roda **localmente**. O GitHub hospeda só código, Wiki, board e CI — não há deploy.

> **Se algo não funcionar**, vá direto para a §5 (problemas conhecidos). Cole o log na issue
> `[INFRA] Validar a execução local do frontend em todas as máquinas` em vez de resolver sozinho:
> se aconteceu com você, vai acontecer com mais gente.

---

## 1. O que você precisa instalar

| Ferramenta | Para quê | Como instalar (Windows) |
|---|---|---|
| **Docker Desktop** | Subir banco, API e web | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| **Git** | Clonar o repositório | `winget install --id Git.Git` |
| **Python 3.12+** | Scripts de board e wiki | `winget install --id Python.Python.3.12` |
| **GitHub CLI** | Scripts de board | `winget install --id GitHub.cli` |

**Node e yarn não são obrigatórios** se você usar Docker. Só precisa deles para rodar o
frontend fora do container (§4).

Confira que o Docker está de pé antes de continuar:

```bash
docker --version
docker compose version
```

Se o segundo comando falhar, abra o Docker Desktop e espere o ícone da baleia ficar estável.

---

## 2. Subir tudo (caminho recomendado)

```bash
git clone https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy.git
cd av2-grupo-1-engenharia-software-moderna-oxetech-academy
```

**Copie o `.env`** — não precisa editar nada:

```powershell
copy .env.example .env          # Windows (PowerShell ou CMD)
```

```bash
cp .env.example .env            # Linux, macOS, Git Bash
```

**Suba, migre e popule:**

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seeds.seed
```

O primeiro `up --build` demora — ele baixa Python, Node e PostgreSQL e instala as dependências.
Cinco a dez minutos na primeira vez é normal. Nas seguintes, segundos.

Se você tem `make` (Git Bash, WSL, Linux, macOS), os três comandos viram um:

```bash
make bootstrap
```

### Onde as coisas ficam

| Serviço | URL |
|---|---|
| **Frontend** | http://localhost:3000 |
| API — Swagger | http://localhost:8000/docs |
| API — ReDoc | http://localhost:8000/redoc |
| Health check | http://localhost:8000/health |
| PostgreSQL | `localhost:5433` (usuário `clinica`, senha `clinica`) |

**Login inicial (atendente):** `recepcao@clinica.com` / `admin123`
Vem do seed. É o único atendente que existe — não há tela de cadastro de atendente no MVP
(RN14 e MF02).

### Confirme que subiu

```bash
docker compose ps
```

Você deve ver **três** containers `running`: `clinica_db`, `clinica_api` e `clinica_web`.
Se `clinica_web` não aparecer ou estiver `exited`, vá para a §5.

---

## 3. Comandos do dia a dia

```bash
docker compose logs -f frontend        # acompanhar os logs do Next
docker compose logs -f backend         # acompanhar os logs do FastAPI
docker compose restart frontend        # reiniciar só o web
docker compose down                    # derrubar (mantém os dados)
docker compose down -v                 # derrubar e APAGAR o banco
```

**Testes e lint** (rodam dentro dos containers, com as mesmas versões do CI):

```bash
docker compose exec backend pytest --cov=app --cov-report=term-missing
docker compose exec frontend yarn test
docker compose exec backend ruff check .
docker compose exec frontend yarn lint
docker compose exec frontend yarn typecheck
```

**Nova migração** depois de mexer em `backend/app/models/`:

```bash
docker compose exec backend alembic revision --autogenerate -m "cria tabela x"
```

⚠️ **Sempre revise a migração gerada à mão.** O autogenerate não cria índice parcial — e o
`uq_slot_ativo` da RN03 é exatamente um índice parcial. `backend/tests/integration/test_migracoes.py`
falha no PR se o model e a migração divergirem.

**Novas dependências do frontend** exigem rebuild da imagem:

```bash
docker compose exec frontend yarn add <pacote>
docker compose up -d --build frontend
```

---

## 4. Rodar o frontend fora do Docker

Útil quando o hot reload dentro do container fica lento — o que acontece no Windows, porque o
`WATCHPACK_POLLING` faz o Next verificar arquivos em laço.

**Suba só o banco e a API no Docker:**

```bash
docker compose up -d postgres backend
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seeds.seed
```

**Rode o Next na sua máquina:**

```bash
cd frontend
corepack enable                    # habilita o yarn 1.22.22 do campo packageManager
yarn install --frozen-lockfile
yarn dev
```

> ⚠️ **Use `yarn`, nunca `npm` nem `pnpm`.** O `yarn.lock` está versionado e é o mesmo que o CI
> usa. Rodar `npm install` gera um `package-lock.json` e uma árvore de dependências diferente —
> o que funciona na sua máquina e quebra no CI. Se você já rodou `npm install` por engano:
> apague `node_modules/` e `package-lock.json`, e rode `yarn install --frozen-lockfile`.

Neste modo o Next proxeia `/api` para `http://localhost:8000`, que é o valor padrão de
`BACKEND_INTERNAL_URL` no `next.config.mjs`. Nada a configurar.

---

## 5. Problemas conhecidos

### O container `frontend` não sobe

```bash
docker compose logs frontend --tail 50
```

| Log contém | Causa | Solução |
|---|---|---|
| `dependency failed to start` | O `backend` não ficou saudável, e o `frontend` depende dele | `docker compose logs backend` — normalmente é o banco. Veja o item seguinte |
| `Cannot find module` | O volume `node_modules` ficou de uma build antiga | `docker compose down -v && docker compose up -d --build` |
| `EADDRINUSE :::3000` | Algo já usa a porta 3000 | Feche o outro processo, ou mude para `"3001:3000"` no `docker-compose.yml` |
| `Corepack ... signature` | Corepack não conseguiu baixar o yarn | Rebuild com rede estável: `docker compose build --no-cache frontend` |

### O `backend` fica reiniciando

Quase sempre é o banco não estar pronto ou o `.env` faltar.

```bash
docker compose logs backend --tail 30
```

| Log contém | Solução |
|---|---|
| `relation "usuario" does not exist` | Falta migrar: `docker compose exec backend alembic upgrade head` |
| `could not connect to server` | O postgres ainda subia. Espere 20s e `docker compose restart backend` |
| `ValidationError ... JWT_SECRET_KEY` | O `.env` não foi criado. `cp .env.example .env` e suba de novo |

### A tela abre mas toda chamada de API falha

Abra o DevTools (F12) → aba Network. Se as requisições para `/api/...` derem **404** ou
**502**, o proxy do Next não alcançou o backend.

- Dentro do Docker: `BACKEND_INTERNAL_URL` precisa valer `http://backend:8000` — é o que o
  `docker-compose.yml` define. Confira com
  `docker compose exec frontend printenv BACKEND_INTERNAL_URL`
- Fora do Docker: o backend precisa estar em `http://localhost:8000`. Teste com
  `curl http://localhost:8000/health`

### Porta 5433 ocupada

O compose expõe o PostgreSQL em **5433** justamente para não brigar com um Postgres local na
5432. Se 5433 também estiver ocupada, mude `POSTGRES_PORT` no `.env`.

### `Python was not found; run without arguments to install from the Microsoft Store`

O Windows instala um **atalho falso** em `%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe`.
Ele aparece no PATH, o PowerShell o encontra, mas ao executar ele só abre a loja. É o
*App Execution Alias*.

Diagnostique:

```powershell
py -3 --version          # se responder "Python 3.x.y", está tudo certo
where.exe python         # se apontar para WindowsApps, é o atalho falso
```

Resolva de um dos dois jeitos:

```powershell
# a) instalar o Python de verdade (recomendado)
winget install --id Python.Python.3.12
# feche e abra o terminal, depois confira:  py -3 --version

# b) desligar o atalho falso
# Configurações > Aplicativos > Configurações avançadas de aplicativos
# > Aliases de execução de aplicativo  ->  desligue python.exe e python3.exe
```

**Python é obrigatório?** Só para o **board** e para **gerar** a Wiki. Para rodar o sistema
(Docker), para publicar a Wiki (`publicar-wiki`, que usa só git) e para criar as labels
(`criar-labels`, que usa só `gh`), não é preciso.

### `syntax error near unexpected token $'do\r'` ao rodar um `.sh`

Fim de linha **CRLF**. O Git no Windows converte LF → CRLF no checkout, e o bash lê o `\r` como
parte do comando.

```powershell
git add --renormalize .
git checkout -- scripts/
py -3 scripts\verificar-sintaxe.py
```

O `.gitattributes` já força `eol=lf` para `*.sh` e `crlf` para `*.ps1`; o `--renormalize` é o que
manda o Git aplicar isso ao que já está no disco.

### Os scripts `.ps1` não fazem nada no Windows

Duas causas, ambas silenciosas:

1. **Você rodou o `.sh` no PowerShell.** PowerShell não executa shell script. Use o `.ps1`.
2. **A política de execução bloqueia.** Libere só para a sessão atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Ou invoque sem alterar política nenhuma:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\popular-board.ps1 -Auditar
```

Se rodar com `-Verbose` e não sair **nada**, é a política de execução.

### O `yarn build` falha com "Element type is invalid ... got: undefined"

É o erro mais traiçoeiro do projeto: **compound component do Mantine em Server Component**.

`List.Item`, `Table.Thead`, `Popover.Target` e afins não atravessam a fronteira RSC —
propriedades estáticas chegam como `undefined`. O erro **não** aparece no `tsc`, nem no ESLint,
nem no Vitest. Só no `next build`.

Duas soluções:

```tsx
// 1. Marcar o componente como client
'use client';
import { List } from '@mantine/core';

// 2. Ou usar o import nomeado
import { List, ListItem } from '@mantine/core';
```

`frontend/__tests__/server-components.test.ts` é a guarda que antecipa isso no `yarn test`.

### Reset completo

Quando nada mais explica:

```bash
docker compose down -v
docker system prune -f
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seeds.seed
```

`down -v` **apaga o banco**. É seguro: o seed recria o atendente e as especialidades base, e é
idempotente (pode rodar quantas vezes quiser).

---

## 6. Checklist do primeiro encontro (31/07)

Cada uma das 6 pessoas precisa marcar tudo isto antes de pegar a primeira tarefa:

- [ ] `docker compose ps` mostra `clinica_db`, `clinica_api` e `clinica_web` como `running`
- [ ] `http://localhost:3000` abre a página inicial
- [ ] `http://localhost:8000/docs` abre o Swagger
- [ ] Login com `recepcao@clinica.com` / `admin123` funciona pelo Swagger
- [ ] `docker compose exec backend pytest` passa
- [ ] `docker compose exec frontend yarn test` passa
- [ ] `git checkout -b feature/teste && git push -u origin feature/teste` funciona (e depois
      apague a branch)

Quem travar em algum item **avisa no grupo na hora**. Ambiente quebrado no dia 1 custa a sprint
inteira, e temos 11 dias.

---

## 7. Nota sobre o CI

O job `docker` do CI sobe **apenas `postgres` e `backend`** — ele valida migração e seed, não a
imagem do frontend. Isso significa que um problema exclusivo do container `clinica_web` **passa
pelo CI sem ser detectado**.

O que cobre esse buraco hoje: os jobs `frontend` (lint, typecheck, Vitest e `yarn build` fora do
Docker) e o checklist da §6, feito por 6 pessoas em máquinas diferentes.

Está registrado como melhoria de pipeline na issue
`[INFRA] Validar o pipeline de CI com os quatro jobs`. Se sobrar tempo, adicionar
`docker compose build frontend` ao job `docker` fecha a lacuna com uma linha.
