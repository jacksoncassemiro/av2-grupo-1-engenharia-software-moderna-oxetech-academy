# Architecture Decision Records (ADR)

Registro das decisões arquiteturais do projeto. Formato enxuto: **Contexto → Decisão →
Consequências → Alternativas**.

Regras:

- Um ADR é **imutável**. Para mudar de rumo, crie um ADR novo com status
  `Substitui ADR-XXX` e marque o antigo como `Substituído por ADR-YYY`.
- Toda decisão que um novo membro perguntaria "por que assim?" merece um ADR.
- ADR não é documentação de como usar — é registro de por que foi escolhido.

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-monorepo.md) | Monorepo com backend e frontend | Aceito |
| [ADR-002](ADR-002-camadas-mvc.md) | Camadas Router → Service → Repository → Model | Aceito |
| [ADR-003](ADR-003-autenticacao.md) | Login flexível CPF ou e-mail com JWT | Aceito |
| [ADR-004](ADR-004-bootstrap-atendente.md) | Bootstrap do primeiro atendente por seed | Aceito |
| [ADR-005](ADR-005-cadastro-paciente.md) | Auto-cadastro e cadastro por atendente no mesmo fluxo | Aceito |
| [ADR-006](ADR-006-design-patterns.md) | Strategy e Repository; índice parcial para a RN03 | Aceito |
| [ADR-007](ADR-007-vitest.md) | Vitest no Next.js em vez de Jest | Aceito |
