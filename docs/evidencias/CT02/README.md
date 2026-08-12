# CT02 — Bloquear cadastro com CPF duplicado (RN01)

- **US:** US-03 · **RN:** RN01
- **Ambiente:** Docker local, seed aplicado, commit `37fbecb`
- **Executor:** Uanderson  · **Data:** 07/08/2026
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Preencher `Carlos Duplicado`, CPF `529.982.247-25` (já usado por CT01), telefone `82988887777`, e-mail `outro@email.com` | `01-tentativa-cpf-duplicado.png` |
| 2 | Salvar | `02-mensagem-cpf-ja-cadastrado.png` — notificação "Não foi possível cadastrar / CPF ja cadastrado" |

## Resposta exata do servidor

```
POST /api/pacientes → 409
"CPF ja cadastrado"
```

## Observações

- Listagem "Cadastrados nesta sessão" continuou mostrando apenas um Carlos Souza após a tentativa — nenhum registro duplicado foi criado.
