#!/usr/bin/env python3
"""Gera scripts/board-itens.json — a fonte unica dos itens do board.

Por que um gerador e nao um JSON escrito a mao:
  o texto das regras de negocio, os criterios de aceite e a Definition of Done
  se repetem em dezenas de issues. Escrever a mao garante divergencia.
  Aqui a RN e escrita UMA vez e injetada em toda issue que a menciona.

Rode depois de editar este arquivo:

    python scripts/gerar-board-itens.py

Depois confira e publique:

    .\\scripts\\popular-board.ps1 -Auditar
    .\\scripts\\popular-board.ps1 -Tudo -DryRun
    .\\scripts\\popular-board.ps1 -Tudo
"""

import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "scripts" / "board-itens.json"

REPO_DOCS = "https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy/blob/develop/docs"

# --------------------------------------------------------------------------
# Regras de negocio — texto integral. Fonte: docs/01-requisitos.md §3
# --------------------------------------------------------------------------
RN = {
    "RN01": "**CPF único.** Não é permitido cadastrar dois pacientes com o mesmo CPF. "
            "Garantido por `UNIQUE paciente.cpf` no banco **e** por `PacienteService."
            "_garantir_cpf_inedito()`. Violação responde **409** `CPF ja cadastrado`.",
    "RN02": "**E-mail único.** Não é permitido cadastrar dois usuários com o mesmo e-mail. "
            "Atenção: `paciente.email` é *nullable* — paciente de balcão pode não ter e-mail, "
            "e o PostgreSQL permite vários `NULL` num índice `UNIQUE`, que é o comportamento "
            "desejado. O service retorna imediatamente quando o e-mail é `None`, sem consultar "
            "o banco. Violação responde **409** `E-mail em uso`.",
    "RN03": "**Horário ocupado não é reofertado.** Um horário já reservado não pode ser "
            "disponibilizado para outro paciente. Duas camadas de defesa: `SELECT ... FOR "
            "UPDATE` em `HorarioRepository.buscar_para_reserva()` e o índice parcial "
            "`uq_slot_ativo` (que só considera status `SOLICITADA` e `CONFIRMADA`, para que o "
            "slot volte a ficar livre após cancelamento). Violação responde **409** "
            "`Horario indisponivel`.",
    "RN04": "**Antecedência de cancelamento.** O paciente só pode cancelar uma consulta com "
            "**pelo menos 24 horas de antecedência**. O atendente cancela sem restrição de "
            "prazo. ⚠️ **Nunca escreva `24` no código** — use "
            "`settings.CANCELAMENTO_ANTECEDENCIA_HORAS`. Para demonstrar sem esperar, baixe "
            "essa variável no `.env`. Violação responde **422**.",
    "RN05": "**Médico sem sobreposição.** Um médico não pode ter duas consultas no mesmo "
            "horário. Garantido por `UniqueConstraint(medico_id, data, horario)` e por "
            "`AgendaService._criar_slot`. Violação responde **409**.",
    "RN06": "**Status da consulta.** Uma consulta deve possuir ao menos os status "
            "`SOLICITADA`, `CONFIRMADA`, `CANCELADA` e `FINALIZADA`, definidos no enum "
            "`StatusConsulta`. Consulta criada pelo paciente nasce `SOLICITADA`; criada pelo "
            "atendente nasce `CONFIRMADA`.",
    "RN07": "**CPF válido.** O CPF deve passar na verificação dos dígitos verificadores. Sem "
            "isso a RN01 aceitaria `00000000000`. Validado no schema Pydantic e, para feedback "
            "imediato, também em `frontend/src/lib/cpf.ts`.",
    "RN08": "**E-mail em formato válido.** Complementa a RN02. `EmailStr` do Pydantic no "
            "backend e `@mantine/form` no frontend.",
    "RN09": "**Horário comercial.** A agenda só aceita horários entre **08:00 e 18:00**. "
            "Validado em `GradeHorariaCriar`. Violação responde **422**.",
    "RN10": "**Transições de status são unidirecionais.** O status só avança; `CANCELADA` e "
            "`FINALIZADA` são terminais. O grafo permitido está em `TRANSICOES_PERMITIDAS` "
            "(`app/models/enums.py`): `SOLICITADA → CONFIRMADA → FINALIZADA`, e "
            "`SOLICITADA|CONFIRMADA → CANCELADA`. Transição fora do grafo levanta "
            "`TransicaoDeStatusInvalida` (**422**).",
    "RN11": "**Senha com hash.** A senha é armazenada com bcrypt via `passlib`, nunca em texto "
            "claro. `senha_hash` não pode aparecer em nenhum schema de resposta.",
    "RN12": "**Autorização por perfil.** Cada rota exige o perfil correto, extraído do JWT. "
            "Requisição sem token responde **401**; com perfil inadequado, **403**. "
            "Dependências: `usuario_atual`, `exigir_paciente`, `exigir_atendente` "
            "(`app/core/deps.py`). Toda operação de paciente usa `usuario.paciente_id` "
            "**do token**, nunca um id vindo do path ou do body.",
    "RN13": "**Expiração do token.** O JWT expira em 24h no MVP, configurável por "
            "`JWT_EXPIRE_MINUTES`. Token expirado responde **401**.",
    "RN14": "**Sem rota pública de atendente.** Não existe endpoint público que crie um "
            "atendente. O primeiro atendente vem do seed idempotente (`app/seeds/seed.py`).",
    "RN15": "**Fuso de referência.** Toda regra temporal é avaliada em `America/Maceio` "
            "(`settings.TIMEZONE`). Comparar em UTC dá erro de 3 horas na RN04.",
}

# --------------------------------------------------------------------------
# Definition of Done por area
# --------------------------------------------------------------------------
DOD = {
    "BACKEND": """- [ ] Branch `feature/{branch}` criada a partir de `develop`
- [ ] Camadas respeitadas: Controller → Service → Repository → Model
- [ ] Nenhum `HTTPException` nem `select(` dentro de `app/services/`
- [ ] Regra de negócio levanta exceção tipada de `app/exceptions/dominio.py`
- [ ] Teste unitário em `backend/tests/unit/` com o ID da RN no nome do teste
- [ ] `docker compose exec backend pytest` verde
- [ ] `docker compose exec backend ruff check .` sem erro
- [ ] Se mexeu em model: migração Alembic criada **e revisada à mão**
- [ ] PR aberto contra `develop` com o template preenchido, CI verde, 1 aprovação
- [ ] Item movido no board""",
    "FRONTEND": """- [ ] Branch `feature/{branch}` criada a partir de `develop`
- [ ] Toda chamada HTTP passa por `src/lib/api.ts` — nenhum `fetch` em componente
- [ ] Componente interativo tem `'use client'` no topo
- [ ] Erro da API vira notificação (`@mantine/notifications`), nunca `alert` nem erro cru
- [ ] Estado de carregamento e estado vazio tratados
- [ ] Teste em `frontend/__tests__/` com Vitest, importando `render` de `@test-utils`
- [ ] `docker compose exec frontend yarn test` verde
- [ ] `yarn lint` e `yarn typecheck` sem erro
- [ ] PR aberto contra `develop` com o template preenchido, CI verde, 1 aprovação
- [ ] Item movido no board""",
    "QA": """- [ ] Artefato versionado em `docs/` ou `docs/evidencias/`
- [ ] Cada caso cita a RN que cobre e tem **pelo menos um caso negativo**
- [ ] Evidência nomeada no padrão `CT<NN>-<passo>-<resultado>.png`
- [ ] Defeito encontrado vira Issue com o template de Bug, com severidade **e** prioridade
- [ ] Relatório de execução atualizado
- [ ] Item movido no board""",
    "INFRA": """- [ ] Configuração aplicada e verificada com print
- [ ] Print salvo em `docs/evidencias/`
- [ ] Documentação correspondente atualizada em `docs/`
- [ ] Item movido no board""",
    "DOCS": """- [ ] Documento em `docs/` (fonte da verdade)
- [ ] Wiki regenerada com `python scripts/gerar-wiki.py` e publicada
- [ ] Revisado por outra pessoa da equipe
- [ ] Item movido no board""",
}

RESP = {
    "BACKEND": "Ronaldo",
    "FRONTEND": "João Vitor / Antonio",
    "QA": "Uanderson / Felipe / Alyssandro",
    "INFRA": "Felipe",
    "DOCS": "Jackson / Antonio",
}


def bloco_rns(ids):
    if not ids:
        return "Nenhuma regra de negócio específica além das validações de formato."
    return "\n".join(f"- **{i}** — {RN[i]}" for i in ids)


def rodape(secao):
    return f"""
---

### Referência complementar

Esta issue é **autocontida**: tudo que você precisa para executá-la está acima. Os links abaixo
servem só para aprofundar.

- Requisitos e regras: [`docs/01-requisitos.md`]({REPO_DOCS}/01-requisitos.md)
- Backlog completo: [`docs/02-backlog.md`]({REPO_DOCS}/02-backlog.md)
- Arquitetura ({secao}): [`docs/03-arquitetura.md`]({REPO_DOCS}/03-arquitetura.md)
- Escopo congelado: [`ADR-008`]({REPO_DOCS}/adr/ADR-008-rebaseline-escopo.md)
"""


