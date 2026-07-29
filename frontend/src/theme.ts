'use client';

import { createTheme, type MantineColorsTuple } from '@mantine/core';

// Paleta da clinica. Gerada em https://mantine.dev/colors-generator/
const clinica: MantineColorsTuple = [
  '#e7f5f4', '#d7e8e7', '#b1d1cf', '#87b9b6', '#66a5a1',
  '#519996', '#44938f', '#34807d', '#28726f', '#12635f',
];

export const theme = createTheme({
  primaryColor: 'clinica',
  colors: { clinica },
  defaultRadius: 'md',
  fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
  headings: { fontWeight: '600' },
  cursorType: 'pointer',
});
