---
name: clinica-frontend
description: Cria telas do MVP da clinica com Next.js App Router, TypeScript e Mantine v9. Use quando a tarefa envolver pagina, formulario, tabela, modal, notificacao, guarda de rota por perfil, chamada a API ou teste Vitest no frontend deste projeto.
---

# Frontend da clínica — como implementar

Stack: Next.js App Router + React + TypeScript **strict** + **Mantine v9** + **yarn**.
Provider e `ColorSchemeScript` já configurados em `src/app/layout.tsx` — não duplicar.

## Regras não negociáveis

1. **`'use client'`** no topo de qualquer página/componente com estado, evento, hook ou
   componente interativo do Mantine.
2. **Nunca use compound component em Server Component.** `List.Item`, `Popover.Target`,
   `Table.Thead`, `Tabs.Tab`, `Menu.Item`, `Card.Section`, `AppShell.Navbar`... Propriedades
   estáticas não atravessam a fronteira RSC — chegam como `undefined` e o **`next build` quebra
   no prerender**:

   ```
   Error occurred prerendering page "/"
   Element type is invalid: expected a string ... but got: undefined
   ```

   Esse erro **não aparece** no `tsc` (o tipo existe), nem no ESLint, nem no Vitest (jsdom não
   tem fronteira RSC). Só no build. As duas correções:

   ```tsx
   // A) marcar como Client Component
   'use client';
   import { List } from '@mantine/core';
   <List><List.Item>…</List.Item></List>

   // B) manter Server Component e usar o import nomeado  ← preferível quando não há interação
   import { List, ListItem } from '@mantine/core';
   <List><ListItem>…</ListItem></List>
   ```

   `frontend/__tests__/server-components.test.ts` varre `src/app/` e falha se algum arquivo sem
   `'use client'` usar compound component. Se você adicionar um componente novo com compounds,
   inclua o nome dele na lista `COM_COMPOUND` desse teste.
3. **Nenhuma outra biblioteca de UI.** Sem Tailwind, MUI, shadcn, styled-components.
   Estilo: props do Mantine (`mt`, `p`, `c`, `gap`) ou CSS Module com `postcss-preset-mantine`.
4. **HTTP só via `src/lib/api.ts`.** Nunca `fetch` em componente. O `api()` já injeta o
   Bearer token e converte erro da API em `ApiError` com mensagem legível.
5. **Tipos vêm de `src/types/dominio.ts`**, espelhando o backend. Sem `any`.
6. **Testes importam de `@test-utils`**, nunca de `@testing-library/react` direto —
   o `render` customizado é o que injeta o `MantineProvider`.

## Estrutura de rotas

Route groups por perfil, com guarda no `layout.tsx` do grupo (RF18):

```
src/app/login/page.tsx              US-00
src/app/primeiro-acesso/page.tsx    US-00 (ativar login / auto-cadastro)
src/app/(paciente)/…                US-04, US-06, US-07, US-08, US-10, US-11
src/app/(atendente)/…               US-01, US-02, US-03, US-05, US-09, US-12, US-13
```

Mapa completo em `frontend/src/app/README.md`.

## Formulário — padrão do projeto

`@mantine/form` com `validate`; erro da API vira notificação, não `alert`:

```tsx
'use client';

import { Button, TextInput } from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';

import { api, ApiError } from '@/lib/api';
import { cpfEhValido, formatarCpf } from '@/lib/cpf';

export function FormularioPaciente() {
  const form = useForm({
    initialValues: { nome: '', cpf: '', telefone: '', email: '' },
    validate: {
      nome: (v) => (v.trim().length < 3 ? 'Informe o nome completo' : null),
      cpf: (v) => (cpfEhValido(v) ? null : 'CPF invalido'),          // RN07
      email: (v) => (!v || /^\S+@\S+$/.test(v) ? null : 'E-mail invalido'), // RN08
    },
  });

  async function enviar(valores: typeof form.values) {
    try {
      await api('/pacientes', { method: 'POST', body: valores });
      notifications.show({ message: 'Paciente cadastrado', color: 'green' });
      form.reset();
    } catch (erro) {
      // RN01/RN02 chegam aqui como 409 com mensagem pronta do backend.
      notifications.show({
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    }
  }

  return (
    <form onSubmit={form.onSubmit(enviar)}>
      <TextInput label="Nome" withAsterisk {...form.getInputProps('nome')} />
      <TextInput
        label="CPF"
        withAsterisk
        {...form.getInputProps('cpf')}
        onChange={(e) => form.setFieldValue('cpf', formatarCpf(e.currentTarget.value))}
      />
      <Button type="submit" mt="md" loading={form.submitting}>Salvar</Button>
    </form>
  );
}
```

## Componentes por caso de uso