# ==========================================================================
# User Stories
# ==========================================================================
US = [
    {
        "id": "US-00",
        "titulo": "Autenticação e primeiro acesso",
        "sprint": "1",
        "prioridade": "P0",
        "perfil": "Paciente e Atendente",
        "historia": ("**Como** paciente ou atendente\n"
                     "**Quero** entrar no sistema com meu CPF ou e-mail\n"
                     "**Para** acessar as funcionalidades do meu perfil"),
        "rns": ["RN01", "RN02", "RN07", "RN11", "RN12", "RN13", "RN14"],
        "ca": [
            "**CA1 — Login do paciente por CPF.** Dado que sou paciente com CPF `529.982.247-25` e senha `senha123`, quando eu digitar `52998224725` no campo \"CPF ou E-mail\" e a senha, então o sistema permite o acesso e me leva ao painel do paciente.",
            "**CA2 — CPF com máscara é aceito.** Dado que meu CPF cadastrado é `52998224725`, quando eu digitar `529.982.247-25`, então o sistema reconhece como o mesmo login.",
            "**CA3 — Login do atendente por e-mail.** Dado que sou atendente com e-mail `recepcao@clinica.com`, quando eu digitar `Recepcao@Clinica.COM` e a senha, então o sistema permite o acesso ignorando maiúsculas e me leva ao painel do atendente.",
            "**CA4 — Primeiro acesso de paciente já cadastrado.** Dado que o atendente me cadastrou no balcão sem senha, quando eu acessar \"Primeiro acesso\" e digitar meu CPF, então o sistema exibe `Encontramos seu cadastro, <nome>! Crie uma senha para ativar seu login.` e, ao salvar, cria a credencial vinculada ao `paciente_id`.",
            "**CA5 — Auto-cadastro de paciente novo.** Dado que meu CPF não está cadastrado, quando eu informar CPF, nome, telefone e senha em \"Primeiro acesso\", então o sistema cria o paciente e a credencial no mesmo passo, e eu já posso solicitar consulta.",
            "**CA6 — CPF que já tem login.** Dado que meu CPF já possui login ativo, quando eu tentar o primeiro acesso, então o sistema informa isso e me direciona para a tela de login.",
            "**CA7 — Credencial inválida.** Quando eu informar login inexistente ou senha errada, então a resposta é `Login ou senha invalidos` — a mensagem **não** revela se o login existe.",
            "**CA8 — Proteção de rotas.** Dado que estou logado como paciente, quando eu tentar acessar rota de atendente, então recebo **403**; sem token, **401**.",
        ],
        "tarefas": [
            ("BACKEND", "Concluir e revisar as rotas de autenticação",
             "us00-autenticacao",
             """As rotas de autenticação **já existem** no repositório (`app/routers/auth_router.py`,
`app/services/auth_service.py`, `app/core/security.py`, `app/core/deps.py`). Esta tarefa é
**revisar, fechar lacunas e cobrir com teste**, não escrever do zero.

**Rotas envolvidas**

| Método | Rota | Perfil | O que faz |
|---|---|---|---|
| POST | `/api/auth/login` | público | Recebe `login` (CPF ou e-mail) e `senha`; normaliza (só dígitos se não tiver `@`, lowercase se tiver); devolve JWT com `tipo_usuario` e `paciente_id` |
| GET | `/api/auth/verificar-cpf/{cpf}` | público | Devolve `{cadastro_existe, login_ativo, nome}` |
| POST | `/api/auth/vincular-ou-criar` | público | Ativa login de paciente existente **ou** faz o auto-cadastro completo |

**Contrato do login**

```json
// requisicao
{ "login": "52998224725", "senha": "senha123" }
// resposta 200
{ "access_token": "eyJ...", "token_type": "bearer",
  "tipo_usuario": "PACIENTE", "nome": "Carlos Silva" }
```

**Checklist de revisão**

- [ ] Normalização do login cobre CPF com e sem máscara, e e-mail com maiúsculas
- [ ] Mensagem de erro de credencial é genérica (CA7) — não vaza se o login existe
- [ ] `senha_hash` não aparece em nenhum schema de resposta
- [ ] `exigir_paciente` e `exigir_atendente` aplicados em todas as rotas protegidas
- [ ] `vincular-ou-criar` cobre os dois caminhos (paciente existente / paciente novo)"""),
            ("FRONTEND", "Criar tela de login",
             "us00-tela-login",
             """Rota `src/app/login/page.tsx`. Precisa de `'use client'`.

**Comportamento**

- Campo único rotulado **"CPF ou E-mail"** + campo de senha (`PasswordInput` do Mantine)
- Máscara dinâmica: se o usuário digitar só dígitos, formatar como CPF enquanto digita; se
  digitar `@`, tratar como e-mail e não mascarar
- Ao submeter: `POST /api/auth/login` via `src/lib/api.ts`
- Sucesso: guardar o token e redirecionar por `tipo_usuario` — `PACIENTE` → `/consultas`,
  `ATENDENTE` → `/agenda`
- Erro **401**: notificação vermelha com `Login ou senha invalidos`. Não dizer se o login existe
- Link para `/primeiro-acesso`
- Botão desabilitado e com `loading` enquanto a requisição está em voo

**Validação no cliente (feedback imediato, não substitui o backend)**

- CPF: `validarCpf()` de `src/lib/cpf.ts` (RN07)
- E-mail: regra de formato do `@mantine/form` (RN08)"""),
            ("FRONTEND", "Criar tela de primeiro acesso e guarda de rota",
             "us00-primeiro-acesso",
             """Rota `src/app/primeiro-acesso/page.tsx` em **duas etapas**, mais a guarda dos route groups.

**Etapa 1 — verificar CPF**

Campo de CPF → `GET /api/auth/verificar-cpf/{cpf}`. A resposta decide a etapa 2:

| Resposta | O que exibir |
|---|---|
| `cadastro_existe: true, login_ativo: false` | `Encontramos seu cadastro, <nome>! Crie uma senha para ativar seu login.` + campos de senha e confirmação |
| `cadastro_existe: false` | Formulário completo: nome, telefone, e-mail (opcional), senha |
| `login_ativo: true` | `Este CPF já tem login.` + botão que leva para `/login` |

**Etapa 2 — enviar**

`POST /api/auth/vincular-ou-criar`. Sucesso: já autenticar e redirecionar para `/consultas`.

**Guarda de rota (CA8)**

- `src/app/(paciente)/layout.tsx` — redireciona para `/login` se não houver token, ou se
  `tipo_usuario !== 'PACIENTE'`
- `src/app/(atendente)/layout.tsx` — o mesmo para `ATENDENTE`

⚠️ A guarda do frontend é **conveniência de UX, não segurança**. Quem barra de verdade é o
backend (RN12). Não crie `middleware.ts`/`proxy.ts` — a guarda fica no `layout.tsx`."""),
        ],
    },
    {
        "id": "US-01",
        "titulo": "Cadastro de especialidades",
        "sprint": "1",
        "prioridade": "P0",
        "perfil": "Atendente",
        "historia": ("**Como** atendente\n"
                     "**Quero** cadastrar as especialidades médicas da clínica\n"
                     "**Para** que médicos e consultas possam ser organizados por área"),
        "rns": ["RN12"],
        "ca": [
            "**CA1.** Dado que preenchi o nome como `Cardiologia`, quando eu salvar, então a especialidade é criada e passa a aparecer como opção nos formulários de médico.",
            "**CA2.** Dado que `Cardiologia` já existe, quando eu tentar cadastrar de novo, então o sistema recusa informando que já está cadastrada.",
            "**CA3.** Quando o paciente consultar as especialidades, então vê apenas as `ativo = true`.",
            "**CA4 (RN12).** Quando um paciente tentar acessar o cadastro de especialidade, então recebe **403**.",
        ],
        "escopo_fora": "Editar e excluir especialidade **não** fazem parte do MVP (MF03 em `docs/15-melhorias-futuras.md`).",
        "tarefas": [
            ("BACKEND", "Criar rotas de cadastro e listagem de especialidade",
             "us01-especialidades",
             """| Método | Rota | Perfil |
|---|---|---|
| POST | `/api/especialidades` | ATENDENTE |
| GET | `/api/especialidades` | autenticado (devolve só `ativo = true`) |

```json
// POST — requisicao
{ "nome": "Cardiologia" }
// resposta 201
{ "id": 1, "nome": "Cardiologia", "ativo": true }
```

- Nome duplicado (case-insensitive) → **409** `Especialidade ja cadastrada`
- `POST` protegido por `exigir_atendente`; `GET` por `usuario_atual`
- Fluxo: `especialidade_router` → service → `especialidade_repository`"""),
            ("FRONTEND", "Criar tela de especialidades do atendente",
             "us01-tela-especialidades",
             """Rota `src/app/(atendente)/especialidades/page.tsx`. Precisa de `'use client'`.

- Formulário com um campo (`Nome`) + botão `Cadastrar`
- Tabela abaixo listando as especialidades ativas
- Erro **409** → notificação amarela `Especialidade ja cadastrada`; o formulário **não** é limpo
- Após sucesso: limpar o campo, recarregar a lista, notificação verde
- Estado vazio: `Nenhuma especialidade cadastrada ainda.`"""),
        ],
    },
    {
        "id": "US-02",
        "titulo": "Cadastro de médicos",
        "sprint": "1",
        "prioridade": "P0",
        "perfil": "Atendente",
        "historia": ("**Como** atendente\n"
                     "**Quero** cadastrar os médicos da clínica\n"
                     "**Para** que eles possam ter agenda e receber consultas"),
        "rns": ["RN02", "RN08", "RN12"],
        "ca": [
            "**CA1.** Quando eu tentar salvar um médico sem selecionar especialidade, então o sistema impede informando `Selecione uma especialidade`.",
            "**CA2 (RN02).** Dado que `silva@email.com` já está cadastrado, quando eu tentar cadastrar com esse e-mail, então o sistema recusa com **409** `E-mail em uso`.",
            "**CA3.** Dado que o CRM `CRM12345` já existe, quando eu tentar cadastrar de novo, então o sistema recusa com **409** `CRM ja cadastrado`.",
            "**CA4.** Quando eu listar médicos, então vejo nome, CRM e especialidade de cada um.",
        ],
        "escopo_fora": "Editar e inativar médico **não** fazem parte do MVP (MF04 em `docs/15-melhorias-futuras.md`).",
        "tarefas": [
            ("BACKEND", "Criar rotas de cadastro e listagem de médico",
             "us02-medicos",
             """| Método | Rota | Perfil |
|---|---|---|
| POST | `/api/medicos` | ATENDENTE |
| GET | `/api/medicos?especialidade_id=` | autenticado |

```json
// POST — requisicao
{ "nome": "Dr. Silva", "email": "silva@clinica.com",
  "crm": "CRM12345", "especialidade_id": 1 }
```

- E-mail duplicado → **409** (RN02); CRM duplicado → **409**
- `especialidade_id` inexistente → **404**
- `GET` aceita filtro opcional por especialidade e devolve só médicos ativos"""),
            ("FRONTEND", "Criar tela de médicos do atendente",
             "us02-tela-medicos",
             """Rota `src/app/(atendente)/medicos/page.tsx`. Precisa de `'use client'`.

- Formulário: nome, e-mail, CRM, `Select` de especialidade (carregado de `GET /api/especialidades`)
- Especialidade é **obrigatória** — bloquear o submit com `Selecione uma especialidade` (CA1)
- Tabela listando nome, CRM e especialidade
- **409** de e-mail → mensagem no campo de e-mail; **409** de CRM → mensagem no campo de CRM.
  Não usar notificação genérica: o usuário precisa saber **qual** campo está duplicado
- Se não houver especialidade cadastrada: `Alert` com link para a tela de especialidades"""),
        ],
    },
    {
        "id": "US-03",
        "titulo": "Cadastro de pacientes pelo atendente",
        "sprint": "1",
        "prioridade": "P0",
        "perfil": "Atendente",
        "historia": ("**Como** atendente\n"
                     "**Quero** cadastrar pacientes no balcão\n"
                     "**Para** atender quem chega sem cadastro prévio"),
        "rns": ["RN01", "RN02", "RN07", "RN08", "RN12"],
        "ca": [
            "**CA1.** Dado que preenchi nome, CPF válido e telefone, quando eu salvar, então o paciente é criado e aparece na listagem.",
            "**CA2 (RN01).** Dado que o CPF `529.982.247-25` já está cadastrado, quando eu tentar cadastrar de novo, então o sistema recusa com **409** `CPF ja cadastrado`.",
            "**CA3 (RN07).** Quando eu informar `111.111.111-11`, então o sistema recusa com **422** — dígitos verificadores inválidos.",
            "**CA4 (RN02).** O e-mail é **opcional**. Quando eu cadastrar dois pacientes sem e-mail, então ambos são aceitos. Quando eu repetir um e-mail já usado, então o sistema recusa com **409**.",
            "**CA5.** O paciente cadastrado no balcão **não** tem senha. Ele ativa o login depois pelo \"Primeiro acesso\" (US-00, CA4).",
        ],
        "escopo_fora": "Editar dados do paciente pelo atendente **não** faz parte do MVP (MF05). O paciente atualiza os próprios dados na US-04.",
        "tarefas": [
            ("BACKEND", "Criar rotas de cadastro e listagem de paciente",
             "us03-pacientes",
             """| Método | Rota | Perfil |
|---|---|---|
| POST | `/api/pacientes` | ATENDENTE |
| GET | `/api/pacientes` | ATENDENTE |

```json
// POST — requisicao (email pode ser omitido ou null)
{ "nome": "Carlos Silva", "cpf": "52998224725",
  "telefone": "82999998888", "email": null, "data_nascimento": "1990-05-14" }
```

**Ordem das validações no service** — importa para a mensagem de erro sair certa:

1. CPF válido pelos dígitos (RN07) → **422**, no schema Pydantic
2. `_garantir_cpf_inedito()` (RN01) → **409**
3. `_garantir_email_inedito()` (RN02) → retorna cedo se `email is None`; senão **409**

Este é também o exemplo de **funções pequenas com responsabilidade única** documentado em
`docs/05-clean-code.md` — o método público orquestra, os `_privados` fazem uma coisa cada.
Mantenha o padrão."""),
            ("FRONTEND", "Criar tela de pacientes do atendente",
             "us03-tela-pacientes",
             """Rota `src/app/(atendente)/pacientes/page.tsx`. Precisa de `'use client'`.

- Formulário: nome, CPF (com máscara), telefone, e-mail (opcional), data de nascimento
  (`DateInput` do `@mantine/dates`)
- Validar CPF no cliente com `validarCpf()` de `src/lib/cpf.ts` **antes** de enviar (RN07)
- Deixar visível que o e-mail é opcional — `description` no `TextInput`
- Tabela listando nome, CPF e telefone
- **409** de CPF → mensagem no campo de CPF; **409** de e-mail → mensagem no campo de e-mail
- Após cadastrar: aviso de que o paciente ativa o login em "Primeiro acesso" (CA5)"""),
        ],
    },
    {
        "id": "US-04",
        "titulo": "Atualização dos próprios dados pelo paciente",
        "sprint": "2",
        "prioridade": "P2",
        "perfil": "Paciente",
        "historia": ("**Como** paciente\n"
                     "**Quero** atualizar meus dados de contato\n"
                     "**Para** que a clínica consiga falar comigo"),
        "rns": ["RN02", "RN08", "RN12"],
        "ca": [
            "**CA1.** Dado que estou logado como paciente, quando eu abrir \"Meus dados\", então vejo meus dados atuais preenchidos.",
            "**CA2.** Quando eu alterar telefone e e-mail e salvar, então as alterações persistem e uma notificação confirma.",
            "**CA3 (RN02).** Quando eu informar um e-mail já usado por outro paciente, então o sistema recusa com **409**.",
            "**CA4.** O **CPF não é editável** — é a chave de identidade do paciente (RN01) e o login dele.",
            "**CA5 (RN12).** A rota altera sempre o paciente do token. Não existe forma de alterar os dados de outro paciente.",
        ],
        "tarefas": [
            ("BACKEND", "Criar rota de atualização cadastral do paciente",
             "us04-atualizar-dados",
             """| Método | Rota | Perfil |
|---|---|---|
| GET | `/api/pacientes/me` | PACIENTE |
| PUT | `/api/pacientes/me` | PACIENTE |

```json
// PUT — requisicao (CPF ausente de proposito)
{ "nome": "Carlos Silva", "telefone": "82988887777", "email": "carlos@email.com" }
```

⚠️ **Ponto de segurança (RN12).** O `paciente_id` vem **do token**, via `usuario_atual`. Não
aceite id no path nem no body — senão qualquer paciente altera o cadastro de outro trocando um
número na URL.

O schema de entrada **não deve conter o campo `cpf`** (CA4). Assim o Pydantic ignora a tentativa
sem precisar de `if` no service."""),
            ("FRONTEND", "Criar tela \"Meus dados\" do paciente",
             "us04-tela-meus-dados",
             """Rota `src/app/(paciente)/meus-dados/page.tsx`. Precisa de `'use client'`.

- Carregar `GET /api/pacientes/me` e preencher o formulário
- CPF exibido em campo **desabilitado**, com `description` explicando que não pode ser alterado (CA4)
- Salvar com `PUT /api/pacientes/me`
- **409** → mensagem no campo de e-mail
- `Skeleton` do Mantine enquanto carrega
- Botão `Salvar` desabilitado enquanto nada mudou"""),
        ],
    },
    {
        "id": "US-05",
        "titulo": "Cadastro de agenda e horários disponíveis",
        "sprint": "1",
        "prioridade": "P0",
        "perfil": "Atendente",
        "historia": ("**Como** atendente\n"
                     "**Quero** lançar a grade de horários de um médico\n"
                     "**Para** que os pacientes possam agendar consultas"),
        "rns": ["RN05", "RN09", "RN12"],
        "ca": [
            "**CA1.** Dado que escolhi o Dr. Silva, a data `10/08/2026` e o intervalo `08:00–12:00` com duração de 30 min, quando eu gerar a grade, então são criados 8 horários disponíveis.",
            "**CA2 (RN05).** Dado que o Dr. Silva já tem o horário `10/08 09:00`, quando eu gerar uma grade que inclua esse horário, então o sistema **não duplica** o slot — os já existentes são ignorados e os novos, criados.",
            "**CA3 (RN09).** Quando eu tentar gerar grade das `07:00` às `19:00`, então o sistema recusa com **422** — o atendimento é das 08:00 às 18:00.",
            "**CA4.** Quando eu abrir a agenda de um médico numa data, então vejo cada horário com status **Livre** ou **Ocupado**.",
        ],
        "escopo_fora": "Excluir slot livre **não** faz parte do MVP (MF06 em `docs/15-melhorias-futuras.md`).",
        "tarefas": [
            ("BACKEND", "Criar rotas de geração e consulta da grade de horários",
             "us05-agenda",
             """| Método | Rota | Perfil |
|---|---|---|
| POST | `/api/medicos/{id}/agenda` | ATENDENTE |
| GET | `/api/medicos/{id}/agenda?data=` | ATENDENTE |

```json
// POST — requisicao
{ "data": "2026-08-10", "hora_inicio": "08:00",
  "hora_fim": "12:00", "duracao_minutos": 30 }
// resposta 201
{ "criados": 8, "ignorados": 0 }
```

- Validar RN09 (08:00–18:00) no schema `GradeHorariaCriar` → **422**
- `AgendaService._criar_slot` ignora slot já existente em vez de estourar (CA2), o que torna a
  operação **idempotente**: rodar duas vezes não duplica
- A constraint `uq_medico_data_horario` é a garantia final no banco (RN05)"""),
            ("FRONTEND", "Criar tela de lançamento de agenda",
             "us05-tela-agenda",
             """Rota `src/app/(atendente)/agenda/page.tsx`. Precisa de `'use client'`.

- `Select` de médico + `DateInput` + `TimeInput` de início e fim + `NumberInput` de duração
- Limitar os `TimeInput` a 08:00–18:00 já no componente (RN09) — o backend revalida
- Botão `Gerar grade` → `POST /api/medicos/{id}/agenda`
- Após gerar: mostrar `X horários criados, Y já existiam` (usa `criados`/`ignorados` da resposta)
- Abaixo, a grade do dia: cada horário como `Badge` verde **Livre** ou cinza **Ocupado**
- **422** de horário comercial → notificação explicando a faixa permitida"""),
        ],
    },
    {
        "id": "US-06",
        "titulo": "Consulta de médicos e especialidades pelo paciente",
        "sprint": "2",
        "prioridade": "P2",
        "perfil": "Paciente",
        "historia": ("**Como** paciente\n"
                     "**Quero** consultar as especialidades e os médicos da clínica\n"
                     "**Para** escolher com quem quero me consultar"),
        "rns": ["RN12"],
        "ca": [
            "**CA1.** Quando eu abrir \"Médicos\", então vejo a lista de médicos ativos com nome, CRM e especialidade.",
            "**CA2.** Quando eu filtrar por `Cardiologia`, então vejo apenas os cardiologistas.",
            "**CA3.** Quando não houver médico na especialidade escolhida, então vejo `Nenhum médico disponível nesta especialidade.` — nunca uma tela em branco.",
            "**CA4.** De cada médico, consigo ir direto para a escolha de horário (US-07).",
        ],
        "tarefas": [
            ("BACKEND", "Liberar listagem de médicos e especialidades para o paciente",
             "us06-listagens-paciente",
             """As rotas `GET /api/especialidades` e `GET /api/medicos?especialidade_id=` já existem
(US-01 e US-02). Esta tarefa garante que elas sejam acessíveis ao **paciente autenticado**.

- Trocar a dependência de `exigir_atendente` para `usuario_atual` **apenas nos GET**
- Os `POST` continuam restritos a atendente (RN12)
- Devolver só registros ativos
- Teste: paciente autenticado recebe **200** no `GET` e **403** no `POST`"""),
            ("FRONTEND", "Criar tela de busca de médicos do paciente",
             "us06-tela-medicos-paciente",
             """Rota `src/app/(paciente)/medicos/page.tsx`. Precisa de `'use client'`.

- `Select` de especialidade no topo (carregado de `GET /api/especialidades`), com opção
  `Todas as especialidades`
- Lista de médicos em `Card`: nome, CRM, especialidade e botão `Ver horários` que leva para
  `/agendar?medico_id=X`
- Estado vazio explícito (CA3), nunca tela em branco
- `Skeleton` durante o carregamento"""),
        ],
    },
    {
        "id": "US-07",
        "titulo": "Visualização de horários disponíveis",
        "sprint": "2",
        "prioridade": "P1",
        "perfil": "Paciente",
        "historia": ("**Como** paciente\n"
                     "**Quero** ver os horários livres de um médico numa data\n"
                     "**Para** escolher quando quero ser atendido"),
        "rns": ["RN03", "RN12"],
        "ca": [
            "**CA1.** Dado que escolhi o Dr. Silva e a data `10/08/2026`, quando a tela carregar, então vejo somente os horários **livres**.",
            "**CA2 (RN03).** Dado que o horário `09:00` foi reservado por outro paciente, quando eu recarregar, então `09:00` **não** aparece mais.",
            "**CA3.** Dado que uma consulta das `10:00` foi cancelada, quando eu recarregar, então `10:00` volta a aparecer como livre.",
            "**CA4.** Quando não houver horário livre na data, então vejo `Nenhum horário disponível nesta data.`",
            "**CA5.** Datas passadas não podem ser selecionadas.",
        ],
        "tarefas": [
            ("BACKEND", "Criar rota de horários livres por médico e data",
             "us07-horarios-livres",
             """| Método | Rota | Perfil |
|---|---|---|
| GET | `/api/medicos/{id}/horarios-livres?data=YYYY-MM-DD` | autenticado |

```json
// resposta 200
[ { "id": 12, "data": "2026-08-10", "horario": "08:00" },
  { "id": 13, "data": "2026-08-10", "horario": "08:30" } ]
```

**O filtro que importa (RN03).** Um slot é livre quando **não** existe consulta ativa ligada a
ele — ativa significa status `SOLICITADA` ou `CONFIRMADA`. Consulta `CANCELADA` **não** ocupa
o slot; é isso que faz o horário voltar a aparecer (CA3), e é a mesma condição do índice
parcial `uq_slot_ativo`.

⚠️ Se você filtrar por "existe qualquer consulta neste slot", a CA3 quebra e o CT10 falha."""),
            ("FRONTEND", "Criar grade de escolha de horário",
             "us07-grade-horarios",
             """Rota `src/app/(paciente)/agendar/page.tsx` (primeira metade — a segunda é a US-08).
Precisa de `'use client'`.

- `Select` de médico + `DateInput` com `minDate={new Date()}` (CA5)
- Ao mudar médico ou data: `GET /api/medicos/{id}/horarios-livres?data=`
- Horários como botões numa grade; o selecionado fica destacado
- Estado vazio explícito (CA4)
- Botão `Atualizar` para recarregar — importante porque outro paciente pode ter reservado
  enquanto a tela estava aberta (CA2)"""),
        ],
    },
    {
        "id": "US-08",
        "titulo": "Solicitação de consulta pelo paciente",
        "sprint": "2",
        "prioridade": "P0",
        "perfil": "Paciente",
        "historia": ("**Como** paciente\n"
                     "**Quero** solicitar uma consulta num horário livre\n"
                     "**Para** ser atendido sem precisar ligar para a clínica"),
        "rns": ["RN03", "RN06", "RN12"],
        "ca": [
            "**CA1.** Dado que escolhi o Dr. Silva em `10/08 09:00`, quando eu confirmar, então a consulta é criada com status **SOLICITADA** e o horário deixa de aparecer como livre.",
            "**CA2 (RN03) — concorrência.** Dado que dois pacientes confirmam o mesmo horário ao mesmo tempo, quando as duas requisições chegarem, então **uma** é criada e a outra recebe **409** `Horario indisponivel`.",
            "**CA3.** Após confirmar, sou levado à minha lista de consultas e vejo a nova lá.",
            "**CA4 (RN06).** Consulta criada pelo paciente nasce **SOLICITADA** — nunca CONFIRMADA. Quem confirma é o atendente (US-13).",
        ],
        "tarefas": [
            ("BACKEND", "Criar rota de solicitação de consulta com lock",
             "us08-solicitar-consulta",
             """| Método | Rota | Perfil |
|---|---|---|
| POST | `/api/consultas` | PACIENTE |

```json
// requisicao
{ "horario_disponivel_id": 12 }
// resposta 201
{ "id": 45, "status": "SOLICITADA", "medico": "Dr. Silva",
  "data": "2026-08-10", "horario": "09:00" }
```

**Esta é a tarefa mais delicada do projeto.** A RN03 sob concorrência exige duas defesas:

1. **Lock pessimista** — `HorarioRepository.buscar_para_reserva()` usa `SELECT ... FOR UPDATE`.
   A segunda transação **espera** a primeira e então enxerga o slot ocupado, recebendo **409**.
2. **Índice parcial `uq_slot_ativo`** — garantia final no banco, caso algum caminho futuro
   esqueça o lock.

O `paciente_id` vem **do token** (RN12), nunca do body.
O status inicial é `SOLICITADA` (RN06/CA4) — não aceite status vindo do cliente.

**Como validar a concorrência de verdade:** dois `curl` simultâneos para o mesmo
`horario_disponivel_id`. Exatamente um deve responder 201 e o outro 409. É o CT05."""),
            ("FRONTEND", "Criar fluxo de confirmação de agendamento",
             "us08-confirmar-agendamento",
             """Segunda metade de `src/app/(paciente)/agendar/page.tsx`.

- Com um horário selecionado (US-07), exibir resumo: médico, especialidade, data, horário
- Botão `Confirmar agendamento` → `POST /api/consultas`
- Usar `modals.openConfirmModal` do `@mantine/modals` antes de enviar
- **201** → notificação verde + `router.push('/consultas')`
- **409** → notificação vermelha `Este horário acabou de ser reservado por outra pessoa.` e
  **recarregar a grade automaticamente** (CA2). Sem o recarregamento, o paciente fica olhando
  um horário que já não existe
- Botão com `loading` e desabilitado durante a requisição, para evitar duplo clique"""),
        ],
    },
    {
        "id": "US-09",
        "titulo": "Cadastro de consultas pelo atendente",
        "sprint": "2",
        "prioridade": "P1",
        "perfil": "Atendente",
        "historia": ("**Como** atendente\n"
                     "**Quero** agendar consulta para um paciente\n"
                     "**Para** atender quem liga ou chega ao balcão"),
        "rns": ["RN03", "RN05", "RN06", "RN12"],
        "ca": [
            "**CA1.** Dado que escolhi paciente, médico, data e um horário livre, quando eu confirmar, então a consulta é criada com status **CONFIRMADA**.",
            "**CA2 (RN06).** Consulta criada pelo atendente nasce **CONFIRMADA** — a solicitação já é presencial, não precisa de confirmação posterior. É a diferença em relação à US-08.",
            "**CA3 (RN03).** Quando o horário já estiver ocupado, então o sistema recusa com **409**.",
            "**CA4.** Quando eu listar as consultas, então vejo todas as consultas da clínica com paciente, médico, data, horário e status.",
        ],
        "tarefas": [
            ("BACKEND", "Criar rotas de agendamento e listagem do atendente",
             "us09-agendamento-atendente",
             """| Método | Rota | Perfil |
|---|---|---|
| POST | `/api/atendente/consultas` | ATENDENTE |
| GET | `/api/atendente/consultas` | ATENDENTE |

```json
// POST — requisicao
{ "paciente_id": 3, "horario_disponivel_id": 12 }
// resposta 201 — nasce CONFIRMADA
{ "id": 46, "status": "CONFIRMADA", ... }
```

- Aqui o `paciente_id` **vem no body** — é o atendente agendando para outra pessoa. É a única
  exceção à regra "id do paciente vem do token", e ela é legítima porque a rota exige
  `exigir_atendente`
- Reaproveite `ConsultaService` com o mesmo lock da US-08. **Não duplique a lógica de reserva**
- O que muda é só o status inicial (CA2). Passe-o como parâmetro, não com `if perfil == ...`
- `GET` devolve todas as consultas, ordenadas por data e horário"""),
            ("FRONTEND", "Criar tela de consultas do atendente",
             "us09-tela-consultas-atendente",
             """Rota `src/app/(atendente)/consultas/page.tsx`. Precisa de `'use client'`.
Esta tela é a base das US-12 e US-13 — deixe espaço para as ações.

- Formulário de agendamento: `Select` de paciente, `Select` de médico, `DateInput`, grade de
  horários livres (mesma chamada da US-07)
- Tabela de consultas: paciente, médico, data, horário, `Badge` de status e coluna `Ações`
  (vazia por enquanto)
- Cores do `Badge`: `SOLICITADA` azul · `CONFIRMADA` verde · `CANCELADA` vermelho ·
  `FINALIZADA` cinza
- **409** → notificação + recarregar a grade de horários"""),
        ],
    },
    {
        "id": "US-10",
        "titulo": "Visualização das consultas pelo paciente",
        "sprint": "2",
        "prioridade": "P2",
        "perfil": "Paciente",
        "historia": ("**Como** paciente\n"
                     "**Quero** ver minhas consultas e o histórico\n"
                     "**Para** acompanhar meus agendamentos"),
        "rns": ["RN12"],
        "ca": [
            "**CA1.** Quando eu abrir \"Minhas consultas\", então vejo minhas consultas com médico, especialidade, data, horário e status.",
            "**CA2.** As consultas futuras aparecem primeiro; o histórico, depois.",
            "**CA3 (RN12).** Vejo **apenas** as minhas consultas. Não existe forma de ver a de outro paciente.",
            "**CA4.** Quando eu abrir uma consulta, então vejo os detalhes e, se aplicável, a ação de cancelar (US-11).",
            "**CA5.** Sem consultas, vejo `Você ainda não tem consultas agendadas.` com link para agendar.",
        ],
        "tarefas": [
            ("BACKEND", "Criar rotas de listagem e detalhe de consulta do paciente",
             "us10-minhas-consultas",
             """| Método | Rota | Perfil |
|---|---|---|
| GET | `/api/consultas` | PACIENTE |
| GET | `/api/consultas/{id}` | PACIENTE |

```json
// resposta 200 (lista)
[ { "id": 45, "status": "SOLICITADA", "medico": "Dr. Silva",
    "especialidade": "Cardiologia", "data": "2026-08-10",
    "horario": "09:00", "pode_cancelar": true } ]
```

⚠️ **`pode_cancelar` é calculado no backend** (RN04 + RN15, fuso `America/Maceio`), não no
React. O frontend só obedece ao booleano. Duplicar a regra de 24h no cliente é exatamente o
tipo de vazamento de regra de negócio que a arquitetura proíbe.

⚠️ **Escopo de dados (RN12).** O filtro usa `usuario.paciente_id` **do token**. No
`GET /api/consultas/{id}`, se a consulta não for do paciente do token, responda **404** — não
403. Um 403 confirmaria que aquele id existe."""),
            ("FRONTEND", "Criar tela de minhas consultas",
             "us10-tela-minhas-consultas",
             """Rotas `src/app/(paciente)/consultas/page.tsx` e `consultas/[id]/page.tsx`.
Precisam de `'use client'` nos componentes interativos.

- Lista em `Card`, separada em **Próximas** e **Histórico** (CA2)
- `Badge` de status com as mesmas cores da tela do atendente
- Estado vazio com link para `/agendar` (CA5)
- Detalhe: médico, especialidade, data, horário, status e o botão de cancelar quando
  `pode_cancelar === true` (US-11)

⚠️ **Next 16:** `params` é `Promise`. Use `PageProps<'/consultas/[id]'>` e `await props.params`.
A forma síncrona da v15 foi removida e quebra no `tsc` e no build."""),
        ],
    },
    {
        "id": "US-11",
        "titulo": "Cancelamento de consulta pelo paciente",
        "sprint": "2",
        "prioridade": "P0",
        "perfil": "Paciente",
        "historia": ("**Como** paciente\n"
                     "**Quero** cancelar uma consulta que não poderei comparecer\n"
                     "**Para** liberar o horário para outra pessoa"),
        "rns": ["RN03", "RN04", "RN10", "RN12", "RN15"],
        "ca": [
            "**CA1 (RN04).** Dado que minha consulta é daqui a 48h, quando eu cancelar, então o status vira **CANCELADA** e o horário volta a ficar livre.",
            "**CA2 (RN04).** Dado que minha consulta é daqui a 10h, quando eu tentar cancelar, então o sistema recusa com **422** `Cancelamento permitido apenas com 24 horas de antecedencia`.",
            "**CA3 (RN03).** Após o cancelamento, o horário reaparece em `horarios-livres` e pode ser reservado por outro paciente.",
            "**CA4 (RN10).** Consulta já `CANCELADA` ou `FINALIZADA` não pode ser cancelada de novo — **422**.",
            "**CA5 (RN15).** O cálculo das 24h usa o fuso `America/Maceio`. Comparar em UTC daria 3h de erro.",
        ],
        "tarefas": [
            ("BACKEND", "Implementar cancelamento com Strategy (paciente e atendente)",
             "us11-cancelamento-strategy",
             """**Esta tarefa cobre a US-11 e a US-12 de uma vez**, porque é o mesmo código com duas
estratégias. É também um dos **2 Design Patterns avaliados** — trate com cuidado.

| Método | Rota | Perfil | Valida RN04? |
|---|---|---|---|
| PATCH | `/api/consultas/{id}/cancelar` | PACIENTE | ✅ sim |
| PATCH | `/api/atendente/consultas/{id}/cancelar` | ATENDENTE | ❌ não |

**Strategy — `app/services/cancelamento_strategy.py`**

```
CancelamentoStrategy (abstrata)
├── CancelamentoPorPaciente   → valida a antecedência de 24h (RN04)
└── CancelamentoPorAtendente  → não valida prazo
```

⚠️ **Se você escrever `if perfil == 'PACIENTE'` dentro do service, o padrão foi desfeito.**
O router escolhe a estratégia e injeta; o service apenas executa. É essa ausência de `if` que
será mostrada na apresentação.

**Regras a aplicar**

- RN04: `settings.CANCELAMENTO_ANTECEDENCIA_HORAS` — **nunca** o literal `24`
- RN15: comparar `agora` e `data + horario` no fuso `America/Maceio`
- RN10: só cancela quem está `SOLICITADA` ou `CONFIRMADA` → senão **422**
- RN03: o slot volta a ficar livre. Como o índice `uq_slot_ativo` ignora `CANCELADA`, isso é
  automático — **confirme com teste** (CT10), não presuma"""),
            ("FRONTEND", "Criar ação de cancelar consulta do paciente",
             "us11-cancelar-paciente",
             """Em `src/app/(paciente)/consultas/`.

- Botão `Cancelar consulta` visível **apenas quando `pode_cancelar === true`** (vem da API)
- Quando `pode_cancelar === false`, exibir texto explicando: `O cancelamento pelo site é
  permitido até 24h antes. Entre em contato com a clínica.`
- Confirmação com `modals.openConfirmModal` — cancelamento é irreversível (RN10)
- `PATCH /api/consultas/{id}/cancelar`
- **422** → notificação com a mensagem que veio da API, sem reescrever a regra no cliente
- Sucesso → recarregar a lista; o card muda para `Badge` vermelho `CANCELADA`

⚠️ **Não calcule as 24h em JavaScript.** A regra é do backend (RN04 + RN15). Duplicá-la aqui
cria duas fontes da verdade que vão divergir por fuso horário."""),
        ],
    },
    {
        "id": "US-12",
        "titulo": "Cancelamento de consultas pelo atendente",
        "sprint": "2",
        "prioridade": "P1",
        "perfil": "Atendente",
        "historia": ("**Como** atendente\n"
                     "**Quero** cancelar qualquer consulta sem restrição de prazo\n"
                     "**Para** atender pedidos por telefone e resolver imprevistos"),
        "rns": ["RN03", "RN10", "RN12"],
        "ca": [
            "**CA1.** Dado que uma consulta é daqui a 2h, quando eu cancelar como atendente, então o cancelamento é aceito — a RN04 **não** se aplica ao atendente.",
            "**CA2 (RN03).** Após o cancelamento, o horário volta a ficar livre.",
            "**CA3 (RN10).** Consulta `CANCELADA` ou `FINALIZADA` não pode ser cancelada de novo — **422**.",
            "**CA4 (RN12).** Um paciente que tentar acessar a rota de cancelamento do atendente recebe **403**.",
        ],
        "tarefas": [
            ("FRONTEND", "Criar ação de cancelar consulta do atendente",
             "us12-cancelar-atendente",
             """Na coluna `Ações` da tabela de `src/app/(atendente)/consultas/page.tsx`.

- Botão `Cancelar` em toda consulta com status `SOLICITADA` ou `CONFIRMADA` (RN10)
- Confirmação com `modals.openConfirmModal`, mostrando paciente, médico e horário — o atendente
  cancela consulta de terceiro, o risco de errar a linha é real
- `PATCH /api/atendente/consultas/{id}/cancelar`
- **Sem regra de 24h aqui** (CA1): o botão aparece independentemente da proximidade
- Sucesso → recarregar a tabela

> O backend desta US já está pronto na tarefa `[US-11] [BACKEND]` — as duas rotas de
> cancelamento saem juntas pelo padrão Strategy."""),
        ],
    },
    {
        "id": "US-13",
        "titulo": "Confirmação e finalização de consultas",
        "sprint": "2",
        "prioridade": "P1",
        "perfil": "Atendente",
        "historia": ("**Como** atendente\n"
                     "**Quero** confirmar consultas solicitadas e finalizar as realizadas\n"
                     "**Para** manter o status das consultas fiel à realidade"),
        "rns": ["RN06", "RN10", "RN12"],
        "ca": [
            "**CA1 (RN06).** Dado que uma consulta está `SOLICITADA`, quando eu confirmar, então o status vira `CONFIRMADA`.",
            "**CA2 (RN06).** Dado que uma consulta está `CONFIRMADA`, quando eu finalizar, então o status vira `FINALIZADA`.",
            "**CA3 (RN10).** Quando eu tentar finalizar uma consulta `SOLICITADA` (pulando CONFIRMADA), então o sistema recusa com **422**.",
            "**CA4 (RN10).** `CANCELADA` e `FINALIZADA` são terminais — nenhuma transição sai delas.",
            "**CA5.** Esta US é o que fecha a RN06: com ela, os **quatro** status ficam alcançáveis pela interface.",
        ],
        "tarefas": [
            ("BACKEND", "Criar rota de transição de status da consulta",
             "us13-transicao-status",
             """| Método | Rota | Perfil |
|---|---|---|
| PATCH | `/api/atendente/consultas/{id}/status` | ATENDENTE |

```json
// requisicao
{ "novo_status": "CONFIRMADA" }
```

**Máquina de estados (RN06 + RN10)** — a fonte é `TRANSICOES_PERMITIDAS` em
`app/models/enums.py`:

```
SOLICITADA ──▶ CONFIRMADA ──▶ FINALIZADA   (terminal)
     │              │
     └──────────────┴──────▶ CANCELADA     (terminal)
```

- Transição fora do grafo → `TransicaoDeStatusInvalida` (**422**)
- ⚠️ **Não escreva a validação como cadeia de `if`.** Use o dicionário
  `TRANSICOES_PERMITIDAS`: `if novo not in TRANSICOES_PERMITIDAS[atual]: raise ...`.
  É o exemplo de "sem números mágicos / sem condicional espalhada" de `docs/05-clean-code.md`
- Teste unitário deve cobrir **todas** as transições inválidas, não só uma"""),
            ("FRONTEND", "Adicionar ações de confirmar e finalizar",
             "us13-acoes-status",
             """Na coluna `Ações` da tabela de `src/app/(atendente)/consultas/page.tsx`.

Botões condicionados ao status atual (RN10) — nunca mostre uma ação que a API vai recusar:

| Status atual | Botões visíveis |
|---|---|
| `SOLICITADA` | `Confirmar` · `Cancelar` |
| `CONFIRMADA` | `Finalizar` · `Cancelar` |
| `CANCELADA` | nenhum |
| `FINALIZADA` | nenhum |

- `PATCH /api/atendente/consultas/{id}/status` com `{ "novo_status": "..." }`
- Sucesso → atualizar o `Badge` da linha sem recarregar a página inteira
- **422** → notificação com a mensagem da API"""),
        ],
    },
]


