'use client';

import { useEffect, useMemo, useState } from 'react';

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
  TextInput,
  Title,
  Tooltip,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { Ban, CheckCircle2, Stethoscope } from 'lucide-react';

import { api, ApiError } from '@/lib/api';
import {
  validarEmailObrigatorio,
  validarNomeCompleto,
  validarTextoMinimo,
} from '@/lib/validadores';
import type { Especialidade, Medico } from '@/types/dominio';

export default function MedicosPage() {
  const [medicos, setMedicos] = useState<Medico[]>([]);
  const [especialidades, setEspecialidades] = useState<Especialidade[]>([]);
  const [filtroEspecialidade, setFiltroEspecialidade] = useState<string | null>(null);
  const [statusFiltro, setStatusFiltro] = useState<string>('true');
  const [carregando, setCarregando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [alterandoId, setAlterandoId] = useState<string | number | null>(null);

  const form = useForm({
    initialValues: { nome: '', email: '', crm: '', especialidadeId: '' },
    validate: {
      nome: (valor: string) => validarNomeCompleto(valor),
      email: validarEmailObrigatorio,
      crm: (valor: string) => validarTextoMinimo(valor, 4, 'CRM inválido'),
      especialidadeId: (valor) => (valor ? null : 'Selecione uma especialidade'),
    },
  });

  const opcoesEspecialidadeForm = useMemo(
    () =>
      especialidades
        .filter((e) => e.ativo !== false)
        .map((e) => ({ value: String(e.id), label: e.nome })),
    [especialidades]
  );

  const opcoesEspecialidadeFiltro = useMemo(
    () => especialidades.map((e) => ({ value: String(e.id), label: e.nome })),
    [especialidades]
  );

  const nomeDaEspecialidade = useMemo(() => {
    const mapa = new Map(especialidades.map((e) => [e.id, e.nome]));
    return (id: number) => mapa.get(id) ?? `#${id}`;
  }, [especialidades]);

  // Carrega as especialidades uma vez ao montar o componente
  useEffect(() => {
    let cancel = false;

    async function buscarEspecialidades() {
      try {
        const dados = await api<Especialidade[]>('/especialidades?apenas_ativas=true');
        if (!cancel) setEspecialidades(dados);
      } catch (erro) {
        if (!cancel) {
          notifications.show({
            message:
              erro instanceof ApiError
                ? erro.message
                : 'Não foi possível carregar as especialidades',
            color: 'red',
          });
        }
      }
    }

    buscarEspecialidades();

    return () => {
      cancel = true;
    };
  }, []);

  // Busca lista de médicos quando os filtros se alteram
  useEffect(() => {
    let cancel = false;

    async function buscarMedicos() {
      try {
        const queryParams = new URLSearchParams();
        if (filtroEspecialidade) queryParams.append('especialidade_id', filtroEspecialidade);
        if (statusFiltro !== 'todos') queryParams.append('apenas_ativos', statusFiltro);

        const query = queryParams.toString();
        const dados = await api<Medico[]>(`/medicos${query ? `?${query}` : ''}`);

        if (!cancel) setMedicos(dados);
      } catch (erro) {
        if (!cancel) {
          notifications.show({
            message:
              erro instanceof ApiError ? erro.message : 'Não foi possível carregar os médicos',
            color: 'red',
          });
        }
      } finally {
        if (!cancel) setCarregando(false);
      }
    }

    buscarMedicos();

    return () => {
      cancel = true;
    };
  }, [filtroEspecialidade, statusFiltro]);

  async function cadastrar(valores: typeof form.values) {
    setEnviando(true);
    try {
      const criado = await api<Medico>('/medicos', {
        method: 'POST',
        body: {
          nome: valores.nome,
          email: valores.email,
          crm: valores.crm,
          especialidade_id: Number(valores.especialidadeId),
        },
      });

      if (
        (!filtroEspecialidade || filtroEspecialidade === valores.especialidadeId) &&
        statusFiltro !== 'false'
      ) {
        setMedicos((atual) => [...atual, criado]);
      }

      notifications.show({ message: 'Médico cadastrado', color: 'teal' });
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

  async function alternarStatus(medico: Medico) {
    setAlterandoId(medico.id);

    try {
      const atualizado = await api<Medico>(`/medicos/${medico.id}/status`, {
        method: 'PATCH',
      });

      setMedicos((atual) => atual.map((item) => (item.id === atualizado.id ? atualizado : item)));

      notifications.show({
        message: `Médico ${atualizado.ativo ? 'ativado' : 'inativado'} com sucesso!`,
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

  const medicosFiltrados = medicos.filter((medico) => {
    if (statusFiltro === 'true') return medico.ativo === true;
    if (statusFiltro === 'false') return medico.ativo === false;
    return true;
  });

  return (
    <Stack gap="lg">
      <Group gap="xs">
        <Stethoscope size={22} />
        <Title order={2} size="h3">
          Médicos
        </Title>
      </Group>

      <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
        <Text fw={600} mb="md">
          Cadastrar novo médico
        </Text>
        <form onSubmit={form.onSubmit(cadastrar)}>
          <Stack gap="md">
            <Group grow align="flex-start" wrap="wrap">
              <Select
                label="Especialidade"
                placeholder="Selecione"
                data={opcoesEspecialidadeForm}
                withAsterisk
                {...form.getInputProps('especialidadeId')}
              />
              <TextInput
                label="CRM"
                placeholder="CRM12345"
                withAsterisk
                {...form.getInputProps('crm')}
              />
            </Group>
            <Group grow align="flex-start" wrap="wrap">
              <TextInput
                label="Nome"
                placeholder="Dra. Ana Souza"
                withAsterisk
                {...form.getInputProps('nome')}
              />
              <TextInput
                label="E-mail"
                placeholder="medico@clinica.com"
                withAsterisk
                {...form.getInputProps('email')}
              />
            </Group>
            <Group justify="flex-end">
              <Button
                type="submit"
                loading={enviando}
                disabled={opcoesEspecialidadeForm.length === 0}
              >
                Cadastrar
              </Button>
            </Group>
            {opcoesEspecialidadeForm.length === 0 && !carregando && (
              <Text size="xs" c="dimmed">
                Cadastre e ative uma especialidade antes de cadastrar um médico.
              </Text>
            )}
          </Stack>
        </form>
      </Card>

      <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
        <Group justify="space-between" align="center" mb="md" wrap="wrap">
          <Text fw={600}>Médicos cadastrados</Text>
          <Group gap="xs" wrap="wrap">
            <Select
              aria-label="Filtrar por especialidade"
              placeholder="Especialidade"
              data={opcoesEspecialidadeFiltro}
              value={filtroEspecialidade}
              onChange={(val) => {
                setFiltroEspecialidade(val);
                setCarregando(true);
              }}
              clearable
              w={{ base: '100%', xs: 200 }}
            />
            <Select
              aria-label="Filtrar por status"
              size="xs"
              w={{ base: '100%', xs: 130 }}
              value={statusFiltro}
              onChange={(val) => {
                setStatusFiltro(val || 'true');
                setCarregando(true);
              }}
              data={[
                { value: 'true', label: 'Ativos' },
                { value: 'false', label: 'Inativos' },
                { value: 'todos', label: 'Todos' },
              ]}
              allowDeselect={false}
            />
          </Group>
        </Group>

        <Table.ScrollContainer minWidth={520}>
          <Table verticalSpacing="sm">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Nome</Table.Th>
                <Table.Th>CRM</Table.Th>
                <Table.Th visibleFrom="sm">Especialidade</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th ta="right">Ações</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {medicosFiltrados.map((medico) => (
                <Table.Tr key={medico.id}>
                  <Table.Td>{medico.nome}</Table.Td>
                  <Table.Td>{medico.crm}</Table.Td>
                  <Table.Td visibleFrom="sm">
                    {nomeDaEspecialidade(medico.especialidade_id)}
                  </Table.Td>
                  <Table.Td>
                    <Badge color={medico.ativo ? 'teal' : 'gray'} variant="light">
                      {medico.ativo ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </Table.Td>
                  <Table.Td ta="right">
                    <Tooltip label={medico.ativo ? 'Inativar' : 'Ativar'}>
                      <ActionIcon
                        variant="light"
                        color={medico.ativo ? 'red' : 'green'}
                        onClick={() => alternarStatus(medico)}
                        loading={alterandoId === medico.id}
                        aria-label={medico.ativo ? 'Inativar' : 'Ativar'}
                      >
                        {medico.ativo ? <Ban size={16} /> : <CheckCircle2 size={16} />}
                      </ActionIcon>
                    </Tooltip>
                  </Table.Td>
                </Table.Tr>
              ))}
              {!carregando && medicosFiltrados.length === 0 && (
                <Table.Tr>
                  <Table.Td colSpan={5}>
                    <Text c="dimmed" ta="center" py="md">
                      Nenhum médico encontrado.
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