| Precisa de | Use |
|---|---|
| Formulário | `@mantine/form` + `TextInput`, `Select`, `PasswordInput` |
| Data / hora | `@mantine/dates`: `DatePickerInput`, `TimeInput` (+ `dayjs`) |
| Confirmação | `modals.openConfirmModal` (`@mantine/modals`) |
| Feedback | `notifications.show` (`@mantine/notifications`) |
| Status da consulta | `Badge` com cor por status |
| Listagem | `Table` + `Table.Thead/Tbody/Tr/Td` |
| Layout autenticado | `AppShell` com `AppShell.Navbar` |
| Carregando | `Skeleton` ou `LoadingOverlay` |

Cores sugeridas por status (RN06): SOLICITADA `yellow`, CONFIRMADA `teal`,
FINALIZADA `gray`, CANCELADA `red`.

## Campo único de login (US-00)

A tela de login tem **um** campo "CPF ou E-mail". Use `pareceEmail()` de `src/lib/cpf.ts`
para decidir se aplica máscara de CPF enquanto o usuário digita. O backend normaliza
os dois formatos — não envie o CPF com máscara.

## Teste com Vitest

```tsx
import { describe, expect, it } from 'vitest';
import { render, screen, userEvent } from '@test-utils';

import { FormularioPaciente } from '@/components/FormularioPaciente';

describe('FormularioPaciente', () => {
  it('bloqueia envio com CPF invalido (RN07)', async () => {
    render(<FormularioPaciente />);
    await userEvent.type(screen.getByLabelText(/CPF/i), '11111111111');
    await userEvent.click(screen.getByRole('button', { name: /salvar/i }));
    expect(await screen.findByText('CPF invalido')).toBeInTheDocument();
  });
});
```

`async` Server Components não são testáveis no Vitest (ADR-007) — mantenha a lógica
testável em Client Components ou em funções puras de `src/lib/`.

## Next 16 — o que muda na prática

| Mudança | O que fazer |
|---|---|
| **`params` e `searchParams` são `Promise`** | `const { id } = await props.params`. Compatibilidade síncrona foi **removida** na v16. |
| **Helpers de tipo por rota** | Prefira `PageProps<'/consultas/[id]'>`, `LayoutProps<'/(paciente)'>`, `RouteContext<'/api/x'>` — gerados por `next typegen`, tipados pela rota real |
| `cookies()`, `headers()`, `draftMode()` | Também assíncronos |
| **`next lint` removido** | `eslint .` (ver abaixo) |
| **`middleware.ts` → `proxy.ts`** | Não usamos. Guarda de rota fica no `layout.tsx` do route group |
| **Turbopack é o padrão** | Não passe `--turbopack` em `dev`/`build` |
| `serverRuntimeConfig`/`publicRuntimeConfig` removidos | Use `NEXT_PUBLIC_*` |
| Parallel routes exigem `default.tsx` | Não usamos parallel routes |
| `next/image`: `qualities` agora é `[75]`, IP local bloqueado | Se usar imagem externa, configure `images.remotePatterns` |

```tsx
// ❌ Errado no Next 16
export default function Page({ params }: { params: { id: string } }) {
  return <Consulta id={params.id} />;
}

// ✅ Certo
export default async function Page(props: PageProps<'/consultas/[id]'>) {
  const { id } = await props.params;
  return <Consulta id={id} />;
}
```

Página assíncrona é Server Component — então o componente interativo dentro dela precisa ser um
Client Component separado (é também o que torna o teste com Vitest possível, ver ADR-007).

## Lint e typecheck no Next 16

`next lint` foi **removido** na v16, junto com a opção `eslint` do `next.config`.

| Script | O que roda | Por quê |
|---|---|---|
| `yarn format` | `prettier --write .` | Formata; `format:check` é a versão que o CI usa |
| `yarn lint` | `eslint .` | CLI do ESLint, com `eslint.config.mjs` em flat config |
| `yarn typecheck` | `next typegen && tsc --noEmit` | `next typegen` gera `next-env.d.ts` e os tipos de rota; sem ele o `tsc` falha |

Prettier e ESLint não brigam: o `eslint-config-next` não tem regra de estilo que conflite, por
isso não usamos `eslint-config-prettier`. O `.prettierrc` reproduz o estilo que o código já
tinha — aspas simples, 100 colunas (mesmo `line-length` do ruff no backend), `trailingComma: es5`.

`eslint.config.mjs` importa `eslint-config-next/core-web-vitals` e `eslint-config-next/typescript`
direto (sem `FlatCompat`). Se precisar desligar uma regra, adicione um objeto `{ rules: {...} }`
depois dos spreads — nunca remova os `globalIgnores`.

## Checklist antes de abrir PR

- [ ] `yarn lint && yarn typecheck && yarn test`
- [ ] `'use client'` onde há interatividade
- [ ] Zero `any`, zero `fetch` direto, zero `console.log`
- [ ] Erro da API tratado com notificação
- [ ] Rota protegida pelo guard do route group
