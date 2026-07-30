# Clean Code e SOLID aplicados

Entregável do Engenheiro de Software: **3 práticas de Clean Code**, aplicadas de verdade no
código e documentadas com exemplo ruim/bom. Base: *Módulo 2 — Clean Code e SOLID* e
*Prática - Clean Code* (`material-aulas/`).

> **Duas stacks, as mesmas três práticas.** O projeto tem duas aplicações — Python/FastAPI e
> TypeScript/Next.js ([`03-arquitetura.md`](03-arquitetura.md)). Cada prática abaixo é
> demonstrada primeiro no **backend**, onde nasceu, e depois traduzida para o **frontend** na
> §*A mesma prática no frontend*. As duas versões contam para o entregável — não é o mesmo
> código repetido, é o mesmo princípio resolvendo problemas diferentes em linguagens
> diferentes.

| Prática | Responsável no backend | Responsável no frontend |
|---|---|---|
| 1. Nomes significativos | Ronaldo | João Vitor |
| 2. Funções pequenas com responsabilidade única | Ronaldo | João Vitor |
| 3. Exceções tipadas em vez de códigos de erro | Ronaldo | João Vitor |

---

## Prática 1 — Nomes significativos

> *"Variáveis, funções e classes devem revelar claramente sua intenção. Evite nomes
> genéricos como `data` ou `temp`."* — Módulo 2

### Onde está aplicada

`app/models/enums.py`, `app/services/*`, `app/exceptions/dominio.py`

### Ruim

```python
def proc(d, db):
    if db.query(P).filter_by(c=d["c"]).first():
        return -1
    p = P(**d)
    db.add(p); db.commit()
    return 1

# status numérico: ninguém sabe o que 3 significa
if consulta.status == 3:
    ...

# número mágico sem nome
if (h.data_hora - datetime.now()).total_seconds() < 86400:
    ...
```

`proc`, `d`, `P`, `c`, `1`, `-1`, `3`, `86400` — nada disso é pesquisável nem pronunciável.
O revisor precisa abrir outro arquivo para saber o que `3` quer dizer.

### Bom

```python
def cadastrar_paciente(dados: PacienteCriar) -> Paciente: ...

class StatusConsulta(StrEnum):
    SOLICITADA = "SOLICITADA"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"

if consulta.status is StatusConsulta.CANCELADA:
    ...

# o prazo tem nome, vem de configuração e o teste pode mudá-lo
self.antecedencia_minima = timedelta(hours=settings.CANCELAMENTO_ANTECEDENCIA_HORAS)
```

### Convenções fixadas no projeto

| Elemento | Convenção | Exemplo |
|---|---|---|
| Método que valida e levanta exceção | `_garantir_<invariante>` | `_garantir_cpf_inedito` |
| Método que busca ou falha | `_buscar_ou_falhar` | `_buscar_ou_falhar(consulta_id)` |
| Repository que busca por campo | `buscar_por_<campo>` | `buscar_por_cpf` |
| Repository que lista com filtro | `listar_<filtro>` | `listar_livres`, `listar_ativos` |
| Exceção de domínio | substantivo do problema | `HorarioIndisponivel`, `MedicoJaAlocado` |
| Teste | `test_[ctuNN_]deve_<comportamento>` | `test_ctu03_deve_bloquear_agendamento_em_horario_ja_ocupado` |

Nenhum número mágico no código: `24` vem de `settings`, `08:00`/`18:00` são
`HORA_ABERTURA`/`HORA_FECHAMENTO` em `schemas/agenda_schema.py`.

---

## Prática 2 — Funções pequenas com responsabilidade única

> *"Ideal: 1-5 linhas | Aceitável: até 20 linhas | Se > 20 linhas, provavelmente faz mais de
> uma coisa."* — Módulo 2

### Onde está aplicada

`PacienteService`, `ConsultaService`, `AgendaService`, `AuthService`

### Ruim

