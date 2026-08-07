# CT01 — Cadastrar paciente com dados válidos

- **US:** US-03 · **RN:** RN07, RN08
- **Ambiente:** Docker local (`docker compose down -v && up -d --build`), seed aplicado, commit `5ce3f75`
- **Executor:** Claude (QA assistido) · **Data:** 01/08/2026
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Login como atendente, acessar *Pacientes* | `01-formulario-vazio.png` |
| 2 | Preencher nome `Carlos Souza`, CPF `529.982.247-25`, telefone `82999990000`, e-mail `carlos@email.com` | `02-formulario-preenchido.png` |
| 3 | Salvar | `03-paciente-criado.png` — notificação "Paciente cadastrado", aparece em "Cadastrados nesta sessão" |
| 4 | Tentar cadastrar com CPF `111.111.111-11` | `04-cpf-invalido-bloqueado.png` — bloqueado no cliente com "CPF inválido" antes de qualquer requisição (RN07) |

## Observações

- Screenshots capturados via Claude in Chrome durante execução ao vivo; salvos manualmente pelo executor a partir das imagens retornadas na sessão (limitação de ferramenta: não há caminho de disco acessível para salvamento automático).
- Passo 4 confirmado como bloqueio 100% client-side — nenhuma requisição HTTP foi disparada (verificado via DevTools Network).
