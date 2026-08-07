'use client';

import { Suspense } from 'react';

import { Group, Skeleton, Stack, Title } from '@mantine/core';
import { CalendarPlus } from 'lucide-react';

import { FormularioAgendamento } from './FormularioAgendamento';

/**
 * Rota /agendar — US-07 (grade de horarios livres) + US-08 (confirmar a solicitacao).
 *
 * O <Suspense> nao e decorativo: `FormularioAgendamento` le `?medico=` com
 * `useSearchParams`, e sem a fronteira o `next build` reprova a pre-renderizacao.
 */
export default function AgendarPage() {
  return (
    <Stack gap="lg">
      <Group gap="xs">
        <CalendarPlus size={22} />
        <Title order={2} size="h3">
          Agendar Consulta
        </Title>
      </Group>

      <Suspense fallback={<Skeleton height={240} radius="md" />}>
        <FormularioAgendamento />
      </Suspense>
    </Stack>
  );
}