```python
def cancelar_consulta(consulta_id, perfil, db):
    consulta = db.query(Consulta).filter_by(id=consulta_id).first()
    if not consulta:
        raise HTTPException(404, "Consulta nao encontrada")
    if consulta.status in ("CANCELADA", "FINALIZADA"):
        raise HTTPException(422, "Consulta nao pode ser cancelada")
    if perfil == "PACIENTE":
        horario = db.query(HorarioDisponivel).filter_by(
            id=consulta.horario_disponivel_id
        ).first()
        momento = datetime.combine(horario.data, horario.horario)
        if (momento - datetime.now()).total_seconds() < 24 * 3600:
            raise HTTPException(422, "Cancelamento nao permitido")
    consulta.status = "CANCELADA"
    horario = db.query(HorarioDisponivel).filter_by(
        id=consulta.horario_disponivel_id
    ).first()
    horario.disponivel = True
    db.commit()
    return consulta
```

Uma função com seis responsabilidades: busca, valida existência, valida status, aplica regra
de prazo por perfil, muda estado, libera slot e commita. Para testar a regra de 24h é preciso
banco e HTTP. Adicionar um terceiro perfil obriga a mexer aqui dentro (viola OCP).

### Bom

```python
def cancelar(self, consulta_id, perfil, motivo=None, agora=None) -> Consulta:
    consulta = self._buscar_ou_falhar(consulta_id)
    self._garantir_transicao(consulta.status, StatusConsulta.CANCELADA)

    strategy = obter_strategy(perfil, settings.CANCELAMENTO_ANTECEDENCIA_HORAS)
    strategy.validar(consulta, agora or self._agora())

    consulta.status = StatusConsulta.CANCELADA
    consulta.motivo_cancelamento = motivo
    consulta.horario.disponivel = True          # RN03
    return self.consultas.salvar(consulta)
```

Cada linha é uma etapa nomeada. `_buscar_ou_falhar`, `_garantir_transicao` e a Strategy são
testáveis isoladamente. `agora` é parâmetro — o teste da RN04 não depende do relógio.

Mesmo padrão no cadastro (o método público só orquestra):

```python
def cadastrar(self, dados: PacienteCriar) -> Paciente:
    self._garantir_cpf_inedito(dados.cpf)       # RN01
    self._garantir_email_inedito(dados.email)   # RN02
    return self.repositorio.salvar(Paciente(**dados.model_dump()))
```

### Objeto como parâmetro em vez de lista longa

> *"Difícil de lembrar ordem dos parâmetros."* — Prática Clean Code

```python
# Ruim
def cadastrar_paciente(nome, cpf, email, telefone, nascimento, ativo, ...): ...

# Bom — schema Pydantic já validado
def cadastrar(self, dados: PacienteCriar) -> Paciente: ...
```

### Métrica

Nenhum método do projeto passa de 12 linhas. Verificação: `ruff` com `line-length = 100` e
revisão de PR. Métrica-alvo do Módulo 2: complexidade ciclomática < 10 por função — atendida
porque as ramificações estão distribuídas entre métodos privados e Strategies.

---

## Prática 3 — Exceções tipadas em vez de códigos de erro

> *"Use exceções, não códigos de erro. Erro silencioso causa bugs difíceis de rastrear."*
> — Módulo 2

### Onde está aplicada

`app/exceptions/dominio.py`, `app/exceptions/handlers.py`, todos os services

### Ruim

```python
def cadastrar_paciente(dados, db):
    if db.query(Paciente).filter_by(cpf=dados["cpf"]).first():
        return {"error": "CPF_DUPLICADO", "code": 409}
    ...
    return {"success": True, "data": paciente}

# quem chama tem que lembrar de checar — e uma hora esquece
resultado = cadastrar_paciente(dados, db)
if resultado.get("error"):
    print(resultado["error"])
```

Problemas: o retorno de sucesso e o de erro têm formatos diferentes; esquecer o `if` faz o
erro passar silenciosamente; o tipo de retorno não diz nada; e a regra de negócio passa a
conhecer códigos HTTP.

### Bom

```python
# app/exceptions/dominio.py — a exceção carrega o status; o service ignora HTTP
class RegraDeNegocioViolada(Exception):
    status_code: int = 400
    mensagem: str = "Regra de negocio violada"

class CpfDuplicado(RegraDeNegocioViolada):
    """RN01."""
    status_code = 409
    mensagem = "CPF ja cadastrado"

# app/services/paciente_service.py
def _garantir_cpf_inedito(self, cpf: str) -> None:
    """RN01."""
    if self.repositorio.buscar_por_cpf(cpf):
        raise CpfDuplicado

# app/exceptions/handlers.py — único ponto que conhece HTTP
@app.exception_handler(RegraDeNegocioViolada)
async def _handler(_, erro):
    return JSONResponse(
        status_code=erro.status_code,
        content={"detail": erro.mensagem, "erro": type(erro).__name__},
    )
```

