# Conflitos do enunciado e decisões da equipe

Documento de análise. Confrontamos três fontes que **não são idênticas** e registramos
como cada divergência foi resolvida. Cada decisão relevante virou um ADR em `docs/adr/`.

**Fontes analisadas:**

| Sigla | Fonte |
|---|---|
| **F1** | Texto do *Case 1 — Sistema de Gestão de Clínica Médica* |
| **F2** | Lista detalhada de funcionalidades por perfil + RN01–RN06 |
| **F3** | Backlog do Wiki (US-00 a US-12), escrito pelo PO — versão de 29/07 |

> **Nota sobre F3.** O Wiki foi republicado a partir de `docs/` em 30/07, então a versão citada
> aqui não está mais disponível para consulta. As divergências que envolviam **apenas** F3 e já
> estavam resolvidas foram encerradas; o que permanece neste documento são as divergências
> entre **F1 e F2**, que são o enunciado e continuam verificáveis.

---

## Resumo

| # | Conflito / lacuna | Gravidade | Resolução | ADR |
|---|---|---|---|---|
| C01 | Quem cadastra o paciente | **Alta** | Os dois caminhos, no mesmo endpoint | ADR-005 |
| C02 | Como nasce o primeiro atendente | **Alta** | Seed idempotente + RN14 | ADR-004 |
| C03 | `UNIQUE` no slot impede reagendar | **Alta** | Índice parcial | ADR-006 |
| C04 | Nada leva a consulta a CONFIRMADA/FINALIZADA | **Alta** | US-13 nova | — |
| C05 | E-mail do médico serve para login? | Média | Não — médico é cadastro, não usuário (MF09) | ADR-003 |
| C06 | `Usuario` do atendente não tem nome | Média | `nome` em `Usuario` | — |
| C07 | RN05 sem constraint no modelo | Média | `UniqueConstraint` | — |
| C08 | "Gerenciar agenda geral" sem US | Média | ~~US-14 nova~~ → fora do MVP (MF01) | [ADR-008](adr/ADR-008-rebaseline-escopo.md) |
| C09 | Status inicial divergente entre US-08 e US-09 | Média | Depende de quem agenda | — |
| C10 | 24h sem fuso definido | Média | RN15 — `America/Maceio` | — |
| C11 | Médico ↔ especialidade: 1:N ou N:N | Baixa | 1:N (segue F3) | — |
| C12 | Vitest × Next.js (Mantine recomenda Jest) | Baixa | Vitest, setup oficial Next | ADR-007 |
| C13 | Composição da equipe | Média | ✅ Resolvido: 6 pessoas, 1/3/2 + PO de apoio | [ADR-008](adr/ADR-008-rebaseline-escopo.md) |

---

## C01 — Quem cadastra o paciente?

**Divergência.** F1 diz: *"o sistema deverá permitir que **pacientes realizem seu cadastro**
e solicitem consultas"*. F2 põe *"Cadastrar novos pacientes"* exclusivamente no perfil
**Atendente** — o perfil Paciente só pode *"Atualizar seus dados cadastrais"*.

Se implementarmos só F2, o paciente nunca cria conta e o login dele não tem origem.
Se implementarmos só F1, contrariamos a lista explícita de funcionalidades.

**Resolução.** O Wiki (F3) já resolveu isso de forma elegante, e adotamos: os dois caminhos
convergem em `POST /api/auth/vincular-ou-criar`.

```
Paciente informa CPF na tela "Primeiro acesso"
        │
        ├─ CPF já existe em `paciente` (cadastrado no balcão pelo atendente)
        │     → cria só a credencial e vincula ao cadastro   [atende F2]
        │
        └─ CPF não existe
              → cria cadastro + credencial no mesmo passo    [atende F1]
```

Consequências: `POST /api/pacientes` (atendente) **não** cria credencial — o paciente
define a própria senha depois, o que é melhor em privacidade do que o atendente escolher
a senha do paciente. Um `GET /api/auth/verificar-cpf/{cpf}` alimenta a tela antes de pedir
a senha. → **ADR-005**

