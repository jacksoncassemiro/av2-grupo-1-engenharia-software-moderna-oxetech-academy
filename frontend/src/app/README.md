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
    ├── agenda/page.tsx           # US-05
    └── consultas/page.tsx        # US-09, US-12, US-13
```

A tela de login vive em `src/app/login/page.tsx` (formulário + chamada à API na própria rota,
com o visual compartilhado em `src/components/AuthShell.tsx`). A guarda de perfil fica em
`src/components/auth/AuthGuard.tsx`, e a home de cada perfil em `src/lib/rotas.ts` — a mesma
constante que o `proxy.ts` lê, para login e guarda nunca discordarem.

---

## ⚠️ Next 16: `params` e `searchParams` são **Promise**

Isto é breaking change da v16 (na v15 havia compatibilidade síncrona temporária, que foi
removida). Vale para `params` em `page.tsx`/`layout.tsx`/`route.ts` e `searchParams` em
`page.tsx`, além de `cookies()`, `headers()` e `draftMode()`.

A rota `consultas/[id]/page.tsx` é onde isso aparece primeiro:

```tsx
// ❌ Errado no Next 16 — quebra em runtime e no tsc
export default function Page({ params }: { params: { id: string } }) {
  return <Consulta id={params.id} />;
}

// ✅ Certo — await no params
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <Consulta id={id} />;
}
```

### Melhor ainda: use os helpers de tipo gerados

`next typegen` (que o `yarn typecheck` já roda) gera `PageProps`, `LayoutProps` e
`RouteContext` globais e tipados **pela rota real**. Se você errar o nome do parâmetro, o
`tsc` reclama:

```tsx
export default async function Page(props: PageProps<'/consultas/[id]'>) {
  const { id } = await props.params;
  const query = await props.searchParams;
  return <Consulta id={id} />;
}
```

```tsx
export default async function Layout(props: LayoutProps<'/(paciente)'>) {
  return <PainelPaciente>{props.children}</PainelPaciente>;
}
```

## Guarda de rota: layout do route group, não `middleware`

No Next 16 o arquivo `middleware.ts` foi renomeado para `proxy.ts` (e o runtime `edge` não é
suportado nele). **Não precisamos disso.** A guarda por perfil (RF05) fica no `layout.tsx` de
cada route group, que é Client Component e lê o `tipo_usuario` do token:

```tsx
// src/app/(atendente)/layout.tsx
'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

import { lerToken } from '@/lib/api';

export default function LayoutAtendente({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  useEffect(() => {
    if (!lerToken()) router.replace('/login');
  }, [router]);

  return <>{children}</>;
}
```

A autorização de verdade é do backend (RN12) — o guard do frontend é só experiência de uso.

---

Regras do projeto: ver `CLAUDE.md` na raiz e `.claude/skills/`.
