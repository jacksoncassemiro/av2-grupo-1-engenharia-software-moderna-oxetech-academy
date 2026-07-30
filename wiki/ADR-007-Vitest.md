# ADR-007 — Vitest no Next.js em vez de Jest

**Status:** Aceito · **Data:** 2026-07-29 · **Decisores:** Equipe 01

## Contexto

O enunciado especifica **Vitest** como ferramenta de testes. Mas a documentação oficial do
Mantine é explícita na página *Testing with Vitest*: *"este guia é destinado a projetos que usam
Vite como bundler. Se você usa outros frameworks/bundlers, recomendamos usar Jest"* — e o
Next.js usa Turbopack/webpack, não Vite.

Ou seja: a stack pedida (Next.js + Mantine) tem recomendação oficial de Jest, e o enunciado
pede Vitest.

## Decisão

**Vitest**, combinando duas fontes oficiais:

1. **Setup do Next.js** (`nextjs.org/docs/app/guides/testing/vitest`):
   `vitest` + `@vitejs/plugin-react` + `vite-tsconfig-paths` + `jsdom`, com
   `vitest.config.mts`.
2. **Mocks do Mantine** (`mantine.dev/guides/vitest`): arquivo de setup com `window.matchMedia`,
   `ResizeObserver`, `document.fonts` e `scrollIntoView` — APIs que o jsdom não tem e vários
   componentes Mantine exigem. *(O guia do Mantine chama esse arquivo de `vitest.setup.mjs`;
   aqui ele é `.ts`, pelo motivo explicado logo abaixo.)*
3. **Custom render** em `test-utils/render.tsx`, envolvendo com
   `<MantineProvider theme={theme} env="test">`. Todo teste importa de `@test-utils`, nunca de
   `@testing-library/react` direto.

O arquivo de setup é **`vitest.setup.ts`**, não `.mjs` como no guia do Mantine. Isso é
deliberado: o `import '@testing-library/jest-dom/vitest'` faz duas coisas — registra os matchers
em runtime **e** aumenta a interface `Assertion` do Vitest com os tipos deles. O aumento de tipo
só vale se o arquivo estiver no `include` do `tsconfig.json`, o que exige extensão `.ts`.

Com `.mjs`, o `yarn test` passava mas o `tsc --noEmit` quebrava no CI com
`Property 'toBeInTheDocument' does not exist on type 'Assertion<HTMLElement>'` — exatamente o
tipo de erro que só aparece quando lint, teste e typecheck rodam separados no pipeline.

O Next.js suporta Vitest oficialmente — a recomendação de Jest do Mantine é sobre conveniência
de bundler, não sobre incompatibilidade.

## Consequências

**Positivas**

- Cumpre o enunciado sem gambiarra, usando dois setups oficiais.
- Vitest é mais rápido que Jest e a API é praticamente idêntica (`describe`/`it`/`expect`),
  então quem já viu Jest não tem curva.
- Cobertura via `@vitest/coverage-v8`, publicada como artifact no CI.
- `vite-tsconfig-paths` faz os aliases `@/*` e `@test-utils` do `tsconfig.json` funcionarem no
  teste sem duplicar configuração.

**Negativas — limitação real, documentada**

- **`async` Server Components não são testáveis no Vitest.** A própria doc do Next.js avisa:
  *"Since async Server Components are new to the React ecosystem, Vitest currently does not
  support them."*

  Mitigação adotada, e é uma decisão de design consciente: a lógica testável fica em
  **Client Components** e em **funções puras** de `src/lib/` (ex.: `cpf.ts`, `api.ts`).
  Página que só compõe layout não precisa de teste unitário — é validada pelos casos de teste
  funcionais do QA.

- Se um componente Mantine novo exigir outra API do browser, o erro aparece como
  `TypeError: x is not a function` dentro do teste. A correção é adicionar o mock em
  `vitest.setup.ts` — anotado no `CLAUDE.md`.

- Duas fontes de configuração para manter (Next + Mantine). Ambas versionadas e comentadas com
  o link da fonte.

## Alternativas

| Alternativa | Por que não |
|---|---|
| Jest (recomendação do Mantine) | O enunciado pede Vitest explicitamente |
| Vitest sem os mocks do Mantine | Quebra em qualquer componente que use `matchMedia` ou `ResizeObserver` |
| Playwright / Cypress no lugar de unitário | E2E não substitui teste unitário; e o enunciado pede Vitest |
| Trocar Next por Vite + React Router | Contraria a stack exigida (Next.js App Router) |
| Não testar o frontend | RNF06 e o entregável de QA exigem teste automatizado |

## Referências

- https://nextjs.org/docs/app/guides/testing/vitest
- https://mantine.dev/guides/vitest/


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