---

## C02 — Como nasce o primeiro atendente?

**Lacuna.** Nenhuma das três fontes diz de onde vem o primeiro atendente. Sem atendente
não há médico, especialidade nem horário — logo o sistema recém-instalado é inutilizável.

Alternativas descartadas:

- **Só seed, sem forma de criar outros** — frágil. Se a senha do seed vaza ou a pessoa sai,
  não há caminho de recuperação. Além disso não demonstra a funcionalidade.
- **Rota pública `/register` de atendente** — qualquer visitante da internet vira atendente
  e passa a ver o prontuário de todos. É falha de segurança, difícil de defender na avaliação.
- **Perfil ADMIN separado** — conceitualmente mais correto, mas adiciona um terceiro perfil,
  telas e testes a um MVP de 11 dias. Fica registrado como evolução futura em
  [`15-melhorias-futuras.md`](15-melhorias-futuras.md).

**Resolução.** Seed **idempotente** cria o primeiro atendente com credenciais vindas do `.env`.
Formalizado como **RN14: não existe rota pública de cadastro de atendente; só quem já tem o
perfil ATENDENTE pode criar outro.** → **ADR-004**

> **Ajuste de 30/07.** A *tela* de cadastro de atendente saiu do MVP no rebaseline de escopo —
> ela não consta na lista de funcionalidades do enunciado, e o atendente do seed basta para a
> demonstração e para os testes. Virou **MF02** em
> [`15-melhorias-futuras.md`](15-melhorias-futuras.md). **A RN14 permanece integralmente** e é
> testada pelo CT14, que prova que não existe caminho público para obter o perfil de atendente.

O CI roda o seed **duas vezes** para provar a idempotência.

---

## C03 — O `UNIQUE` no slot impediria reagendar (bug de modelagem)

**Problema técnico encontrado ao revisar F3.** O Wiki define
`consulta.horario_disponivel_id` como `Obrigatório, Único` para garantir a RN03.
Mas a US-11 diz que ao cancelar, o slot volta a `disponivel = true`.

Com `UNIQUE` simples, a linha da consulta **CANCELADA** continua ocupando o valor no índice.
Resultado: o slot aparece livre na tela, mas qualquer novo agendamento estoura violação de
constraint. O slot fica permanentemente inutilizável depois do primeiro cancelamento —
exatamente o cenário que a US-11 quer viabilizar.

**Resolução.** Índice **parcial**, que só considera consultas que de fato ocupam o slot:

```sql
CREATE UNIQUE INDEX uq_slot_ativo
  ON consulta (horario_disponivel_id)
  WHERE status IN ('SOLICITADA', 'CONFIRMADA');
```

Consultas CANCELADAS/FINALIZADAS saem do índice e o slot pode ser reaproveitado.
Complementarmente, a reserva usa `SELECT ... FOR UPDATE` (`buscar_para_reserva`) para
resolver a corrida de dois pacientes clicando ao mesmo tempo — cenário que a própria US-08
descreve. O índice fica como garantia de último recurso. → **ADR-006**

---

## C04 — Nada leva a consulta a CONFIRMADA nem a FINALIZADA

**Lacuna.** RN06 exige gestão dos quatro status. Mas nas US-00 a US-12:
`SOLICITADA` nasce na US-08, `CONFIRMADA` nasce na US-09, `CANCELADA` vem das US-11/US-12 —
e **nenhuma US** promove SOLICITADA → CONFIRMADA ou CONFIRMADA → FINALIZADA.

Isto é: uma consulta solicitada pelo paciente (US-08) ficaria eternamente SOLICITADA, e o
status FINALIZADA seria código morto. A RN06 não estaria demonstrável.

**Resolução.** Criada a **US-13 — Atendente confirma e finaliza consultas**
(`PATCH /api/atendente/consultas/{id}/status`), validada pela máquina de estados da RN10.
Sem ela, a RN06 fica sem cobertura de teste.

