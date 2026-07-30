# ADR-005 — Auto-cadastro e cadastro por atendente no mesmo fluxo

**Status:** Aceito · **Data:** 2026-07-29 · **Decisores:** Equipe 01

## Contexto

Conflito direto entre as fontes do enunciado:

- **Case 1:** *"o sistema deverá permitir que **pacientes realizem seu cadastro** e solicitem
  consultas"*
- **Lista de funcionalidades:** *"Cadastrar novos pacientes"* aparece **somente** no perfil
  Atendente. O perfil Paciente tem apenas *"Atualizar seus dados cadastrais"*.

Implementar só o Case contraria a lista explícita. Implementar só a lista deixa o paciente sem
forma de obter login — e a jornada do paciente descrita no Case fica inacessível.

Complicação adicional: se o atendente criasse a senha do paciente no balcão, o atendente
saberia a senha de todos os pacientes. Ruim em privacidade e difícil de defender.

## Decisão

**Os dois caminhos, convergindo em um único endpoint:**
`POST /api/auth/vincular-ou-criar`.

```
Tela "Primeiro acesso" → paciente informa CPF
        │
        │  GET /api/auth/verificar-cpf/{cpf}
        │
        ├─ cadastro_existe = true, login_ativo = false
        │     "Encontramos seu cadastro, João! Crie uma senha para ativar seu login."
        │     → cria só a credencial e vincula ao paciente existente     [atende a lista]
        │
        ├─ cadastro_existe = false
        │     formulário completo (nome, telefone, e-mail opcional) + senha
        │     → cria cadastro E credencial no mesmo passo                [atende o Case]
        │
        └─ login_ativo = true
              → redireciona para o login normal
```

Consequência de modelagem: `POST /api/pacientes` (atendente, US-03) **não** cria credencial.
Ele registra apenas os dados cadastrais. O paciente define a própria senha depois.

O crédito da solução é do PO — está no backlog do Wiki como US-00. Nós apenas identificamos
que ela resolve o conflito e registramos por quê.

## Consequências

**Positivas**

- As duas fontes do enunciado ficam satisfeitas; nenhuma funcionalidade listada é descartada.
- O atendente nunca conhece a senha do paciente. Melhor privacidade.
- Atendimento de balcão continua rápido: cadastro sem exigir e-mail nem senha na hora.
- Um endpoint em vez de dois — menos superfície de teste, RN01/RN02/RN07 reaproveitadas.
- Paciente que nunca foi à clínica consegue se cadastrar e já agendar, como o Case pede.

**Negativas**

- O endpoint tem dois caminhos internos, o que exige teste dos dois
  (`test_primeiro_acesso_ativa_login_de_paciente_cadastrado_pelo_atendente` e
  `test_auto_cadastro_cria_paciente_e_credencial_no_mesmo_fluxo`).
- `nome` e `telefone` são condicionalmente obrigatórios (só no auto-cadastro). Validado no
  service, não no schema — o Pydantic não expressa bem essa condição.
- `GET /verificar-cpf` é público e revela se um CPF existe na clínica. Vazamento pequeno de
  informação, aceito porque a tela precisa da resposta antes de pedir senha. Anotado como
  risco; mitigação futura seria rate limiting.

## Alternativas

| Alternativa | Por que não |
|---|---|
| Só atendente cadastra | Contraria o Case; paciente nunca obtém login |
| Só auto-cadastro | Contraria a lista de funcionalidades; inviabiliza atendimento de balcão |
| Dois endpoints separados (`/pacientes/auto-cadastro` + `/auth/ativar`) | Duplica RN01/RN02/RN07 e a tela do paciente teria que decidir qual chamar |
| Atendente define a senha do paciente | Atendente passa a conhecer a senha de todos — problema de privacidade |
| Convite por e-mail para ativar conta | Paciente pode não ter e-mail (ver ADR-003) |


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
