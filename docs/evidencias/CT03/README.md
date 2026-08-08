# CT03 — Bloquear e-mail duplicado e permitir e-mail nulo (RN02)

- **US:** US-03 · **RN:** RN02, RN08
- **Ambiente:** Docker local (`docker compose down -v && up -d --build`), seed aplicado, commit `e2053c2`
- **Executor:** Uanderson · **Data:** 07/08/2026
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Cadastrar Maria Teste, CPF `111.444.777-35`, e-mail `carlos@email.com` (já em uso) | `01-email-duplicado-bloqueado.png` — HTTP 409 "E-mail em uso" |
| 2 | Repetir com e-mail `carlos@` | `02-email-formato-invalido.png` — bloqueado no cliente com "E-mail inválido" (RN08) |
| 3 | Repetir deixando o campo e-mail vazio | `03a-formulario-sem-email.png` (antes de salvar) <br> `03b-sucesso-email-vazio.png` (paciente criado com sucesso) |
| 4 | Cadastrar João Sem Email, CPF `123.456.789-09`, também sem e-mail | `04a-formulario-joao.png` (antes de salvar) <br> `04b-dois-emails-nulos.png` (criado com sucesso; dois pacientes com e-mail nulo coexistem) |

## Observações

- O Passo 4 confirma que campos `NULL` não contam como duplicidade na restrição `UNIQUE` do banco de dados (é exatamente o caso que pega a implementação ingênua da RN02, conforme nota do plano de testes).