import { Anchor, Container, List, Stack, Text, Title } from '@mantine/core';

export default function HomePage() {
  return (
    <Container size="sm" py="xl">
      <Stack gap="md">
        <Title order={1}>Clinica Medica - MVP</Title>
        <Text c="dimmed">
          Scaffold do frontend pronto: Next.js App Router + TypeScript + Mantine v9,
          com Vitest configurado. As telas serao construidas pelas User Stories do backlog.
        </Text>
        <List>
          <List.Item>
            <Anchor href="/login">/login</Anchor> - US-00: entrar com CPF ou e-mail
          </List.Item>
          <List.Item>
            <Anchor href="/primeiro-acesso">/primeiro-acesso</Anchor> - US-00: ativar
            login ou se auto-cadastrar
          </List.Item>
        </List>
        <Text size="sm" c="dimmed">
          Documentacao completa em <Anchor href="/docs">docs/</Anchor> e na Wiki do
          repositorio.
        </Text>
      </Stack>
    </Container>
  );
}
