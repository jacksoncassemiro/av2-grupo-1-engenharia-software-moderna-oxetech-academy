/**
 * Guarda de regressão: compound component do Mantine em Server Component.
 *
 * Propriedades estáticas (`List.Item`, `Popover.Target`, `Table.Thead`, ...) não
 * atravessam a fronteira dos React Server Components. Num arquivo sem
 * `'use client'`, `List.Item` chega como `undefined` e o `next build` quebra em
 * tempo de prerender com:
 *
 *   Error occurred prerendering page "/"
 *   Element type is invalid: expected a string (for built-in components) or a
 *   class/function (for composite components) but got: undefined.
 *
 * O erro NÃO aparece no `tsc` (o tipo existe), NÃO aparece no ESLint e NÃO aparece
 * nos testes com Testing Library (jsdom não tem fronteira RSC). Só no build.
 * Este teste antecipa a falha para o `yarn test`, que roda antes.
 *
 * Correção: adicionar `'use client'` no topo do arquivo, OU usar o import nomeado
 * (`ListItem`, `PopoverTarget`, `TableThead`).
 *
 * Fonte: https://mantine.dev/guides/next/#compound-components-in-server-components
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

import { describe, expect, it } from 'vitest';

const RAIZ_APP = join(process.cwd(), 'src', 'app');

/** Componentes do Mantine com compound components. Amplie conforme usar mais. */
const COM_COMPOUND = [
  'Accordion',
  'AppShell',
  'Avatar',
  'Burger',
  'Card',
  'Combobox',
  'Fieldset',
  'Grid',
  'HoverCard',
  'Image',
  'List',
  'Menu',
  'Modal',
  'NavLink',
  'Popover',
  'Spoiler',
  'Stepper',
  'Table',
  'Tabs',
  'Timeline',
  'Tooltip',
] as const;

const PADRAO_COMPOUND = new RegExp(`<(${COM_COMPOUND.join('|')})\\.[A-Z]\\w*`, 'g');

function listarArquivos(diretorio: string): string[] {
  const encontrados: string[] = [];
  for (const entrada of readdirSync(diretorio)) {
    const caminho = join(diretorio, entrada);
    if (statSync(caminho).isDirectory()) {
      encontrados.push(...listarArquivos(caminho));
    } else if (/\.tsx$/.test(entrada)) {
      encontrados.push(caminho);
    }
  }
  return encontrados;
}

function ehClientComponent(conteudo: string): boolean {
  // 'use client' tem de ser a primeira instrução do arquivo (comentários são ok).
  const semComentarios = conteudo.replace(/^(\s*(\/\/.*|\/\*[\s\S]*?\*\/)\s*)*/, '');
  return /^['"]use client['"]/.test(semComentarios.trimStart());
}

describe('Server Components e compound components do Mantine', () => {
  it('nenhum arquivo sem "use client" usa compound component', () => {
    const violacoes: string[] = [];

    for (const arquivo of listarArquivos(RAIZ_APP)) {
      const conteudo = readFileSync(arquivo, 'utf-8');
      if (ehClientComponent(conteudo)) continue;

      const usos = [...conteudo.matchAll(PADRAO_COMPOUND)].map((m) => m[0].slice(1));
      if (usos.length > 0) {
        violacoes.push(
          `${relative(process.cwd(), arquivo)}: ${[...new Set(usos)].join(', ')}`
        );
      }
    }

    expect(
      violacoes,
      'Compound component em Server Component quebra o `next build` com ' +
        '"Element type is invalid ... got: undefined".\n' +
        'Adicione \'use client\' no topo do arquivo OU troque para o import nomeado ' +
        '(List.Item -> ListItem, Popover.Target -> PopoverTarget):\n  ' +
        violacoes.join('\n  ')
    ).toEqual([]);
  });

  it('encontra os arquivos de rota (sanidade do próprio teste)', () => {
    expect(listarArquivos(RAIZ_APP).length).toBeGreaterThan(0);
  });
});