---

## C05 — Médico tem e-mail, mas não é perfil de acesso

**Ambiguidade.** F2 manda "cadastrar médicos" com e-mail, e a RN02 exige e-mail único **entre
usuários**. Isso levanta a dúvida: o e-mail do médico serve para ele fazer login?

**Resolução.** Não. O enunciado define **dois perfis**: Paciente e Atendente. No MVP, **Médico
é entidade de cadastro, não usuário do sistema** — tem `email` para unicidade (RN02) e contato,
mas não tem credencial nem login, e o enum `tipo_usuario` tem apenas `PACIENTE` e `ATENDENTE`.

Um terceiro perfil mudaria o modelo de autorização inteiro. Registrado como **MF09** em
[`15-melhorias-futuras.md`](15-melhorias-futuras.md), versão-alvo v2.0. → **ADR-003**

---

## C06 — O `Usuario` do atendente não tem nome

**Lacuna.** A tabela `Usuario` de F3 tem `id, login, senha, tipo_usuario, paciente_id`.
O nome do paciente vem por `paciente_id`. Mas o atendente tem `paciente_id = NULL` — então
não há como exibir "Olá, Maria" no painel do atendente nem auditar quem cancelou o quê.

**Resolução.** Adicionada a coluna `nome` em `usuario` (obrigatória), e `ativo` para soft
delete coerente com as demais tabelas.

---

## C07 — RN05 declarada, mas sem constraint no modelo

**Lacuna.** RN05 ("bloqueio de alocação dupla para o mesmo médico no mesmo horário") não
tem nenhuma restrição correspondente na tabela `HorarioDisponivel` de F3. A regra ficaria
só na aplicação — e uma inserção concorrente ou um script fora da API a violaria.

**Resolução.** `UniqueConstraint('medico_id', 'data', 'horario')` em `horario_disponivel`,
mais validação no `AgendaService` para devolver uma mensagem de negócio em vez de erro de
banco cru.

---

## C08 — "Cadastrar e gerenciar a agenda geral" não tem US

**Lacuna.** F2 lista essa funcionalidade para o Atendente. A US-05 cobre *cadastrar* a grade
de um médico, mas a **visão consolidada** da clínica (todos os médicos, filtro por data,
quem está livre) não tem US nem endpoint.

**Resolução original (29/07).** Criada a **US-14 — Agenda geral da clínica**, prioridade
*Desejável*.

**Resolução atual (30/07) — revertida.** A US-14 **saiu do MVP** no rebaseline de escopo. Ela
não consta na lista de funcionalidades dos dois perfis, e é uma visualização agregada de dados
que já são acessíveis pelas telas existentes: o atendente vê a agenda de cada médico na tela de
agenda (US-05) e todas as consultas na tela de consultas (US-09). A lacuna que ela preenchia é
de conveniência, não de capacidade.

Registrada como **MF01** em [`15-melhorias-futuras.md`](15-melhorias-futuras.md), com esforço
estimado e versão-alvo v1.1. Justificativa em
[ADR-008](adr/ADR-008-rebaseline-escopo.md).

---

## C09 — Status inicial: SOLICITADA ou CONFIRMADA?

**Divergência aparente.** US-08 (paciente) diz status inicial `SOLICITADA`; US-09 (atendente)
diz `CONFIRMADA`.

**Resolução.** Não é conflito, é regra: o status inicial **depende de quem agenda**.
Paciente pede (precisa de confirmação da clínica) → `SOLICITADA`. Atendente agenda pelo
balcão/telefone (já é a clínica falando) → `CONFIRMADA`. Explicitado em
`ConsultaService._status_inicial()` e coberto por teste unitário.

---

## C10 — "24h de antecedência" em qual fuso?

**Ambiguidade.** RN04 fala em 24h, mas nem F1, F2 ou F3 definem fuso. Um servidor em UTC
compararia `datetime.now()` (UTC) com um horário digitado em hora local — erro de 3h, que
faz uma consulta de 26h parecer de 23h e bloquear um cancelamento legítimo.

