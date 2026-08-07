// src\app\(atendente)\gerenciar-consultas\TabelaConsultas.tsx
'use client';

import { useEffect, useState } from 'react';

import { Badge, Button, Card, Group, Select, Table, Text } from '@mantine/core';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';

import { api, ApiError } from '@/lib/api';
import type { Consulta, StatusConsulta } from '@/types/dominio';

const COR_STATUS: Record<StatusConsulta, string> = {
  SOLICITADA: 'yellow',
  CONFIRMADA: 'teal',
  FINALIZADA: 'gray',
  CANCELADA: 'red',
};

const RETULO_STATUS: Record<StatusConsulta, string> = {
  SOLICITADA: 'Solicitada',
  CONFIRMADA: 'Confirmada',
  FINALIZADA: 'Finalizada',
  CANCELADA: 'Cancelada',
};

const OPCOES_STATUS = (Object.keys(RETULO_STATUS) as StatusConsulta[]).map((status) => ({
  value: status,
  label: RETULO_STATUS[status],
}));

interface TabelaConsultasProps {
  versao: number;
}

export function TabelaConsultas({ versao }: TabelaConsultasProps) {
  const [consultas, setConsultas] = useState<Consulta[]>([]);
  const [filtroStatus, setFiltroStatus] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [processando, setProcessando] = useState<number | null>(null);

  function carregar(status?: string | null) {
    setCarregando(true);
    const query = status ? `?status=${status}` : '';
    api<Consulta[]>(`/atendente/consultas${query}`)
      .then(setConsultas)
      .catch((erro) => {
        notifications.show({
          message: erro instanceof ApiError ? erro.message : 'Não foi possível carregar as consultas',
          color: 'red',
        });
      })
      .finally(() => setCarregando(false));
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    carregar(filtroStatus);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [versao]);

  function aoFiltrar(valor: string | null) {
    setFiltroStatus(valor);
    carregar(valor);
  }

  async function mudarStatus(consulta: Consulta, novoStatus: StatusConsulta) {
    setProcessando(consulta.id);
    try {
      await api<Consulta>(`/atendente/consultas/${consulta.id}/status`, {
        method: 'PATCH',
        body: { status: novoStatus },
      });
      notifications.show({ message: `Consulta ${RETULO_STATUS[novoStatus].toLowerCase()}`, color: 'teal' });
      carregar(filtroStatus);
    } catch (erro) {
      notifications.show({
        title: 'Não foi possível atualizar',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    } finally {
      setProcessando(null);
    }
  }

  function confirmarCancelamento(consulta: Consulta) {
    modals.openConfirmModal({
      title: 'Cancelar consulta',
      children: (
        <Text size="sm">
          Cancelar a consulta de {consulta.paciente_nome ?? 'Paciente'} com {consulta.medico_nome ?? 'Médico'}{' '}
          {consulta.data ? `em ${consulta.data.split('-').reverse().join('/')}` : ''}? O atendente pode cancelar mesmo com
          menos de 24h (US-12).
        </Text>
      ),
      labels: { confirm: 'Cancelar consulta', cancel: 'Voltar' },
      confirmProps: { color: 'red' },
      onConfirm: () => cancelar(consulta),
    });
  }

  async function cancelar(consulta: Consulta) {
    setProcessando(consulta.id);
    try {
      await api<Consulta>(`/atendente/consultas/${consulta.id}/cancelar`, {
        method: 'PATCH',
        body: { motivo: null },
      });
      notifications.show({ message: 'Consulta cancelada', color: 'teal' });
      carregar(filtroStatus);
    } catch (erro) {
      notifications.show({
        title: 'Não foi possível cancelar',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    } finally {
      setProcessando(null);
    }
  }

  return (
    <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
      <Group justify="space-between" mb="md" wrap="wrap">
        <Text fw={600}>Todas as consultas</Text>
        <Select
          placeholder="Filtrar por status"
          data={OPCOES_STATUS}
          value={filtroStatus}
          onChange={aoFiltrar}
          clearable
          w={{ base: '100%', xs: 220 }}
        />
      </Group>
      <Table.ScrollContainer minWidth={720}>
        <Table verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Paciente</Table.Th>
              <Table.Th>Médico</Table.Th>
              <Table.Th visibleFrom="sm">Data</Table.Th>
              <Table.Th visibleFrom="sm">Horário</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Ações</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {consultas.map((consulta) => (
              <Table.Tr key={consulta.id}>
                <Table.Td>{consulta.paciente_nome ?? '-'}</Table.Td>
                <Table.Td>{consulta.medico_nome ?? '-'}</Table.Td>
                <Table.Td visibleFrom="sm">
                  {consulta.data ? consulta.data.split('-').reverse().join('/') : '-'}
                </Table.Td>
                <Table.Td visibleFrom="sm">
                  {consulta.horario ? consulta.horario.slice(0, 5) : '-'}
                </Table.Td>
                <Table.Td>
                  <Badge color={COR_STATUS[consulta.status]} variant="light">
                    {RETULO_STATUS[consulta.status]}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs" wrap="nowrap">
                    {consulta.status === 'SOLICITADA' && (
                      <Button
                        size="xs"
                        variant="light"
                        color="teal"
                        loading={processando === consulta.id}
                        onClick={() => mudarStatus(consulta, 'CONFIRMADA')}
                      >
                        Confirmar
                      </Button>
                    )}
                    {consulta.status === 'CONFIRMADA' && (
                      <Button
                        size="xs"
                        variant="light"
                        color="gray"
                        loading={processando === consulta.id}
                        onClick={() => mudarStatus(consulta, 'FINALIZADA')}
                      >
                        Finalizar
                      </Button>
                    )}
                    {(consulta.status === 'SOLICITADA' || consulta.status === 'CONFIRMADA') && (
                      <Button
                        size="xs"
                        variant="subtle"
                        color="red"
                        loading={processando === consulta.id}
                        onClick={() => confirmarCancelamento(consulta)}
                      >
                        Cancelar
                      </Button>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {!carregando && consultas.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text c="dimmed" ta="center" py="md">
                    Nenhuma consulta encontrada.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>
    </Card>
  );
}
