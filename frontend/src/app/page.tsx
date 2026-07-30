// Server Component (sem 'use client').
//
// ATENCAO: em Server Component NAO se usa compound component do Mantine
// (`List.Item`, `Popover.Target`, ...). Propriedades estaticas nao atravessam a
// fronteira RSC, entao `List.Item` chega como `undefined` e o build quebra com
// "Element type is invalid: expected a string ... but got: undefined".
// A alternativa e o import nomeado: `ListItem`, `PopoverTarget`, etc.
// Fonte: https://mantine.dev/guides/next/#compound-components-in-server-components
import { Code, Container, List, ListItem, Stack, Text, Title } from '@mantine/core';

export default function HomePage() {
  return (
    <Container size="sm" py="xl">
      <Stack gap="md">
        <Title order={1}>Clínica Médica — MVP</Title>

        <Text c="dimmed">
          Scaffold do frontend pronto: Next.js App Router + TypeScript + Mantine v9, com Vitest
          configurado. As telas são construídas conforme as User Stories entram na sprint.
        </Text>

        <Title order={2} size="h4" mt="md">
          Próximas rotas (US-00)
        </Title>

        <List spacing="xs">
          <ListItem>
            <Code>/login</Code> — entrar com CPF ou e-mail
          </ListItem>
          <ListItem>
            <Code>/primeiro-acesso</Code> — ativar o login ou se auto-cadastrar
          </ListItem>
        </List>

        <Text size="sm" c="dimmed" mt="md">
          Mapa completo das rotas em <Code>frontend/src/app/README.md</Code>. Documentação do
          projeto em <Code>docs/</Code> e na Wiki do repositório.
        </Text>
      </Stack>
    </Container>
  );
}
