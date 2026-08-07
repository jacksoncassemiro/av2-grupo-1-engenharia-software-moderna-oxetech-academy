'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

import {
  Badge,
  Button,
  Card,
  Group,
  Modal,
  Stack,
  Table,
  Text,
  Textarea,
  Title,
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { Calendar, CalendarPlus } from 'lucide-react';

import { api, ApiError } from '@/lib/api';
import type { Consulta, StatusConsulta } from '@/types/dominio';

const COR_STATUS: Record<StatusConsulta, string> = {
  SOLICITADA: 'yellow',
  CONFIRMADA: 'teal',
  FINALIZADA: 'gray',
  CANCELADA: 'red',
};

const RECUSA_STATUS: Record<StatusConsulta, string> = {
  SOLICITADA: 'Solicitada',
  CONFIRMADA: 'Confirmada',
  FINALIZADA: 'Finalizada',
  CANCELADA: 'Cancelada',
};

export default function ConsultasPage() {
  const [consultas, setConsultas] = useState<Consulta[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [alvoCancelamento, setAlvoCancelamento] = useState<Consulta | null>(null);
  const [motivo, setMotivo] = useState('');
  const [cancelando, setCancelando] = useState(false);

  function carregar() {
    api<Consulta[]>('/consultas')
      .then(setConsultas)
      .catch((erro) => {
        notifications.show({
          message:
            erro instanceof ApiError ? erro.message : 'Não foi possível carregar suas consultas',
          color: 'red',
        });
      })
      .finally(() => setCarregando(false));
  }

  useEffect(() => {
    carregar();
  }, []);

  function abrirCancelamento(consulta: Consulta) {
    setAlvoCancelamento(consulta);
    setMotivo('');
  }

  async function confirmarCancelamento() {
    if (!alvoCancelamento) return;
    setCancelando(true);
    try {
      await api<Consulta>(`/consultas/${alvoCancelamento.id}/cancelar`, {
        method: 'PATCH',
        body: { motivo: motivo || null },
      });
      notifications.show({ message: 'Consulta cancelada', color: 'teal' });
      setAlvoCancelamento(null);
      setCarregando(true);
      carregar();
    } catch (erro) {
      notifications.show({
        title: 'Não foi possível cancelar',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    } finally {
      setCancelando(false);
    }
  }
  return (
    <Stack gap="lg">
      <Group justify="space-between" wrap="wrap">
        <Group gap="xs">
          <Calendar size={22} />
          <Title order={2} size="h3">
            Minhas Consultas
          </Title>
        </Group>
        <Button component={Link} href="/agendar" leftSection={<CalendarPlus size={16} />}>
          Nova consulta
        </Button>
      </Group>

      {!carregando && consultas.length === 0 && (
        <Card withBorder radius="md" p="xl">
          <Stack align="center" gap="sm">
            <Text c="dimmed">Você ainda não tem consultas agendadas.</Text>
            <Button
              component={Link}
              href="/agendar"
              variant="light"
              leftSection={<CalendarPlus size={16} />}
            >
              Agendar minha primeira consulta
            </Button>
          </Stack>
        </Card>
      )}

      {consultas.length > 0 && (
        <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
          <Table.ScrollContainer minWidth={640}>
            <Table verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Médico</Table.Th>
                  <Table.Th visibleFrom="sm">Especialidade</Table.Th>
                  <Table.Th>Data</Table.Th>
                  <Table.Th visibleFrom="sm">Horário</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th>Ações</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {consultas.map((consulta) => (
                  <Table.Tr key={consulta.id}>
                    <Table.Td>{consulta.medico_nome}</Table.Td>
                    <Table.Td visibleFrom="sm">{consulta.especialidade_nome}</Table.Td>
                    <Table.Td>{consulta.data.split('-').reverse().join('/')}</Table.Td>
                    <Table.Td visibleFrom="sm">{consulta.horario.slice(0, 5)}</Table.Td>
                    <Table.Td>
                      <Badge color={COR_STATUS[consulta.status]} variant="light">
                        {RECUSA_STATUS[consulta.status]}
                      </Badge>
                      {consulta.status === 'CANCELADA' && consulta.motivo_cancelamento && (
                        <Text size="xs" c="dimmed" mt={2}>
                          {consulta.motivo_cancelamento}
                        </Text>
                      )}
                    </Table.Td>
                    <Table.Td>
                      {consulta.pode_cancelar ? (
                        <Button
                          size="xs"
                          variant="light"
                          color="red"
                          onClick={() => abrirCancelamento(consulta)}
                        >
                          Cancelar
                        </Button>
                      ) : (
                        <Text size="xs" c="dimmed">
                          —
                        </Text>
                      )}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        </Card>
      )}

      <Modal
        opened={alvoCancelamento !== null}
        onClose={() => setAlvoCancelamento(null)}
        title="Cancelar consulta"
      >
        <Stack gap="md">
          <Text size="sm">
            Tem certeza que deseja cancelar a consulta com{' '}
            <Text component="span" fw={600}>
              {alvoCancelamento?.medico_nome}
            </Text>{' '}
            em {alvoCancelamento?.data.split('-').reverse().join('/')} às{' '}
            {alvoCancelamento?.horario.slice(0, 5)}?
          </Text>
          <Textarea
            label="Motivo"
            description="Opcional"
            placeholder="Ex.: imprevisto de última hora"
            value={motivo}
            onChange={(evento) => setMotivo(evento.currentTarget.value)}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setAlvoCancelamento(null)}>
              Voltar
            </Button>
            <Button color="red" loading={cancelando} onClick={confirmarCancelamento}>
              Confirmar cancelamento
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
