'use client';

import { Select, type SelectProps } from '@mantine/core';

/** Largura dos filtros de cabeçalho de tabela, no desktop. No mobile eles ocupam a linha. */
export const LARGURA_FILTRO_TABELA = 200;

/**
 * `Select` dos filtros que ficam no cabeçalho das telas de tabela.
 *
 * Existe para que largura e altura sejam iguais em todas elas. Cada tela vinha
 * escolhendo a sua — `size="xs" w={160}` em especialidades, `w={200}` no tamanho
 * padrão e `size="xs" w={130}` lado a lado em médicos, `w={220}` em
 * gerenciar-consultas — e na tela de médicos os dois filtros vizinhos saíam com
 * alturas diferentes, porque um usava `size="xs"` e o outro o padrão.
 *
 * `size` e `w` são aplicados **depois** do spread de propósito: a tela escolhe os
 * dados e o comportamento do filtro, não a proporção dele.
 */
export function FiltroTabela(props: SelectProps) {
  return <Select {...props} size="sm" w={{ base: '100%', xs: LARGURA_FILTRO_TABELA }} />;
}
