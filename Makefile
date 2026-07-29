# Atalhos do projeto. Windows: use `make` do Git Bash/WSL, ou copie o comando.
.DEFAULT_GOAL := help
SHELL := /bin/bash

help: ## Lista os comandos disponiveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

up: ## Sobe todo o stack (postgres + api + web)
	docker compose up -d --build

down: ## Derruba o stack
	docker compose down

reset: ## Derruba e APAGA o volume do banco
	docker compose down -v

logs: ## Segue os logs de todos os servicos
	docker compose logs -f

migrate: ## Aplica as migracoes do Alembic
	docker compose exec backend alembic upgrade head

migration: ## Gera migracao: make migration m="cria tabela x"
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

seed: ## Cria o atendente inicial e as especialidades base (idempotente)
	docker compose exec backend python -m app.seeds.seed

bootstrap: up migrate seed ## Do zero ao sistema navegavel
	@echo ""
	@echo "  Frontend : http://localhost:3000"
	@echo "  Swagger  : http://localhost:8000/docs"
	@echo "  Login    : recepcao@clinica.com / admin123"

test: test-backend test-frontend ## Roda a suite completa

test-backend: ## pytest
	docker compose exec backend pytest --cov=app --cov-report=term-missing

test-frontend: ## vitest
	docker compose exec frontend yarn test

lint: ## ruff + eslint + tsc
	docker compose exec backend ruff check .
	docker compose exec frontend yarn lint
	docker compose exec frontend yarn typecheck

.PHONY: help up down reset logs migrate migration seed bootstrap test test-backend test-frontend lint
