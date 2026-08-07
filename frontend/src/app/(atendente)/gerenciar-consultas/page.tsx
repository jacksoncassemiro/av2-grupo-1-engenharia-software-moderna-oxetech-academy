// src\app\(atendente)\gerenciar-consultas\page.tsx
'use client';

import { useState } from 'react';

import { Group, Stack, Title } from '@mantine/core';
import { ClipboardList } from 'lucide-react';

import { AgendarParaPaciente } from './AgendaParaPaciente';
import { TabelaConsultas } from './TabelaConsultas';

export default function ConsultasAtendentePage() {
  const [versaoLista, setVersaoLista] = useState(0);

  return (
    <Stack gap="lg">
      <Group gap="xs">
        <ClipboardList size={22} />
        <Title order={2} size="h3">
          Gestão de Consultas
        </Title>
      </Group>

      <AgendarParaPaciente onAgendado={() => setVersaoLista((v) => v + 1)} />
      <TabelaConsultas versao={versaoLista} />
    </Stack>
  );
}
