# CT11 — Paciente não acessa rota de atendente (RN12)

- **US:** US-00 · **RN:** RN12
- **Ambiente:** Docker local, seed aplicado
- **Executor:** Uanderson · **Data:** 08/08/2026
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Logado como paciente, acessar `http://localhost:3000/consultas` diretamente pela URL | `01-redirect-login.mp4` (Vídeo) — Mostra o usuário sendo redirecionado imediatamente para `/login` pelo guard do route group `(atendente)` |
| 2 | (Teste API) Com token de paciente, forçar `POST /api/pacientes` | `02-api-403-restrito.png` — HTTP **403**: `"Acesso restrito ao perfil ATENDENTE"` |
| 3 | (Teste API) Com token de paciente, forçar `GET /api/consultas?paciente_id=2` | `03-api-200-isolamento.mp4` — Retorna **200**, mas apenas com as consultas do próprio usuário (`paciente_id: 1`). O parâmetro injetado foi devidamente ignorado e o filtro real foi derivado exclusivamente do JWT de forma segura. |

## Observações

- Nenhum bug encontrado. Comportamento exatamente como especificado — `paciente_id` nunca é
  aceito do cliente, sempre derivado do JWT.