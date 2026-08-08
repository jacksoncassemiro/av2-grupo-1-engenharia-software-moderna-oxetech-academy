# CT12 — Requisição sem token e com token inválido (RN12, RN13)

- **US:** US-00 · **RN:** RN12, RN13
- **Ambiente:** Docker local, seed aplicado
- **Executor:** Uanderson · **Data:** 08/08/2026
- **Resultado:** ✅ passou 

## Passos e evidências

Passo | Evidência |
|---|---|---|
| 1 | Teste de API: `GET /api/consultas` sem header `Authorization` | `01-api-sem-token.png` — HTTP **401**, Header `WWW-Authenticate: Bearer`, Corpo: `{"detail":"Not authenticated"}` |
| 2 | Teste de API: Mesma chamada com `Authorization: Bearer token-invalido` | `02-api-token-invalido.png` — HTTP **401**, Header `WWW-Authenticate: Bearer`, Corpo: `{"detail":"Nao autenticado"}` |
| 3 | Corromper o token no `sessionStorage` (via console, chave `clinica.token`) e recarregar a página `/gerenciar-consultas` | `03-token-corrompido-logout.mp4` — Mostra o redirecionamento automático para `/login`, confirmando que o fix do bug abaixo está funcionando |
| 4 | Teste de API: `POST /api/auth/login` com senha errada, e depois com login inexistente | `04a-senha-incorreta.png` `04b-login-invalido.png` — Retorna HTTP **401** `"Login ou senha invalidos"` (`erro: CredenciaisInvalidas`) nos dois casos, com mensagem idêntica (não revela se o login existe) |

## Bug encontrado e corrigido

Passo 3 revelou que a aplicação não tratava sessão inválida: com um token corrompido, `/consultas`
renderizava **"Você ainda não tem consultas agendadas"** — indistinguível de um usuário sem
histórico, quando na verdade a API estava rejeitando com 401 a cada chamada (confirmado via
Network). Corrigido centralizando o tratamento em `src/lib/api.ts`: 401 numa requisição que
enviou token agora força `encerrarSessao()` + redirecionamento para `/login`. Ver commit/PR
`fix/us00-401-forca-logout`. Reexecutado o passo 3 após o fix: agora redireciona corretamente.

## Observações

- Inconsistência de idioma nas mensagens 401: passo 1 (sem header) usa a mensagem padrão em
  inglês do FastAPI (`"Not authenticated"`), enquanto o passo 2 (token inválido, tratado por
  código próprio) usa português (`"Nao autenticado"`). Cosmético, não bloqueante — registrado
  aqui para eventual padronização futura.