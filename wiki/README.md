# Espelho do Wiki

Estas páginas são **geradas** a partir de `docs/` e publicadas no Wiki do GitHub.

## Fluxo

```bash
python3 scripts/gerar-wiki.py           # 1. regenera wiki/ a partir de docs/  (Windows: .\scripts\gerar-wiki.ps1)
./scripts/publicar-wiki.sh --dry-run    # 2. confere o que mudaria
./scripts/publicar-wiki.sh              # 3. publica no Wiki do GitHub
```

`python3 scripts/gerar-wiki.py --check` (Windows: `.\scripts\gerar-wiki.ps1 -Check`) falha se `wiki/` estiver fora de sincronia com `docs/` —
útil como verificação antes de abrir PR.

## ⚠️ Regra da equipe

**Fonte da verdade é `docs/`.** Não edite pelo Wiki do GitHub na web — a próxima publicação
sobrescreve. Se alguém editou na web, copie a alteração para `docs/` antes de publicar.

## Páginas

| Página | Origem |
|---|---|
| `Home.md` | escrita à mão (índice do wiki) |
| `_Sidebar.md` | navegação lateral |
| `_Footer.md` | rodapé |
| `Visao-do-Produto.md` | `docs/00-visao-do-produto.md` |
| `Requisitos.md` | `docs/01-requisitos.md` |
| `Backlog-e-User-Stories.md` | `docs/02-backlog.md` |
| `Arquitetura.md` | `docs/03-arquitetura.md` |
| `Modelo-de-Dados.md` | `docs/04-modelo-de-dados.md` |
| `Clean-Code-e-SOLID.md` | `docs/05-clean-code.md` |
| `Design-Patterns.md` | `docs/06-design-patterns.md` |
| `Plano-de-Testes.md` | `docs/07-plano-de-testes.md` |
| `Casos-de-Teste.md` | `docs/08-casos-de-teste.md` |
| `CI-CD.md` | `docs/09-ci-cd.md` |
| `Git-Flow.md` | `docs/10-git-flow.md` |
| `Ciclo-de-Desenvolvimento.md` | `docs/11-ciclo-desenvolvimento.md` |
| `Cronograma.md` | `docs/12-cronograma.md` |
| `Papeis-e-Responsabilidades.md` | `docs/13-papeis-e-responsabilidades.md` |
| `Conflitos-e-Decisoes.md` | `docs/14-conflitos-e-decisoes.md` |
| `ADR-00*.md` | `docs/adr/ADR-00*.md` |
