# Estrutura de rotas (App Router)

Crie as rotas abaixo conforme as User Stories forem entrando na Sprint.
Route groups `(paciente)` e `(atendente)` isolam layout e guarda de rota por perfil (RF18).

```
src/app/
├── layout.tsx                    # MantineProvider + ColorSchemeScript (ja pronto)
├── page.tsx                      # landing (ja pronto)
├── login/page.tsx                # US-00
├── primeiro-acesso/page.tsx      # US-00 (ativar login / auto-cadastro)
├── (paciente)/
│   ├── layout.tsx                # guarda: tipo_usuario === 'PACIENTE'
│   ├── meus-dados/page.tsx       # US-04
│   ├── medicos/page.tsx          # US-06
│   ├── agendar/page.tsx          # US-07 + US-08
│   └── consultas/
│       ├── page.tsx              # US-10
│       └── [id]/page.tsx         # US-10 (detalhe) + US-11 (cancelar)
└── (atendente)/
    ├── layout.tsx                # guarda: tipo_usuario === 'ATENDENTE'
    ├── pacientes/page.tsx        # US-03
    ├── especialidades/page.tsx   # US-01
    ├── medicos/page.tsx          # US-02
    ├── agenda/page.tsx           # US-05 + US-14 (agenda geral)
    └── consultas/page.tsx        # US-09, US-12, US-13
```

Regras do projeto: ver `CLAUDE.md` na raiz e `.claude/skills/`.