**Resolução.** **RN15: todas as regras temporais usam `America/Maceio`**, configurável via
`TIMEZONE` no `.env`. `datetime` do banco é `timezone=True`, e a Strategy recebe `agora`
por parâmetro — o que também torna o teste determinístico.

---

## C11 — Médico e especialidade: 1:N ou N:N?

**Divergência entre propostas.** Uma proposta anterior modelou tabela associativa
`medico_especialidade` (N:N). F3 usa `especialidade_id` como FK direta em `medico` (1:N).

**Resolução.** **1:N**, seguindo F3. É o suficiente para o MVP, mantém a US-06 (filtro por
especialidade) simples, e evita uma tabela e um join. Se a clínica precisar de médico com
duas especialidades, é migração aditiva depois.

---

## C12 — Vitest com Next.js

**Divergência de recomendação.** O enunciado exige **Vitest**. A documentação do Mantine
recomenda **Jest** para Next.js, reservando Vitest para projetos Vite.

**Resolução.** Vitest, usando o setup **oficial do Next.js**
(`@vitejs/plugin-react` + `vite-tsconfig-paths` + `jsdom`) combinado com o `vitest.setup.mjs`
de mocks do Mantine (`matchMedia`, `ResizeObserver`, `document.fonts`). Limitação aceita e
documentada: `async` Server Components não são testáveis no Vitest — por isso a lógica
testável fica em Client Components e em funções puras de `src/lib/`. → **ADR-007**

---

## C13 — Composição da equipe

**Divergência original.** O enunciado diz *"As funções, sendo **2 para cada**"* → 2 PO + 2 Eng
+ 2 QA. O repositório listava **7 nomes**, distribuídos como 1 PO + 4 Engenharia + 2 QA.

**Resolvido em 30/07.** Com a saída de Jonatha da Silva Fernandes, a equipe passou a **6
pessoas**: 1 PO + 3 Engenharia + 2 QA.

A leitura "2 para cada" é atendida pela coluna **Apoio** de
[`13-papeis-e-responsabilidades.md`](13-papeis-e-responsabilidades.md): **Antonio atua como PO
de apoio** nos itens de processo (cerimônias e slides), enquanto Jackson mantém a propriedade
do backlog. Assim há dois nomes em cada papel sem inflar o escopo de ninguém.

Os entregáveis que eram de Jonatha (arquitetura MVC, Clean Code e Design Patterns) foram para
**Ronaldo**, que passa a ser dono do backend e do domínio por inteiro. Clean Code e testes
unitários **do frontend** ficaram com João Vitor — são práticas de outra stack, e concentrá-las
numa pessoa só não faria sentido. Registrado no
[ADR-008](adr/ADR-008-rebaseline-escopo.md).

O que importa para a avaliação: **todo entregável tem um responsável nomeado**, e a tabela de
`13-papeis-e-responsabilidades.md` mostra isso item a item.

---

## Regras de negócio adicionadas nesta análise

Além das RN01–RN06 do enunciado:

| ID | Regra | Origem |
|---|---|---|
| RN07 | CPF válido por dígitos verificadores | Boa prática — RN01 sem isso aceita `00000000000` |
| RN08 | E-mail em formato válido | Complementa RN02 |
| RN09 | Agenda restrita a horário comercial (08:00–18:00) | Realismo do domínio (F1: substituir planilha) |
| RN10 | Transições de status unidirecionais | Torna RN06 verificável |
| RN11 | Senha com hash bcrypt | Segurança — F3 diz "senha criptografada" sem especificar |
| RN12 | Autorização por perfil no token | F2 (dois perfis com permissões próprias) |
| RN13 | Expiração do JWT | Segurança |
| RN14 | Sem rota pública de cadastro de atendente | C02 |
| RN15 | Regras temporais em `America/Maceio` | C10 |
