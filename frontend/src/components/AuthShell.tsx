import { Center, Container, Paper } from '@mantine/core';

/** Cartao centralizado usado por /login e /primeiro-acesso. Responsivo: Container limita a
 * largura em telas grandes e ocupa 100% em mobile, com padding lateral proprio. */
export function AuthShell({ children }: { children: React.ReactNode }) {
  return (
    <Center mih="100vh" px="md" py="xl">
      <Container size={440} w="100%" p={0}>
        <Paper withBorder shadow="md" p={{ base: 'lg', sm: 'xl' }} radius="md">
          {children}
        </Paper>
      </Container>
    </Center>
  );
}
