# ADR-001 — Monorepo com backend e frontend

**Status:** Aceito · **Data:** 2026-07-29 · **Decisores:** Equipe 01

## Contexto

O repositório começou com o FastAPI na raiz (`app/`, `pyproject.toml`, `docker-compose.yml`
direto em `/`). O frontend Next.js ainda não existia. Duas opções: repositórios separados ou
um só.

Restrições: 6 pessoas, prazo curto até 10/08, uma única entrega avaliada, ninguém do time com experiência
prévia em orquestrar dois repositórios.

## Decisão

**Monorepo** com dois diretórios de topo:

```
backend/   FastAPI + SQLAlchemy + Alembic
frontend/  Next.js + TypeScript + Mantine
```

O FastAPI que estava na raiz foi movido para `backend/` e `app/database.py` virou
`backend/app/core/database.py`. `docker-compose.yml`, `Makefile` e `.env.example` ficam na
raiz e orquestram os dois.

## Consequências

**Positivas**

- Um `git clone` + `make bootstrap` entrega o sistema completo. Critério de sucesso da visão
  do produto ("1 comando").
- Um único PR pode conter backend + frontend da mesma US, com revisão coerente.
- Um `docker-compose.yml` sobe banco, API e web com a rede interna já resolvida.
- Um CI com jobs paralelos, um único quality gate.
- Wiki, Projects e Issues em um lugar — o que a avaliação examina.

**Negativas**

- Mais chance de conflito de merge. Mitigação: divisão por pasta entre pessoas e PRs pequenos.
- CI roda backend e frontend mesmo em mudança de um só. Aceitável no volume do projeto;
  se incomodar, `paths-filter` resolve.
- Versionamento único (uma tag para os dois). Irrelevante aqui.

## Alternativas

| Alternativa | Por que não |
|---|---|
| Dois repositórios | Dobraria CI, README, board e Wiki; sincronizar versões custaria tempo que não temos |
| Frontend embutido no FastAPI (Jinja) | Contraria a stack exigida (React/Next/Mantine) |
| Monorepo com yarn workspaces cobrindo backend | Backend é Python; workspaces não ajudam |
