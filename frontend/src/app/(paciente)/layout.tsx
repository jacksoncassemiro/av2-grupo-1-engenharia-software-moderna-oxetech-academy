// Setup do Mantine para App Router conforme a doc oficial:
// https://mantine.dev/guides/next/#setup-with-app-router
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/notifications/styles.css';

import { ColorSchemeScript, MantineProvider, mantineHtmlProps } from '@mantine/core';
import { ModalsProvider } from '@mantine/modals';
import { Notifications } from '@mantine/notifications';
import type { Metadata } from 'next';

import { theme } from '@/theme';

export const metadata: Metadata = {
  title: 'Clinica Medica - MVP',
  description: 'Sistema de Gestao de Clinica Medica - AV2 Oxetech Academy, Equipe 01',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" {...mantineHtmlProps}>
      <head>
        <ColorSchemeScript defaultColorScheme="auto" />
      </head>
      <body>
        <MantineProvider theme={theme}>
          <ModalsProvider>
            <Notifications position="top-right" />
            {children}
          </ModalsProvider>
        </MantineProvider>
      </body>
    </html>
  );
}
