---
name: clinica-fluxo-git
description: Aplica o Git Flow, padrao de commits, Pull Request e movimentacao do board Kanban do projeto da clinica. Use quando a tarefa envolver criar branch, escrever mensagem de commit, abrir ou revisar PR, fazer release, ou mover item no GitHub Projects deste projeto.
---

# Git Flow do projeto

## Branches

```
main       # produção, protegida — só recebe merge de release/* e hotfix/*
develop    # integração, protegida — base de todo trabalho
feature/*  # nova funcionalidade   → develop
fix/*      # correção de bug       → develop
docs/*     # só documentação       → develop
release/*  # estabilização         → main + develop
hotfix/*   # urgência em produção  → main + develop
```

Nome da branch: `<tipo>/us<NN>-<slug-curto>` — ex.: `feature/us08-solicitar-consulta`,
`fix/us11-fuso-cancelamento`, `docs/adr-strategy`.

Nunca commite direto em `main` ou `develop`. Sempre atualize a base antes de abrir PR:

```bash
git switch develop && git pull --ff-only
git switch -c feature/us08-solicitar-consulta
# ... trabalho ...
git switch develop && git pull --ff-only
git switch - && git rebase develop
git push -u origin feature/us08-solicitar-consulta
```

## Conventional Commits (em português)

```
<tipo>(<escopo>): <o que mudou, imperativo, minúsculo> (<RN>)
```

Tipos: `feat` `fix` `docs` `test` `refactor` `chore` `ci` `perf`
Escopos: `auth` `paciente` `medico` `especialidade` `agenda` `consulta` `ui` `ci` `docs` `infra`

```
feat(consulta): impede reserva de horario ja ocupado (RN03)
fix(auth): normaliza CPF com mascara no login
test(agenda): cobre bloqueio de alocacao dupla (RN05)
refactor(paciente): extrai validacoes para metodos privados
docs(adr): registra escolha de Strategy para cancelamento
ci: adiciona job de docker compose ao pipeline
```

Ruim: `ajustes`, `wip`, `correções finais`, `update`, `feat: várias coisas`.
Um commit = uma ideia. Se a mensagem precisa de "e", divida.

## Pull Request

Template em `.github/pull_request_template.md`. Obrigatório:
US referenciada, RNs cobertas, link do item do board, CI verde, ≥ 1 aprovação.

PR grande (> ~400 linhas) deve ser dividido. PR sem teste de RN nova é reprovado no review.

## Code review — o que olhar

1. Vazamento de camada (`HTTPException`/`select` em service; `if` de regra em router)
2. `if perfil ==` onde deveria haver Strategy
3. RN sem teste, ou teste sem o ID da RN no nome
4. Paciente agindo sobre id que não veio do token
5. Número mágico (24h, 08:00) hardcoded em vez de `settings` / constante
6. `any` no TypeScript, `fetch` direto em componente, falta de `'use client'`
7. `print` / `console.log` esquecido

Aprovar com `changesRequested` quando houver item 1–4; comentário simples para 5–7.

## Release

```bash
git switch -c release/1.0 develop
# ajustes finais, bump de versão, CHANGELOG
git switch main && git merge --no-ff release/1.0
git tag -a v1.0.0 -m "MVP - AV2 Equipe 01"
git switch develop && git merge --no-ff release/1.0
git push origin main develop --tags
```

## Board (GitHub Projects)

Colunas: **To Do → In Dev → Code Review → In QA → UAT → Done**

- Ao começar: mova para *In Dev* e se atribua. WIP máximo **2 itens por pessoa**.
- Ao abrir PR: mova para *Code Review*.
- Após o merge: *In QA* (QA executa o caso de teste e coleta evidência).
- Depois: *UAT* (PO percorre os critérios de aceite).
- *Done* só depois do merge em `develop` **e** aprovação do PO em *UAT*.

Itens podem ser **draft items** (só no board, sem Issue) ou Issues do repo.
Para popular em lote: `scripts/popular-board.sh` (ver `--help`).