# ==========================================================================
# Itens de processo (QA, INFRA, DOCS)
# ==========================================================================
PROCESSO = [
    ("1", "QA", "Revisar o plano de testes com o escopo do rebaseline",
     """**Objetivo.** Alinhar `docs/07-plano-de-testes.md` ao escopo congelado no ADR-008 (14 User
Stories, US-14 e US-15 fora) e à separação entre backend e frontend.

**O que fazer**

- Remover do escopo do plano tudo que se refere às antigas US-14 e US-15
- Separar a contagem de testes unitários por stack: pytest no backend, Vitest no frontend
- Conferir que **toda RN01–RN15 tem ao menos um caso negativo** na matriz de cobertura
- Atualizar as sessões exploratórias para EXP-01, EXP-02 e EXP-03 (eram quatro)
- Ajustar os critérios de entrada e saída ao calendário real (31/07 a 10/08)"""),
    ("1", "QA", "Escrever CT01 a CT04, CT08, CT13 e CT14",
     """**Objetivo.** Ter os casos de teste da Sprint 1 escritos **antes** do código da US existir,
para não enviesar o teste pela implementação.

| CT | O que verifica | RN |
|---|---|---|
| CT01 | Cadastrar paciente com dados válidos | RN07 |
| CT02 | Bloquear CPF duplicado | RN01 |
| CT03 | Bloquear e-mail duplicado e permitir e-mail nulo | RN02 |
| CT04 | Primeiro acesso: ativar login de paciente do balcão | RN11 |
| CT08 | Bloquear alocação dupla do mesmo médico | RN05 |
| CT13 | Bloquear horário fora do funcionamento | RN09 |
| CT14 | Não existe rota pública de cadastro de atendente | RN14 |

Cada CT precisa de: pré-condição, passos numerados, resultado esperado, resultado obtido
(preenchido na execução) e o campo de evidência.
**Todo CT tem pelo menos um caminho negativo.**"""),
    ("1", "QA", "Executar CT01 a CT04, CT08, CT13 e CT14 com evidência",
     """**Objetivo.** Executar os CTs da Sprint 1 conforme as US entram em `In QA` e registrar a
evidência.

- Executar só depois que a US estiver com backend **e** frontend prontos — é a regra da fatia
  vertical (ADR-008 §2)
- Evidência em `docs/evidencias/`, nomeada `CT<NN>-<passo>-<resultado>.png`
- Preencher o resultado obtido e o status (Passou / Falhou / Bloqueado) em
  `docs/08-casos-de-teste.md` §4
- Defeito encontrado → Issue com o template de Bug, com **severidade e prioridade separadas**"""),
    ("1", "QA", "Sessão exploratória EXP-01 — cadastros",
     """**Charter.** Explorar os cadastros de especialidade, médico e paciente em busca de falhas
que os casos de teste roteirizados não cobrem. **Timebox: 60 minutos.**

**Heurísticas a aplicar**

- Campos no limite: nome com 1 caractere, nome com 300 caracteres, só espaços
- Caracteres especiais e acentuação em todos os campos de texto
- CPF em formatos variados: com máscara, sem máscara, com espaços, com letras
- Duplo clique no botão de salvar (cria dois registros?)
- Voltar no navegador logo após salvar e submeter de novo
- Recarregar a página no meio do preenchimento

**Registro obrigatório** em `docs/07-plano-de-testes.md` §6: charter, duração, o que foi
testado, o que foi encontrado, e uma Issue por defeito."""),
    ("2", "QA", "Escrever CT05 a CT07 e CT09 a CT12",
     """**Objetivo.** Casos de teste da Sprint 2 — agendamento, cancelamento e autorização.

| CT | O que verifica | RN |
|---|---|---|
| CT05 | Bloquear agendamento em horário já ocupado (concorrência) | RN03 |
| CT06 | Paciente cancela com mais de 24h | RN04, RN15 |
| CT07 | Bloquear cancelamento do paciente com menos de 24h | RN04 |
| CT09 | Ciclo de vida completo do status | RN06, RN10 |
| CT10 | Reagendar horário liberado por cancelamento | RN03, RN10 |
| CT11 | Paciente não acessa rota de atendente | RN12 |
| CT12 | Requisição sem token e com token inválido | RN12, RN13 |

**Atenção no CT05.** Testar concorrência de verdade exige duas requisições **simultâneas** ao
mesmo `horario_disponivel_id`. Dois `curl` em paralelo bastam; exatamente um deve responder
201 e o outro 409.

**Atenção no CT06/CT07.** Para não esperar 24h reais, baixe `CANCELAMENTO_ANTECEDENCIA_HORAS`
no `.env` e registre isso na evidência."""),
    ("2", "QA", "Executar CT05 a CT07 e CT09 a CT12 com evidência",
     """Mesmo procedimento da execução da Sprint 1: evidência em `docs/evidencias/`, resultado
preenchido em `docs/08-casos-de-teste.md` §4, defeito vira Issue de Bug.

**Prazo:** até 09/08, para sobrar tempo de correção antes da entrega."""),
    ("2", "QA", "Sessão exploratória EXP-02 — agendamento e concorrência",
     """**Charter.** Explorar o fluxo de agendamento sob condições adversas. **Timebox: 60 minutos.**

**Heurísticas**

- Dois navegadores (um anônimo) reservando o mesmo horário ao mesmo tempo
- Deixar a grade de horários aberta, reservar pelo outro navegador, e então confirmar no primeiro
- Duplo clique rápido no botão `Confirmar agendamento`
- Voltar no navegador após confirmar e confirmar de novo
- Agendar, cancelar e reagendar o mesmo horário em sequência
- Manipular o `horario_disponivel_id` direto na requisição (id inexistente, id de outro médico)

Registro em `docs/07-plano-de-testes.md` §6."""),
    ("2", "QA", "Sessão exploratória EXP-03 — cancelamento e limite de 24h",
     """**Charter.** Explorar as fronteiras da RN04 e das transições de status.
**Timebox: 60 minutos.**

**Heurísticas**

- Consulta exatamente na fronteira: 24h00, 23h59 e 24h01 de antecedência
- Verificar se o cálculo respeita `America/Maceio` (RN15) e não UTC — diferença de 3h
- Cancelar consulta já cancelada; finalizar consulta cancelada; confirmar consulta finalizada
- Paciente tentando cancelar consulta de outro paciente (trocar o id na URL)
- Atendente cancelando consulta que começa em 1 hora (deve permitir)

Registro em `docs/07-plano-de-testes.md` §6."""),
    ("2", "QA", "Escrever o relatório final de testes",
     """**Objetivo.** Documento único que a apresentação usa para provar a qualidade da entrega.

**Conteúdo**

- Resumo da execução: total de CTs, quantos passaram, falharam, ficaram bloqueados
- Matriz de cobertura RN × CT, com todas as RN01–RN15 cobertas
- Contagem de testes automatizados **por stack**: pytest (backend) e Vitest (frontend)
- Defeitos encontrados, com severidade, prioridade e status de correção
- Resumo das três sessões exploratórias
- Print do CI verde **e** print de um PR bloqueado pelo quality gate — mostrar que o gate
  realmente barra vale mais do que só mostrar o verde
- Riscos residuais e o que não foi testado (com justificativa)"""),
    ("1", "INFRA", "Ativar branch protection em main e develop",
     """**Objetivo.** Tornar impossível quebrar `develop` e `main`, e produzir a evidência disso.

**Configuração em Settings → Branches**

Para `main` e `develop`:

- [ ] Require a pull request before merging — **1 aprovação**
- [ ] Require status checks to pass — marcar o job **`quality-gate`**
- [ ] Require branches to be up to date before merging
- [ ] Do not allow bypassing the above settings

**Evidência**

- Print da tela de configuração
- Print de um PR **bloqueado** pelo gate, salvo em `docs/evidencias/`

O PR bloqueado é a evidência que mais vale na avaliação: prova que a regra existe e funciona,
não apenas que foi configurada."""),
    ("1", "INFRA", "Validar o pipeline de CI com os quatro jobs",
     """**Objetivo.** Confirmar que `.github/workflows/ci.yml` roda os quatro jobs e que o quality
gate barra de verdade.

| Job | O que roda |
|---|---|
| `backend` | ruff + pytest com cobertura |
| `frontend` | eslint + tsc + vitest |
| `docker` | sobe o compose, migra e roda o seed **duas vezes** (prova a idempotência do ADR-004) |
| `quality-gate` | agrega os três; é o check obrigatório do branch protection |

**Como validar**

1. Abrir um PR de teste que **quebra** de propósito um teste do backend
2. Conferir que o `quality-gate` fica vermelho e o merge é bloqueado
3. Corrigir e conferir que fica verde
4. Salvar os dois prints em `docs/evidencias/`"""),
    ("1", "INFRA", "Validar a execução local do frontend em todas as máquinas",
     """**Objetivo.** As 6 pessoas conseguirem abrir `http://localhost:3000` no primeiro encontro.
Enquanto isso não acontece, o trabalho de frontend está bloqueado.

**Caminho padrão — Docker (recomendado)**

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seeds.seed
```

Frontend em `http://localhost:3000` · Swagger em `http://localhost:8000/docs`
Login: `recepcao@clinica.com` / `admin123`

**Caminho alternativo — fora do Docker (só o frontend)**

```bash
docker compose up -d postgres backend
cd frontend
corepack enable            # habilita o yarn 1.22.22 do campo packageManager
yarn install --frozen-lockfile
yarn dev
```

⚠️ **Use `yarn`, nunca `npm` nem `pnpm`.** O `yarn.lock` está versionado; usar outro gerenciador
gera uma árvore de dependências diferente da do CI.

**Checklist por pessoa**

- [ ] `docker compose ps` mostra `postgres`, `backend` e `frontend` de pé
- [ ] `http://localhost:3000` abre a página inicial
- [ ] `http://localhost:8000/docs` abre o Swagger
- [ ] Login com `recepcao@clinica.com` funciona
- [ ] `docker compose exec frontend yarn test` passa

**Se o `frontend` não subir**, colete e cole na issue:

```bash
docker compose logs frontend --tail 50
docker compose ps
```

Erros conhecidos e o que fazer estão em `docs/17-como-rodar.md`."""),
    ("2", "DOCS", "Publicar a Wiki a partir de docs/",
     """**Objetivo.** Wiki do GitHub espelhando `docs/`, que é a fonte da verdade.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python scripts\\gerar-wiki.py
.\\scripts\\publicar-wiki.ps1 -DryRun
.\\scripts\\publicar-wiki.ps1
```

- [ ] `python scripts/gerar-wiki.py --check` não acusa desatualização
- [ ] `_Sidebar.md` inclui as páginas novas (Melhorias Futuras, Como Rodar, ADR-008)
- [ ] `Home.md` reflete o escopo do rebaseline
- [ ] Nenhuma página menciona US-14, US-15 ou a equipe antiga de 7 pessoas

⚠️ O script **substitui** os `.md` do Wiki pelos de `wiki/`. Quem editar direto na interface web
perde a alteração. Regra: edite em `docs/`, gere, publique."""),
    ("2", "DOCS", "Montar os slides da apresentação final",
     """**Objetivo.** Deck em `docs/apresentacao/`. Roteiro completo em
`docs/13-papeis-e-responsabilidades.md` §Roteiro dos slides.

**Os slides que mais pesam na avaliação**

| Slide | Cuidado |
|---|---|
| Escopo dentro/fora | Mostrar o corte como **decisão**, com o ADR-008 na tela. Escopo controlado é competência, não limitação |
| Arquitetura | Deixar claro que são **duas aplicações**. O MVC avaliado é o do backend; o frontend tem arquitetura própria |
| Clean Code | Uma prática por slide, com ruim/bom lado a lado, nas duas stacks |
| Design Patterns | Strategy e Repository, com diagrama e a justificativa de por que **não** foi um `if` |
| CI | Print do verde **e** print de um PR bloqueado |
| Melhorias futuras | Responde antecipadamente ao "e por que não fizeram X?" |

**Prazo:** rascunho em 08/08, versão final em 09/08. Ensaiar antes de 10/08."""),
    ("2", "DOCS", "Fechar a release v1.0.0",
     """**Objetivo.** Tag `v1.0.0` em `main`, com tudo verde.

**Checklist antes de taguear**

- [ ] `develop` com CI verde
- [ ] `release/1.0.0` criada a partir de `develop`
- [ ] Todos os CTs executados e o relatório final preenchido
- [ ] Documentação sincronizada com o código; Wiki publicada
- [ ] Nenhum item aberto na coluna `In Dev` ou `Code Review`
- [ ] PR `release/1.0.0` → `main` aprovado e mergeado
- [ ] Tag `v1.0.0` criada e release publicada no GitHub

**Notas da release** devem trazer: funcionalidades entregues por perfil, regras de negócio
implementadas (RN01–RN15), métricas de teste por stack, e o link para
`docs/15-melhorias-futuras.md` como escopo da próxima versão.

**Prazo: 10/08.**"""),
]


