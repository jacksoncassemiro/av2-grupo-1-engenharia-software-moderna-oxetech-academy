# Evidências de teste

Uma pasta por caso de teste (`CT01`, `CT02`, …) ou sessão exploratória (`EXP-01`, …).

```
CT02/
├── README.md                        # obrigatório
├── 01-cadastro-inicial.png
├── 02-tentativa-cpf-duplicado.png
└── 03-mensagem-de-erro.png
```

## Modelo do README.md da pasta

```markdown
# CT02 — Bloquear cadastro com CPF duplicado

- **US:** US-03 · **RN:** RN01
- **Ambiente:** Docker local, seed aplicado, commit `<sha>`
- **Executor:** <nome> · **Data:** DD/MM/AAAA
- **Resultado:** ✅ passou

## Passos e evidências

| # | Passo | Evidência |
|---|---|---|
| 1 | Cadastrar Carlos com CPF 529.982.247-25 | `01-cadastro-inicial.png` |
| 2 | Tentar cadastrar outro com o mesmo CPF | `02-tentativa-cpf-duplicado.png` |
| 3 | Sistema retorna 409 "CPF ja cadastrado" | `03-mensagem-de-erro.png` |

## Observações
<desvios, dados usados, configuração alterada>
```

## Regras

- O print precisa mostrar a **mensagem de erro exata** — é ela que prova que a RN foi aplicada.
- Arquivos numerados na ordem do passo.
- Sem dado pessoal real: use os CPFs fictícios de `../08-casos-de-teste.md` §1.
- Se alterou alguma configuração para viabilizar o teste (ex.:
  `CANCELAMENTO_ANTECEDENCIA_HORAS`), **registre em Observações**.
