'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

import { Badge, Button, Card, Group, Select, SimpleGrid, Stack, Text, Title } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { CalendarPlus, Stethoscope } from 'lucide-react';

import { api, ApiError } from '@/lib/api';
import type { Especialidade, Medico } from '@/types/dominio';

export default function MedicosPage() {
  const [medicos, setMedicos] = useState<Medico[]>([]);
  const [especialidades, setEspecialidades] = useState<Especialidade[]>([]);
  const [filtroEspecialidade, setFiltroEspecialidade] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(true);

  const opcoesEspecialidade = useMemo(
    () => especialidades.map((e) => ({ value: String(e.id), label: e.nome })),
    [especialidades]
  );

  const nomeDaEspecialidade = useMemo(() => {
    const mapa = new Map(especialidades.map((e) => [e.id, e.nome]));
    return (id: number) => mapa.get(id) ?? '';
  }, [especialidades]);

  // Carrega as especialidades uma única vez na montagem
  useEffect(() => {
    let ignorar = false;
    api<Especialidade[]>('/especialidades?apenas_ativas=true')
      .then((dados) => {
        if (!ignorar) setEspecialidades(dados);
      })
      .catch((erro) => {
        // Sem as especialidades o filtro fica vazio e cada medico aparece sem
        // o badge da especialidade: falhar em silencio esconde isso do paciente.
        if (ignorar) return;
        notifications.show({
          message:
            erro instanceof ApiError ? erro.message : 'Não foi possível carregar as especialidades',
          color: 'red',
        });
      });
    return () => {
      ignorar = true;
    };
  }, []);

  // Busca médicos sempre que o filtro por especialidade for alterado
  useEffect(() => {
    let ignorar = false;

    async function carregarMedicos() {
      try {
        const queryParams = new URLSearchParams();
        queryParams.append('apenas_ativos', 'true');
        if (filtroEspecialidade) queryParams.append('especialidade_id', filtroEspecialidade);
        const listaMedicos = await api<Medico[]>(`/medicos?${queryParams.toString()}`);
        if (!ignorar) setMedicos(listaMedicos);
      } catch (erro) {
        if (!ignorar) {
          notifications.show({
            message:
              erro instanceof ApiError ? erro.message : 'Não foi possível carregar os médicos',
            color: 'red',
          });
        }
      } finally {
        if (!ignorar) setCarregando(false);
      }
    }

    carregarMedicos();

    return () => {
      ignorar = true;
    };
  }, [filtroEspecialidade]);

  function aoFiltrar(valor: string | null) {
    setCarregando(true);
    setFiltroEspecialidade(valor);
  }

  return (
    <Stack gap="lg">
      <Group gap="xs">
        <Stethoscope size={22} />
        <Title order={2} size="h3">
          Médicos
        </Title>
      </Group>

      <Select
        label="Filtrar por especialidade"
        placeholder="Todas as especialidades"
        data={opcoesEspecialidade}
        value={filtroEspecialidade}
        onChange={aoFiltrar}
        clearable
        maw={{ base: '100%', xs: 320 }}
      />

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="md">
        {medicos.map((medico) => (
          <Card key={medico.id} withBorder radius="md" p="lg">
            <Stack gap={4}>
              <Text fw={600}>{medico.nome}</Text>
              <Badge variant="light" w="fit-content">
                {nomeDaEspecialidade(medico.especialidade_id)}
              </Badge>
              <Text size="sm" c="dimmed">
                CRM {medico.crm}
              </Text>
              <Button
                component={Link}
                href={`/agendar?medico=${medico.id}`}
                variant="light"
                mt="sm"
                leftSection={<CalendarPlus size={16} />}
              >
                Agendar
              </Button>
            </Stack>
          </Card>
        ))}
      </SimpleGrid>

      {!carregando && medicos.length === 0 && (
        <Text c="dimmed" ta="center" py="xl">
          Nenhum médico disponível nesta especialidade.
        </Text>
      )}
    </Stack>
  );
}