# ==========================================================================
# Montagem
# ==========================================================================
def corpo_user_story(us):
    historia_citada = "\n".join("> " + linha for linha in us["historia"].split("\n"))
    partes = [
        historia_citada,
        "",
        f"**Sprint {us['sprint']} · Prioridade {us['prioridade']} · Perfil: {us['perfil']}**",
        "",
        "---",
        "",
        "## Critérios de aceite",
        "",
        "Esta lista é o que o **PO valida na coluna UAT**. A User Story só sai de UAT quando "
        "todos estiverem marcados.",
        "",
    ]
    for i, c in enumerate(us["ca"], 1):
        partes.append(f"- [ ] {c}")
        partes.append("")
    partes += [
        "---",
        "",
        "## Regras de negócio envolvidas",
        "",
        bloco_rns(us["rns"]),
        "",
    ]
    if us.get("escopo_fora"):
        partes += ["---", "", "## Fora do escopo desta US", "", f"> {us['escopo_fora']}", ""]
    partes += [
        "---",
        "",
        "## Tarefas desta User Story",
        "",
        "Esta issue é **guarda-chuva**. O trabalho acontece nas tarefas abaixo:",
        "",
    ]
    for area, titulo, _b, _c in us["tarefas"]:
        partes.append(f"- [ ] `[{us['id']}] [{area}] {titulo}`")
    partes += [
        "",
        "---",
        "",
        "## Definition of Done da User Story",
        "",
        "- [ ] Todas as tarefas acima concluídas e mergeadas em `develop`",
        "- [ ] Fluxo funciona **ponta a ponta** pela interface, não só pelo Swagger",
        "- [ ] Todos os critérios de aceite acima marcados pelo PO",
        "- [ ] Casos de teste relacionados executados com evidência em `docs/evidencias/`",
        "- [ ] Nenhum bug de severidade Blocker ou Critical em aberto nesta US",
        "",
        "> **Regra de corte (ADR-008 §2).** Se o prazo apertar, esta User Story sai **inteira**. "
        "Não se entrega backend sem tela: sem fluxo navegável o QA não produz evidência, e "
        "evidência é entregável avaliado.",
        rodape("§2 backend · §3 frontend"),
    ]
    return "\n".join(partes)


