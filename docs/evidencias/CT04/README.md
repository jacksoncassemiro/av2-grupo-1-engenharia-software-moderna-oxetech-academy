# CT04 — Primeiro acesso: ativar login de paciente cadastrado no balcão

- **US:** US-00 · **RN:** RN11
- **Ambiente:** Docker local, seed aplicado, commit `5ce3f75`
- **Executor:** Claude (QA assistido) · **Data:** 01/08/2026
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Logout do atendente | — |
| 2 | Acessar *Primeiro acesso*, informar `529.982.247-25` | `01-cpf-encontrado.png` — "Encontramos seu cadastro, Carlos Souza! Crie uma senha para ativar seu login." |
| 3 | Definir senha `senha123` e confirmar | `POST /api/auth/vincular-ou-criar` → 201; login criado, redireciona para `/consultas` (painel do paciente) |
| 4 | Sair e logar com `52998224725` / `senha123` (CPF sem máscara) | `POST /api/auth/login` → 200, aceito sem máscara |
| 5 | Repetir *Primeiro acesso* com o mesmo CPF | `02-cpf-ja-tem-login.png` — "Este CPF já possui login ativo / Você já criou sua senha anteriormente." |

## Verificação RN11 (senha nunca em texto claro)

Corpo da resposta de `POST /api/auth/login` inspecionado via DevTools:
```json
{"access_token": "<jwt>", "token_type": "bearer", "tipo_usuario": "PACIENTE"}
```
Nenhum campo `senha` presente; string `senha123` não aparece em lugar nenhum da resposta.

## Observações

- Nenhum bug encontrado neste CT.
