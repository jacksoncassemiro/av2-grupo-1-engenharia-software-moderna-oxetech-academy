// Server Component fino. Toda a interatividade vive no Client Component, que e o
// que torna a tela testavel no Vitest (ADR-007).
import { Container } from '@mantine/core';
import type { Metadata } from 'next';

import { PrimeiroAcesso } from '@/components/primeiro-acesso/PrimeiroAcesso';

export const metadata: Metadata = {
  title: 'Primeiro acesso - Clinica Medica',
  description: 'Ative seu login ou cadastre-se pelo CPF (US-00)',
};

export default function PrimeiroAcessoPage() {
  return (
    <Container size="xs" py="xl">
      <PrimeiroAcesso />
    </Container>
  );
}
