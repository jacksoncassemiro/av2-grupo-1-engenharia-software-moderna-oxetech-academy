'use client';

import { useEffect, useState } from 'react';

import {
  ActionIcon,
  Badge,
  Button,
  Card,
  Group,
  Select,
  Stack,
  Table,
  Text,
  Textarea,
  TextInput,
  Title,
  Tooltip,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { Ban, CheckCircle2, Tag } from 'lucide-react';

import { api, ApiError } from '@/lib/api';
import { validarNomeCompleto } from '@/lib/validadores';
import type { Especialidade } from '@/types/dominio';

export default function EspecialidadesPage() {
  const [especialidades, setEspecialidades] = useState<Especialidade[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [alterandoId, setAlterandoId] = useState<string | number | null>(null);
  const [statusFiltro, setStatusFiltro] = useState<string>('true');

  const form = useForm({
    initialValues: { nome: '', descricao: '' },
    validate: {
      nome: (valor: string) => validarNomeCompleto(valor, 'Informe ao menos 3 caracteres'),
    },
  });

  useEffect(() => {
    let cancel = false;

    async function buscar() {
      try {
        const queryParam = statusFiltro !== 'todos' ? `?apenas_ativas=${statusFiltro}` : '';
        const dados = await api<Especialidade[]>(`/especialidades${queryParam}`);
        if (!cancel) setEspecialidades(dados);
      } catch (erro) {
        if (!cancel) {
          notifications.show({
            message: erro instanceof ApiError ? erro.message : 'Não foi possível carregar as especialidades',
            color: 'red',
          });
        }
      } finally {
        if (!cancel) setCarregando(false);
      }
    }

    buscar();

    return () => {
      cancel = true;
    };
  }, [statusFiltro]);

  async function cadastrar(valores: typeof form.values) {
    setEnviando(true);
    try {
      const criada = await api<Especialidade>('/especialidades', {
        method: 'POST',
        body: { nome: valores.nome, descricao: valores.descricao || null },
      });

      if (statusFiltro !== 'false') {
        setEspecialidades((atual) => [...atual, criada]);
      }

      notifications.show({ message: 'Especialidade cadastrada', color: 'teal' });
      form.reset();
    } catch (erro) {
      notifications.show({
        title: 'Não foi possível cadastrar',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    } finally {
      setEnviando(false);
    }
  }

  async function alternarStatus(especialidade: Especialidade) {
    setAlterandoId(especialidade.id);

    try {
      const atualizada = await api<Especialidade>(`/especialidades/${especialidade.id}/status`, {
        method: 'PATCH',
      });

      setEspecialidades((atual) =>
        atual.map((item) => (item.id === atualizada.id ? atualizada : item))
      );

      notifications.show({
        message: `Especialidade ${atualizada.ativo ? 'ativada' : 'inativada'} com sucesso!`,
        color: 'teal',
      });
    } catch (erro) {
      notifications.show({
        title: 'Não foi possível alterar o status',
        message: erro instanceof ApiError ? erro.message : 'Falha na requisição',
        color: 'red',
      });
    } finally {
      setAlterandoId(null);
    }
  }

  const especialidadesFiltradas = especialidades.filter((esp) => {
    if (statusFiltro === 'true') return esp.ativo === true;
    if (statusFiltro === 'false') return esp.ativo === false;
    return true;
  });

  return (
    <Stack gap="lg">
      <Group gap="xs">
        <Tag size={22} />
        <Title order={2} size="h3">
          Especialidades
        </Title>
      </Group>

      <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
        <Text fw={600} mb="md">
          Cadastrar nova especialidade
        </Text>
        <form onSubmit={form.onSubmit(cadastrar)}>
          <Stack gap="md">
            <TextInput
              label="Nome"
              placeholder="Ex.: Cardiologia"
              withAsterisk
              {...form.getInputProps('nome')}
            />
            <Textarea
              label="Descrição"
              description="Opcional"
              placeholder="Breve descrição da especialidade"
              autosize
              minRows={2}
              {...form.getInputProps('descricao')}
            />
            <Group justify="flex-end">
              <Button type="submit" loading={enviando}>
                Cadastrar
              </Button>
            </Group>
          </Stack>
        </form>
      </Card>

      <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
        <Group justify="space-between" align="center" mb="md">
          <Text fw={600}>Especialidades cadastradas</Text>
          <Select
            aria-label="Filtrar por status"
            size="xs"
            w={160}
            value={statusFiltro}
            onChange={(val) => {
              setStatusFiltro(val || 'true');
              setCarregando(true);
            }}
            data={[
              { value: 'true', label: 'Ativas' },
              { value: 'false', label: 'Inativas' },
              { value: 'todos', label: 'Todas' },
            ]}
            allowDeselect={false}
          />
        </Group>

        <Table.ScrollContainer minWidth={480}>
          <Table verticalSpacing="sm">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Nome</Table.Th>
                <Table.Th visibleFrom="sm">Descrição</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th ta="right">Ações</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {especialidadesFiltradas.map((especialidade) => (
                <Table.Tr key={especialidade.id}>
                  <Table.Td>{especialidade.nome}</Table.Td>
                  <Table.Td visibleFrom="sm">
                    <Text c="dimmed" size="sm">
                      {especialidade.descricao || '—'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={especialidade.ativo ? 'teal' : 'gray'} variant="light">
                      {especialidade.ativo ? 'Ativa' : 'Inativa'}
                    </Badge>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Tooltip label={especialidade.ativo ? 'Inativar' : 'Ativar'}>
                      <ActionIcon
                        variant="light"
                        color={especialidade.ativo ? 'red' : 'green'}
                        onClick={() => alternarStatus(especialidade)}
                        loading={alterandoId === especialidade.id}
                        aria-label={especialidade.ativo ? 'Inativar' : 'Ativar'}
                      >
                        {especialidade.ativo ? <Ban size={16} /> : <CheckCircle2 size={16} />}
                      </ActionIcon>
                    </Tooltip>
                  </Table.Td>
                </Table.Tr>
              ))}
              {!carregando && especialidadesFiltradas.length === 0 && (
                <Table.Tr>
                  <Table.Td colSpan={4}>
                    <Text c="dimmed" ta="center" py="md">
                      Nenhuma especialidade encontrada.
                    </Text>
                  </Table.Td>
                </Table.Tr>
              )}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Card>
    </Stack>
  );
}