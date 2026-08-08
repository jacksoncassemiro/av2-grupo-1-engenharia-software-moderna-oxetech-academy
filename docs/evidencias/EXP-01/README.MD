### Sessão EXP-01 — Cadastro de paciente e Primeiro acesso

- **Charter:** Explorar os fluxos de cadastro de paciente (atendente) e ativação de primeiro acesso (paciente), validando robustez dos campos de texto (nome, senha) contra entradas inválidas, espaços em branco e caracteres repetidos.
- **Duração:** 45 min · **Data:** 07/08/2026 · **Executor:** João Vitor
- **Ambiente:** Docker local, seed aplicado, commit <sha>

- **Achados:**

  | # | Descrição | Severidade | Issue |
  |---|---|---|---|
  | 1 | No **Primeiro acesso**, o campo "Criar senha" aceita senha composta **apenas de espaços em branco** (passa na validação de mínimo de 6 caracteres). Também aceita senha formada por um único caractere repetido (`çççççççççç...`), sem nenhuma verificação de complexidade mínima. | Alta | #46 |
  | 2 | No cadastro de **Paciente** (Nome completo) e reproduzido também em **Meus Dados**, o campo aceita espaço em branco no final do nome (`"JOAO "`), números (`"JOAO 123"`) e strings sem sentido/caracteres especiais (`"12345498604824-2-392-=9521=2- vitor"`), sem nenhuma validação de que o valor deve conter apenas letras (e eventuais acentos/apóstrofos/hífen de nomes compostos). | Média | #46 |

- **Não testado / ficou de fora:** tentativa de XSS/injeção nos mesmos campos; duplo clique e reload no meio do preenchimento (ficou para próxima sessão).
- **Evidências:** `docs/evidencias/EXP-01/`
  - `EXP-01-01-senha-so-espacos.png`
  - `EXP-01-02-senha-caractere-repetido.png`
  - `EXP-01-03-nome-com-espaco-e-numero.png`
  - `EXP-01-04-nome-string-invalida-primeiro-acesso.png`


