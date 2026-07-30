# ADR-003 — Login flexível (CPF ou e-mail) com JWT

**Status:** Aceito · **Data:** 2026-07-29 · **Decisores:** Equipe 01

## Contexto

O Wiki do PO definiu um requisito de domínio importante: **paciente pode não ter e-mail**.
Numa clínica que atende por telefone e balcão, exigir e-mail excluiria parte dos pacientes.
Mas o atendente tem e-mail profissional e é por ele que se identifica.

Havia também uma frase no Wiki afirmando que **médicos** também logariam por e-mail — mas o
enum `tipo_usuario` só tem `PACIENTE` e `ATENDENTE`, e nenhuma User Story começa com
"Como Médico...".

## Decisão

**Uma tela de login com um único campo "CPF ou E-mail".**

Modelagem: `usuario.login` é `VARCHAR UNIQUE` que guarda CPF (só dígitos) para pacientes ou
e-mail em minúsculas para atendentes. `AuthService._normalizar()` decide pela presença de `@`:
com `@` → lowercase; sem `@` → apenas dígitos. Assim `529.982.247-25`, `52998224725` e
`Recepcao@Clinica.COM` todos funcionam.

Autenticação por **JWT HS256** com `sub` (login), `tipo_usuario`, `paciente_id` e `exp`.
`exigir_atendente` / `exigir_paciente` como dependência de rota (RN12). Expiração de 24h no
MVP, configurável (RN13). Senha com **bcrypt** via `passlib` (RN11).

**Contas separadas por papel:** se um atendente também for paciente da clínica, ele terá duas
contas — uma com login = e-mail (ATENDENTE), outra com login = CPF (PACIENTE). Decisão do PO,
mantida: evita auto-atendimento e simplifica a autorização.

**Perfil MEDICO fica fora do MVP.** Médico é entidade de cadastro, sem credencial. A frase do
Wiki foi corrigida.

## Consequências

**Positivas**

- Paciente sem e-mail usa o sistema — requisito real do domínio atendido.
- Um campo em vez de dois: menos atrito e menos erro de usuário.
- JWT stateless: nenhuma sessão no servidor, o que simplifica o Docker.
- `paciente_id` dentro do token permite escopar dados sem consultar o banco a cada request.

**Negativas**

- `login` polimórfico exige normalização disciplinada. Sem isso, `529.982.247-25` e
  `52998224725` seriam contas diferentes. Coberto por teste unitário
  (`test_paciente_loga_com_cpf_formatado`).
- Sem revogação de token antes da expiração. Aceitável para MVP; o campo `usuario.ativo`
  permite bloquear no próximo login.
- Recuperação de senha por e-mail não é possível para quem não tem e-mail — fica fora do MVP.
- Duas contas para a mesma pessoa física pode confundir. Documentado na visão do produto.

## Alternativas

| Alternativa | Por que não |
|---|---|
| Dois campos (e-mail *ou* CPF) na tela | Mais atrito; o usuário precisa saber qual é o seu |
| Login só por e-mail | Excluiria paciente sem e-mail — quebra o domínio |
| Login só por CPF | Atendente não tem CPF cadastrado como identidade funcional |
| Sessão com cookie no servidor | Estado no servidor complica o Docker; JWT é o padrão da stack |
| OAuth / provedor externo | Dependência externa, sem valor de avaliação, e exigiria e-mail |
| Perfil ADMIN + MEDICO agora | Escopo — ver ADR-004 |