Ganhos concretos:

- Impossível ignorar o erro por acidente.
- Assinatura honesta: `-> Paciente`, não `-> dict | None`.
- Adicionar uma regra nova = criar uma classe; nenhum router muda.
- O teste fica declarativo: `with pytest.raises(CpfDuplicado):`.
- **Nenhuma exceção é silenciada** — não existe `except: pass` no projeto.

### Catálogo

| Exceção | HTTP | Regra |
|---|---|---|
| `CpfDuplicado` | 409 | RN01 |
| `EmailDuplicado` | 409 | RN02 |
| `HorarioIndisponivel` | 409 | RN03 |
| `MedicoJaAlocado` | 409 | RN05 |
| `CancelamentoNaoPermitido` | 422 | RN04 |
| `TransicaoDeStatusInvalida` | 422 | RN06, RN10 |
| `RecursoNaoEncontrado` | 404 | — |
| `CredenciaisInvalidas` | 401 | RN11 |

---

## SOLID complementar

### S — Single Responsibility

Cada service cuida de um domínio: `AuthService` (credenciais), `PacienteService` (cadastro),
`AgendaService` (grade), `ConsultaService` (ciclo de vida). Não existe `ClinicaService`
fazendo tudo — o antipadrão "classe faz-tudo" do Módulo 2.

E dentro do domínio a separação continua: quem valida (`_garantir_*`), quem persiste
(Repository) e quem traduz para HTTP (handler) são peças distintas — exatamente o exemplo
`User` / `EmailValidator` / `UserRepository` do material.

### O — Open/Closed

`CancelamentoStrategy` é o caso canônico. Adicionar um perfil MEDICO com regra própria de
cancelamento significa **criar uma classe nova**, sem editar `ConsultaService`. É a mesma
refatoração que o Módulo 2 mostra com `PaymentProcessor` + `if/elif` → Strategy.

### L — Liskov Substitution

Toda `CancelamentoStrategy` respeita o mesmo contrato: `validar()` retorna `None` ou levanta
`CancelamentoNaoPermitido`. `CancelamentoPorAtendente` não quebra a expectativa — ela apenas
não tem restrição. `ConsultaService` funciona com qualquer implementação sem saber qual é.

### I — Interface Segregation

`RepositorioBase` expõe só `buscar_por_id`, `listar` e `salvar`. Métodos específicos ficam nos
repositories concretos (`buscar_por_cpf` só em `PacienteRepository`). Nenhum repository é
obrigado a implementar método que não usa.

### D — Dependency Inversion

O ponto mais importante da testabilidade do projeto: os services recebem o repository por
construtor e dependem da **abstração**, não de `Session`.

```python
class PacienteService:
    def __init__(self, repositorio: PacienteRepository):
        self.repositorio = repositorio
```

Por isso os 17 testes unitários rodam em ~3 segundos sem PostgreSQL, usando os fakes de
`tests/conftest.py`. Nos routers, o FastAPI injeta a implementação real via `Depends`.

---

## As mesmas 3 práticas no frontend

O frontend é outra aplicação, com outra linguagem e outros problemas. Os princípios são os
mesmos; a aplicação deles muda.

### Prática 1 no frontend — nomes significativos

**Onde está aplicada:** `src/lib/api.ts`, `src/lib/cpf.ts`, `src/types/dominio.ts`

```ts
// ❌ Ruim — o que é `d`? o que significa `s === 2`?
const d = await fetch(`/api/consultas/${id}`).then(r => r.json());
if (d.s === 2) mostrarBotao();

// ✅ Bom — o tipo revela a intenção e o enum elimina o número mágico
const consulta: Consulta = await api.get<Consulta>(`/consultas/${id}`);
if (consulta.status === StatusConsulta.CONFIRMADA) mostrarBotaoFinalizar();
```

**Convenções fixadas**