def corpo_tarefa(us, area, titulo, branch, detalhe):
    secao = "§2 backend" if area == "BACKEND" else "§3 frontend"
    partes = [
        f"> **User Story:** `{us['id']} — {us['titulo']}` · **Sprint {us['sprint']}** · "
        f"**{us['prioridade']}** · **Responsável sugerido:** {RESP[area]}",
        "",
        "---",
        "",
        "## Contexto",
        "",
        "\n".join("> " + linha for linha in us["historia"].split("\n")),
        "",
        "---",
        "",
        "## O que fazer",
        "",
        detalhe,
        "",
        "---",
        "",
        "## Regras de negócio a respeitar",
        "",
        bloco_rns(us["rns"]),
        "",
        "---",
        "",
        "## Critérios de aceite da User Story",
        "",
        "Esta tarefa contribui para os critérios abaixo. O PO valida todos eles em conjunto na "
        "coluna UAT.",
        "",
    ]
    for c in us["ca"]:
        partes.append(f"- {c}")
    partes += [
        "",
        "---",
        "",
        "## Definition of Done",
        "",
        DOD[area].format(branch=branch),
        "",
        "---",
        "",
        "## Branch e commit",
        "",
        "```bash",
        f"git checkout develop && git pull",
        f"git checkout -b feature/{branch}",
        "```",
        "",
        "Commit no padrão Conventional Commits, em português, citando a RN quando aplicável:",
        "",
        "```",
        f"feat({us['id'].lower().replace('-', '')}): descricao curta em minusculas",
        "```",
        rodape(secao),
    ]
    return "\n".join(partes)


