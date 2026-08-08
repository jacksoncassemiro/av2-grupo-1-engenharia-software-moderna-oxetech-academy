# CT14 — Não existe caminho público para virar atendente

- **US:** US-00 · **RN:** RN14, RN12
- **Ambiente:** Docker local, seed aplicado, commit `e2053c2`
- **Executor:** Felipe · **Data:** 07/08/2026
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Abrir `http://localhost:8000/docs` e procurar rota pública que crie usuário `ATENDENTE` | `01-rotas-publicas.png` — únicos endpoints sem cadeado em "Autenticacao": `POST /auth/login`, `GET /auth/verificar-cpf/{cpf}`, `POST /auth/vincular-ou-criar`. Nenhuma rota pública de cadastro de atendente existe |
| 2 | Sem token, `POST /api/auth/vincular-ou-criar` forçando `"tipo_usuario": "ATENDENTE"` no corpo (paciente Maria Silva, CPF `123.456.789-09`) | `02-forcar-atendente.png` — **201**, resposta com `"tipo_usuario": "PACIENTE"`. O campo enviado no corpo é ignorado; o schema `PrimeiroAcesso` não expõe `tipo_usuario` |
| 2b | Confirmação: `GET /api/pacientes/me` com o token recém-criado | `03-paciente-me.png` — **200**, retorna o cadastro de Maria Silva como paciente comum (`id: 3`), provando que a conta nasceu `PACIENTE` de fato, não só na resposta do login |
| 3 | Logada como paciente (Maria), chamar `GET /api/atendente/consultas?status=SOLICITADA` | `04-rota-protegida-tipo-incorreto.png` — **403**, `{"detail": "Acesso restrito ao perfil ATENDENTE"}` |
| 4 | Sem token, chamar a mesma rota `/api/atendente/consultas` | `05-rota-protegida-deslogado.png` — **401**, `{"detail": "Not authenticated"}`, header `www-authenticate: Bearer` |
| 5 | Rodar `docker compose exec backend python -m app.seeds.seed` uma segunda vez | `06-seed-idempotente.png` — saída `Atendente ja existe - nada a fazer. Seed concluido.` Nenhum atendente duplicado (ADR-004) |

## Observações

- Nenhum bug encontrado neste CT.
