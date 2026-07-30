---
name: clinica-backend
description: Implementa uma feature no backend FastAPI do MVP da clinica seguindo a arquitetura em camadas Router -> Service -> Repository -> Model. Use quando a tarefa envolver endpoint, regra de negocio (RN01-RN15), model SQLAlchemy, schema Pydantic, migracao Alembic ou teste pytest deste projeto.
---

# Backend da clinica — como implementar

## Ordem obrigatoria

Implemente **de dentro para fora**. Nunca comece pelo router.

1. **Model** (`app/models/`) — colunas e constraints. Constraint de banco é a primeira
   linha de defesa das RNs (ex.: `UniqueConstraint` da RN05).
2. **Migração** — `make migration m="descricao"`, depois **leia** o arquivo gerado em
   `alembic/versions/` e corrija índices parciais que o autogenerate não pega.

   ⚠️ `alembic upgrade head` **não falha** com `versions/` vazia ou desatualizada — ele
   simplesmente não cria nada, e o erro aparece só depois (`UndefinedTable`).
   `tests/integration/test_migracoes.py` compara model × migração e falha no PR. Rode-o
   sempre que tocar em model.
3. **Schema** (`app/schemas/`) — validação de formato (RN07 CPF, RN08 e-mail, RN09 horário).
4. **Repository** (`app/repositories/`) — só query. Herde de `RepositorioBase`.
5. **Service** (`app/services/`) — a regra de negócio. Levante exceção de domínio.
6. **Teste unitário** (`tests/unit/`) — com fake de repositório, sem banco.
7. **Router** (`app/routers/`) — por último, só fiação.

## Contratos de cada camada

**Service** — proibido importar `fastapi`, `HTTPException`, `Session`, `select`.
Recebe repositories no `__init__`. Método público curto que delega para `_privados`:

```python
def cadastrar(self, dados: PacienteCriar) -> Paciente:
    self._garantir_cpf_inedito(dados.cpf)      # RN01
    self._garantir_email_inedito(dados.email)  # RN02
    return self.repositorio.salvar(Paciente(**dados.model_dump()))
```

**Router** — proibido conter `if` de regra. Sempre este formato:

```python
@router.post("", response_model=XResposta, status_code=201, summary="US-XX")
def criar(
    dados: XCriar,
    service: Annotated[XService, Depends(obter_service)],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAutenticado, Depends(exigir_atendente)],  # RN12
) -> XResposta:
    entidade = service.criar(dados)
    db.commit()
    return XResposta.model_validate(entidade)
```

O `db.commit()` é do router. O repository faz `flush()`, nunca `commit()`.

**Exceções** — nunca `HTTPException` fora de `core/deps.py`. Crie/reutilize em
`app/exceptions/dominio.py`, que já leva o `status_code`:

```python
class HorarioIndisponivel(RegraDeNegocioViolada):
    """RN03."""
    status_code = 409
    mensagem = "Horario indisponivel"
```

## Regra que depende do perfil → Strategy, não `if`

Se a regra muda conforme quem executa, estenda `CancelamentoStrategy` em
`services/cancelamento_strategy.py`. Escrever `if perfil == TipoUsuario.PACIENTE`
dentro de um service quebra o OCP e é apontado na avaliação.

## Concorrência (US-08)

Reserva de slot usa `buscar_para_reserva()` (`SELECT ... FOR UPDATE`) **e** o índice
parcial `uq_slot_ativo`. Não remova nenhum dos dois: o lock resolve a corrida, o índice
é a garantia de último recurso.

## Autorização

`Depends(exigir_atendente)` ou `Depends(exigir_paciente)` em toda rota que não seja
`/auth/*` ou `/health`. Paciente age sempre sobre `usuario.paciente_id` do token —
**nunca** sobre um id vindo do path/body, senão qualquer paciente lê o prontuário do outro.

## Teste unitário — padrão do projeto

Use os fakes de `tests/conftest.py` (`FakePacienteRepository`, etc.), não `MagicMock` cego.
Nome do teste declara a regra:

```python
@pytest.mark.unit
def test_ctu03_deve_bloquear_agendamento_em_horario_ja_ocupado(slot_livre):
    """RN03 - slot com consulta ativa nao pode ser reservado de novo."""
```

Tempo é sempre injetado (`agora=datetime(...)`), nunca `datetime.now()` dentro do teste.

## Checklist antes de abrir PR

- [ ] `ruff check . && ruff format --check .`
- [ ] `pytest -q` verde
- [ ] Cada RN tocada tem teste citando o ID
- [ ] `grep -r "HTTPException\|select(" app/services/` vazio
- [ ] Migração gerada e revisada
