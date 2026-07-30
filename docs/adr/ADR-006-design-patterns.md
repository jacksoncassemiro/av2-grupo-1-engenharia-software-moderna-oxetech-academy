# ADR-006 — Strategy e Repository; índice parcial para a RN03

**Status:** Aceito · **Data:** 2026-07-29 · **Decisores:** Equipe 01

## Contexto

O enunciado exige **2 padrões de projeto** implementados e documentados (RNF03). O Módulo 3 do
curso cobre os 23 padrões GoF, e o `Case - Design Patterns` demonstra Singleton, Factory Method
e Builder num e-commerce.

O risco é escolher padrão "bonito" sem problema para resolver — o que o próprio Módulo 3 trata
como antipadrão. Então partimos dos problemas reais deste MVP:

1. A regra de cancelamento **muda conforme o perfil** (RN04 para paciente, sem restrição para
   atendente). O caminho natural seria `if perfil == ...`, que viola OCP.
2. Com SQLAlchemy chamado direto no service, **testar qualquer RN exige PostgreSQL rodando**.
   Numa equipe de 6 pessoas em máquinas diferentes, isso trava o desenvolvimento.

Um terceiro problema apareceu ao revisar a modelagem do Wiki, e é de banco, não de código:
o `UNIQUE` em `consulta.horario_disponivel_id` (proposto para garantir a RN03) **impediria
reagendar um slot depois de cancelado** — porque a linha da consulta CANCELADA continuaria
ocupando o índice. A US-11 diz explicitamente que o slot volta a ficar disponível.

## Decisão

### Padrão 1 — Strategy (comportamental)

`backend/app/services/cancelamento_strategy.py`

`CancelamentoStrategy` (ABC) com `CancelamentoPorPaciente` (valida RN04) e
`CancelamentoPorAtendente` (não valida). `obter_strategy(perfil)` resolve qual usar.
`ConsultaService.cancelar()` não contém nenhum `if` de perfil.

É a mesma refatoração que o Módulo 2 demonstra: `PaymentProcessor` com
`if type == 'credit' / elif 'debit' / elif 'paypal'` → Strategy.

### Padrão 2 — Repository (arquitetural)

`backend/app/repositories/`

`RepositorioBase[ModeloT]` genérica com `buscar_por_id`, `listar`, `salvar`. Concretos expõem
só o que o domínio precisa (`buscar_por_cpf`, `listar_livres`, `buscar_para_reserva`).
Services recebem repository por construtor (DIP) — daí os fakes nos testes.

### Correção de modelagem — índice parcial para a RN03

```sql
CREATE UNIQUE INDEX uq_slot_ativo
  ON consulta (horario_disponivel_id)
  WHERE status IN ('SOLICITADA', 'CONFIRMADA');
```

Em SQLAlchemy:

```python
_SLOT_OCUPADO = text("status IN ('SOLICITADA', 'CONFIRMADA')")

__table_args__ = (
    Index("uq_slot_ativo", "horario_disponivel_id", unique=True,
          postgresql_where=_SLOT_OCUPADO),
)
```

Consultas CANCELADAS e FINALIZADAS ficam fora do índice, liberando o slot para reagendamento.

Complementarmente, a reserva usa **lock pessimista** — `HorarioRepository.buscar_para_reserva()`
com `SELECT ... FOR UPDATE` — para o cenário de concorrência que a própria US-08 descreve
("dois pacientes clicando ao mesmo tempo"). O índice é a garantia de último recurso.

## Consequências

**Positivas**

- **17 testes unitários em ~3 segundos, sem banco.** Contado e medido, não estimado. É o benefício
  concreto do Repository + DIP.
- Perfil novo com regra própria de cancelamento = classe nova, `ConsultaService` intacto (OCP).
- O prazo de 24h vem de `settings` e `agora` é injetado → teste determinístico e demonstração
  possível com prazo 0.
- Detalhe de lock pessimista encapsulado em uma linha do repository; o service só chama um
  método com nome de intenção.
- RN03 protegida em duas camadas (aplicação + banco) sem quebrar a US-11.

**Negativas**

- Mais arquivos e uma camada de indireção. Custo real de leitura para quem chega novo;
  mitigado por `CLAUDE.md` e pela skill `clinica-backend`.
- Os fakes de `tests/conftest.py` precisam ser mantidos em sincronia com a interface dos
  repositories reais. Se divergirem, o teste passa e a produção quebra. Mitigação: os testes de
  integração em `tests/integration/` exercitam o caminho real.
- Índice parcial é específico de PostgreSQL (`postgresql_where`). Aceitável: o banco é fixo
  pelo enunciado. Em SQLite os testes de integração não veriam o índice — mais um motivo para
  usar PostgreSQL também no CI.
- `SELECT FOR UPDATE` serializa reservas do mesmo slot. Irrelevante no volume de uma clínica.

## Alternativas

| Problema | Alternativa | Por que não |
|---|---|---|
| Regra por perfil | `if perfil ==` no service | Viola OCP; é o antipadrão do material |
| Regra por perfil | Chain of Responsibility | Corrente de um elo só; exagero |
| Regra por perfil | Template Method | Exigiria herdar `ConsultaService`; acopla mais |
| Acesso a dados | `Session` direto no service | Impede teste sem banco; espalha query |
| Acesso a dados | Active Record | Model com duas responsabilidades |
| Acesso a dados | Unit of Work explícito | O `Session` já é um UoW; o router delimita a transação |
| RN03 | `UNIQUE` simples | Trava o slot para sempre após o primeiro cancelamento |
| RN03 | Só o flag `disponivel` | Sem garantia no banco; corrida passa |
| RN03 | Lock otimista com coluna `version` | Mais código e conflito exposto ao usuário sem ganho |

## Padrões considerados e recusados

`Factory Method` (resolvido por `_status_inicial()` em 3 linhas), `Singleton`
(`@lru_cache` em `get_settings()` já resolve e permite override em teste), `Observer`
(notificação fora do MVP), `Decorator` (sem requisito de auditoria), `Builder`
(Pydantic já é o construtor validado), `State` (um dict `TRANSICOES_PERMITIDAS` é mais legível
que 4 classes para 4 status).

Detalhamento com código e diagramas em [../06-design-patterns.md](../06-design-patterns.md).
