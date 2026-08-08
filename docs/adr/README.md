# Architecture Decision Records (ADR)

Registro das decisões arquiteturais do projeto. Formato enxuto: **Contexto → Decisão →
Consequências → Alternativas**.

Regras:

- Um ADR é **imutável a partir do momento em que a equipe o aceita em cerimônia**. Para mudar
  de rumo depois disso, crie um ADR novo com status `Substitui ADR-XXX` e marque o antigo como
  `Substituído por ADR-YYY`.
- Toda decisão que um novo membro perguntaria "por que assim?" merece um ADR.
- ADR não é documentação de como usar — é registro de por que foi escolhido.

> **Marco de imutabilidade: 31/07/2026.** Os ADR-001 a ADR-007 foram redigidos em um único dia
> (29/07), antes do kickoff, e **nunca passaram por revisão da equipe**. Eram rascunho, não
> história. Por isso foram **corrigidos no lugar** durante o rebaseline de 30/07
> ([ADR-008](ADR-008-rebaseline-escopo.md)), e cada um traz a data da revisão no cabeçalho.
>
> O que foi corrigido:
>
> | ADR | Correção |
> |---|---|
> | ADR-002 | O mapeamento dizia `View = frontend/src/app/`. Corrigido: a View do MVC é a camada de schemas Pydantic, e o MVC se fecha dentro de `backend/` |
> | ADR-003 | Removida a análise de uma frase do Wiki sobre médicos logando — fonte que não existe mais desde a republicação. A decisão (médico não é perfil) permanece |
> | ADR-006 | A contagem dizia 20 testes unitários; são 17, conferidos no código |
> | ADR-001, 002, 004 | "2 semanas" trocado pelo prazo real |
>
> **A partir do kickoff de 31/07, a regra de imutabilidade vale integralmente.** ADR aceito em
> Planning não se edita: escreve-se um novo que o substitui. O ADR-008 é o primeiro sob a regra.

| ADR | Título | Status |
|---|---|---|
| [ADR-001](ADR-001-monorepo.md) | Monorepo com backend e frontend | Aceito |
| [ADR-002](ADR-002-camadas-mvc.md) | Camadas Router → Service → Repository → Model | Aceito |
| [ADR-003](ADR-003-autenticacao.md) | Login flexível CPF ou e-mail com JWT | Aceito |
| [ADR-004](ADR-004-bootstrap-atendente.md) | Bootstrap do primeiro atendente por seed | Aceito |
| [ADR-005](ADR-005-cadastro-paciente.md) | Auto-cadastro e cadastro por atendente no mesmo fluxo | Aceito |
| [ADR-006](ADR-006-design-patterns.md) | Strategy e Repository; índice parcial para a RN03 | Aceito |
| [ADR-007](ADR-007-vitest.md) | Vitest no Next.js em vez de Jest | Aceito |
| [ADR-008](ADR-008-rebaseline-escopo.md) | Rebaseline de escopo e separação backend × frontend na documentação | Aceito · §1 parcialmente substituído por [ADR-009](ADR-009-inativacao-especialidade-medico.md) |
| [ADR-009](ADR-009-inativacao-especialidade-medico.md) | Inativação de especialidade e médico entra no MVP (RN16) | Aceito · substitui [ADR-008](ADR-008-rebaseline-escopo.md) §1 no corte de MF03/MF04 |
