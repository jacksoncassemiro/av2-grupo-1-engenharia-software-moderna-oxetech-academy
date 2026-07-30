# ADR-002 — Camadas Controller → Service → Repository → Model

**Status:** Aceito · **Data:** 2026-07-29 · **Revisado:** 2026-07-30 (rebaseline — ADR-008)
· **Decisores:** Equipe 01

> **Revisão de 30/07.** A versão original deste ADR mapeava a **View do MVC** para
> `frontend/src/app/`. Isso estava incorreto e foi substituído pelo mapeamento da §Decisão
> abaixo. Justificativa em [ADR-008](ADR-008-rebaseline-escopo.md) §3.

## Contexto

O enunciado exige **arquitetura MVC** documentada (RNF01). O MVC clássico pressupõe View
renderizada pelo servidor — um template que o Controller preenche. Numa API REST essa View não
existe: o Controller devolve JSON. Além disso, o FastAPI permite escrever tudo no arquivo do
router — caminho mais rápido no dia 1 e mais caro no dia 5.

O Módulo 4 do curso apresenta a arquitetura em camadas e o MVC como estilo, e o Módulo 2
cobra baixo acoplamento e testabilidade.

## Decisão

Quatro camadas com dependência **sempre para dentro**, **inteiramente dentro de `backend/`**:

```
Controller → Service → Repository → Model → PostgreSQL
```

Mapeamento para o MVC:

| Camada MVC | Onde | Papel |
|---|---|---|
| **Model** | `backend/app/models/` | Entidades SQLAlchemy e constraints das RNs |
| **View** | `backend/app/schemas/` | DTOs Pydantic — a representação do Model para o mundo externo |
| **Controller** | `backend/app/routers/` | Recebe a requisição, autoriza, chama um service, devolve o schema |

**Service** e **Repository** são camadas de apoio que evitam o "fat controller" e o acoplamento
ao ORM.

**O app Next.js não é a View do MVC.** Ele é uma segunda aplicação, com roteamento, estado e
build próprios; não é preenchido pelo Controller, apenas *consome* a API. A leitura adotada —
serializador no papel de View — é a mesma do Django REST Framework, e faz o MVC se fechar onde
ele de fato existe. A arquitetura do frontend está documentada em
[`03-arquitetura.md`](../03-arquitetura.md) §3, com vocabulário próprio.

Contratos verificáveis:

| Camada | Proibido |
|---|---|
| Service | importar `fastapi`, `HTTPException`, `Session`, `select` |
| Controller | conter `if` de regra de negócio |
| Repository | conter regra de negócio ou chamar `commit()` |
| Model | ter lógica de aplicação |
| Schema (View) | consultar o banco |

O `commit()` é do Controller — uma requisição, uma transação. Repository faz `flush()`.

## Consequências

**Positivas**

- Testar regra de negócio não exige banco nem HTTP (ver ADR-006).
- Violação de camada é detectável por `grep`, o que torna o code review objetivo:
  `grep -r "HTTPException\|select(" backend/app/services/` deve ser vazio.
- Regra nova = exceção nova + método no service; nenhum Controller muda.
- Duas pessoas podem trabalhar na mesma US em camadas diferentes.
- Com a View sendo os schemas Pydantic, o MVC é apontável num diretório só na apresentação,
  em vez de espalhado por duas stacks.

**Negativas**

- Mais arquivos por feature (model, schema, repository, service, router, teste). Custo real
  no início; paga-se a partir da terceira US.
- Curva de aprendizado para quem só viu CRUD em arquivo único. Mitigado por `CLAUDE.md` e
  pela skill `clinica-backend`.

## Alternativas

| Alternativa | Por que não |
|---|---|
| Tudo no router | Impede teste sem banco; é o "fat controller" que o Módulo 2 critica |
| Router → Model (sem Service/Repository) | Regra de negócio no model = duas responsabilidades |
| Hexagonal com ports/adapters completo | Ganho marginal aqui, custo de abstração alto para o prazo disponível |
| Microsserviços | O próprio material recomenda monolito para equipe pequena em fase inicial |