def corpo_processo(area, detalhe, sprint):
    return "\n".join([
        f"> **Área:** {area} · **Sprint {sprint}** · **Responsável sugerido:** {RESP[area]}",
        "",
        "---",
        "",
        detalhe,
        "",
        "---",
        "",
        "## Definition of Done",
        "",
        DOD[area].format(branch="processo"),
        rodape("geral"),
    ])


def montar():
    user_stories = []
    tarefas = []
    for us in US:
        user_stories.append({
            "sprint": us["sprint"],
            "tipo": "US",
            "titulo": f"{us['id']}: {us['titulo']}",
            "corpo": corpo_user_story(us),
        })
        for area, titulo, branch, detalhe in us["tarefas"]:
            tarefas.append({
                "sprint": us["sprint"],
                "tipo": area,
                "titulo": f"[{us['id']}] [{area}] {titulo}",
                "corpo": corpo_tarefa(us, area, titulo, branch, detalhe),
            })

    processo = [{
        "sprint": sprint,
        "tipo": area,
        "titulo": f"[{area}] {titulo}",
        "corpo": corpo_processo(area, detalhe, sprint),
    } for sprint, area, titulo, detalhe in PROCESSO]

    return {
        "_leia": [
            "FONTE UNICA dos itens do board (GitHub Projects nº 3).",
            "",
            "NAO EDITE ESTE ARQUIVO A MAO. Ele e gerado por scripts/gerar-board-itens.py,",
            "que injeta o texto das regras de negocio e a Definition of Done em cada item.",
            "Editar aqui e rodar o gerador de novo faz voce perder a edicao.",
            "",
            "Para mudar um item: edite scripts/gerar-board-itens.py e rode",
            "    python scripts/gerar-board-itens.py",
            "",
            "Publicar no board:",
            "    .\\scripts\\popular-board.ps1 -Auditar          (o que existe vs. o planejado)",
            "    .\\scripts\\popular-board.ps1 -Tudo -DryRun     (confira antes de escrever)",
            "    .\\scripts\\popular-board.ps1 -Tudo             (limpa e recria)",
            "",
            "PRINCIPIO: toda issue e AUTOCONTIDA. Criterio de aceite, texto integral das",
            "regras de negocio e Definition of Done ficam DENTRO do corpo da issue.",
            "Links para docs/ sao referencia complementar, nunca pre-requisito.",
            "",
            "Escopo congelado pelo ADR-008: 14 User Stories (US-00 a US-13).",
            "US-14 e US-15 sairam do MVP e viraram MF01 e MF02 em docs/15-melhorias-futuras.md.",
        ],
        "colunas_do_board": ["To Do", "In Dev", "Code Review", "In QA", "UAT", "Done"],
        "preservar_status": ["UAT", "Done"],
        "user_stories": user_stories,
        "tarefas": tarefas,
        "processo": processo,
    }


if __name__ == "__main__":
    dados = montar()
    SAIDA.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Gerado: {SAIDA.relative_to(RAIZ)}")
    print(f"  user_stories : {len(dados['user_stories']):>3}")
    print(f"  tarefas      : {len(dados['tarefas']):>3}")
    print(f"  processo     : {len(dados['processo']):>3}")
    total = sum(len(dados[k]) for k in ("user_stories", "tarefas", "processo"))
    print(f"  TOTAL        : {total:>3}")
