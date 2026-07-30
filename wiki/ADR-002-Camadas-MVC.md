# ADR-002 — Camadas Router → Service → Repository → Model

**Status:** Aceito · **Data:** 2026-07-29 · **Decisores:** Equipe 01

## Contexto

O enunciado exige **arquitetura MVC** documentada (RNF01). O MVC clássico pressupõe View
renderizada pelo servidor; aqui a View é um app Next.js separado. Além disso, o FastAPI
permite escrever tudo no arquivo do router — caminho mais rápido no dia 1 e mais caro no dia 5.

O Módulo 4 do curso apresenta a arquitetura em camadas e o MVC como estilo, e o Módulo 2
cobra baixo acoplamento e testabilidade.

## Decisão

Quatro camadas com dependência **sempre para dentro**:

```
Router (Controller) → Service → Repository → Model → PostgreSQL
```

Mapeamento para o MVC: **View** = `frontend/src/app/`; **Controller** = `backend/app/routers/`;
**Model** = `backend/app/models/`. **Service** e **Repository** são camadas de apoio que
evitam o "fat controller" e o acoplamento ao ORM.

Contratos verificáveis:

| Camada | Proibido |
|---|---|
| Service | importar `fastapi`, `HTTPException`, `Session`, `select` |
| Router | conter `if` de regra de negócio |
| Repository | conter regra de negócio ou chamar `commit()` |
| Model | ter lógica de aplicação |

O `commit()` é do Router — uma requisição, uma transação. Repository faz `flush()`.

## Consequências

**Positivas**

- Testar regra de negócio não exige banco nem HTTP (ver ADR-006).
- Violação de camada é detectável por `grep`, o que torna o code review objetivo:
  `grep -r "HTTPException\|select(" backend/app/services/` deve ser vazio.
- Regra nova = exceção nova + método no service; nenhum router muda.
- Duas pessoas podem trabalhar na mesma US em camadas diferentes.

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
| Hexagonal com ports/adapters completo | Ganho marginal aqui, custo de abstração alto para 2 semanas |
| Microsserviços | O próprio material recomenda monolito para equipe pequena em fase inicial |


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