| Elemento | Convenção | Exemplo |
|---|---|---|
| Componente | `PascalCase`, substantivo | `GradeDeHorarios`, `CardConsulta` |
| Hook | `use` + verbo | `useConsultasDoPaciente()` |
| Handler de evento | `handle` + evento | `handleConfirmarAgendamento()` |
| Booleano | `é`/`tem`/`pode` no nome | `podeCancelar`, `estaCarregando` |
| Tipo de domínio | espelha o schema do backend | `Consulta`, `HorarioDisponivel` |

### Prática 2 no frontend — funções e componentes pequenos

No React, o equivalente a "função pequena com responsabilidade única" é **separar o componente
que busca dados do componente que desenha**.

```tsx
// ❌ Ruim — um componente que busca, filtra, formata e desenha
export default function Consultas() {
  const [dados, setDados] = useState([]);
  useEffect(() => { /* fetch, tratamento de erro, filtro, ordenação... */ }, []);
  return <div>{/* 80 linhas de JSX com if aninhado */}</div>;
}

// ✅ Bom — cada peça faz uma coisa
export default function PaginaConsultas() {
  const { consultas, estaCarregando, erro } = useConsultasDoPaciente();  // busca
  if (estaCarregando) return <SkeletonConsultas />;                       // estado
  if (erro) return <AvisoDeErro mensagem={erro.message} />;               // estado
  return <ListaDeConsultas consultas={consultas} />;                      // desenho
}

// ListaDeConsultas recebe props e nao sabe de onde vieram — testavel isolado
```

**Métrica adotada:** componente com mais de ~80 linhas de JSX, ou com mais de um `useEffect`
de busca, é sinal de que há dois componentes ali dentro.

### Prática 3 no frontend — erro tipado em vez de código

`src/lib/api.ts` é o único ponto do app que conhece HTTP. Ele traduz status em `ApiError`
tipado, e nenhum componente precisa saber o que é um 409.

```ts
// ❌ Ruim — cada componente reinterpreta o status
const resposta = await fetch('/api/consultas', { method: 'POST', body });
if (resposta.status === 409) alert('erro');
if (resposta.status === 422) alert('outro erro');

// ✅ Bom — o cliente HTTP lanca um erro tipado com a mensagem que o backend mandou
try {
  await api.post('/consultas', { horario_disponivel_id: id });
} catch (erro) {
  if (erro instanceof ApiError) {
    notifications.show({ message: erro.message, color: 'red' });
    if (erro.status === 409) await recarregarHorarios();
  }
}
```

O ganho é o mesmo do backend: **a mensagem de erro tem uma fonte só**. O backend já devolve
texto pronto (`CPF ja cadastrado`), e o frontend o repassa em vez de reescrever a regra.

> ⚠️ **Onde o frontend erra com mais facilidade.** Duplicar regra de negócio "para melhorar a
> experiência" — por exemplo, calcular as 24h da RN04 em JavaScript para esconder o botão de
> cancelar. Isso cria duas fontes da verdade que divergem por fuso horário (RN15). A API devolve
> `pode_cancelar`; o React obedece.

---

## Refatoração incremental

O Módulo 2 e a *Prática - Clean Code* tratam refatoração como processo contínuo, não como
tarefa no fim. No projeto:

- **Regra do Escoteiro** — todo PR pode melhorar nome ou extrair método no código que tocou,
  desde que o comportamento não mude e o teste continue passando.
- **Extract Method** — técnica principal. Foi assim que `cancelar()` virou
  `_buscar_ou_falhar` + `_garantir_transicao` + Strategy.
- **Refinamento técnico visível** — débito técnico entra no board como item próprio, com
  label `tech-debt`, não fica na cabeça de quem viu. Foi o que a *Aula Prática 13-05* pediu:
  *"documentar os antipadrões no quadro Kanban"*.

## Métricas de qualidade (Módulo 2)

| Métrica | Meta do material | Como medimos |
|---|---|---|
| Complexidade ciclomática | < 10 por função | `ruff` + revisão; ramos distribuídos em privados/Strategy |
| Cobertura de testes | > 80% | `pytest --cov` e `vitest --coverage` no CI |
| Duplicação de código | < 5% | `RepositorioBase` genérico e `src/lib/api.ts` único |
| Índice de manutenibilidade | > 80 | Proxy: camadas verificáveis por `grep` + PR pequeno |
