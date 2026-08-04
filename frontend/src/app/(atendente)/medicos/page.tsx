'use client';

import { useEffect, useMemo, useState } from 'react';

import {
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
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { Stethoscope } from 'lucide-react';

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
  const [carregando, setCarregando] = useState(true);
  const [enviando, setEnviando] = useState(false);

  const form = useForm({
    initialValues: { nome: '', email: '', crm: '', especialidadeId: '' },
    validate: {
      nome: (valor: string) => validarNomeCompleto(valor),
      email: validarEmailObrigatorio,
      crm: (valor: string) => validarTextoMinimo(valor, 4, 'CRM inválido'),
      especialidadeId: (valor) => (valor ? null : 'Selecione uma especialidade'), // CA1
    },
  });

  const opcoesEspecialidade = useMemo(
    () => especialidades.map((e) => ({ value: String(e.id), label: e.nome })),
    [especialidades]
  );

  const nomeDaEspecialidade = useMemo(() => {
    const mapa = new Map(especialidades.map((e) => [e.id, e.nome]));
    return (id: number) => mapa.get(id) ?? `#${id}`;
  }, [especialidades]);

  async function carregar(especialidadeId?: string | null) {
    setCarregando(true);
    try {
      const query = especialidadeId ? `?especialidade_id=${especialidadeId}` : '';
      const [listaMedicos, listaEspecialidades] = await Promise.all([
        api<Medico[]>(`/medicos${query}`),
        especialidades.length === 0
          ? api<Especialidade[]>('/especialidades')
          : Promise.resolve(especialidades),
      ]);
      setMedicos(listaMedicos);
      if (especialidades.length === 0) setEspecialidades(listaEspecialidades);
    } catch (erro) {
      notifications.show({
        message: erro instanceof ApiError ? erro.message : 'Não foi possível carregar os médicos',
        color: 'red',
      });
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    queueMicrotask(() => {
      carregar();
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function aoFiltrar(valor: string | null) {
    setFiltroEspecialidade(valor);
    carregar(valor);
  }

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
      if (!filtroEspecialidade || filtroEspecialidade === valores.especialidadeId) {
        setMedicos((atual) => [...atual, criado]);
      }
      notifications.show({ message: 'Médico cadastrado', color: 'teal' });
      form.reset();
    } catch (erro) {
      // CA2 (e-mail) e CA3 (CRM) chegam aqui como 409 com mensagem pronta do backend.
      notifications.show({
        title: 'Não foi possível cadastrar',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    } finally {
      setEnviando(false);
    }
  }

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
                data={opcoesEspecialidade}
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
              <Button type="submit" loading={enviando} disabled={opcoesEspecialidade.length === 0}>
                Cadastrar
              </Button>
            </Group>
            {opcoesEspecialidade.length === 0 && !carregando && (
              <Text size="xs" c="dimmed">
                Cadastre uma especialidade antes de cadastrar um médico.
              </Text>
            )}
          </Stack>
        </form>
      </Card>

      <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
        <Group justify="space-between" mb="md" wrap="wrap">
          <Text fw={600}>Médicos cadastrados</Text>
          <Select
            placeholder="Filtrar por especialidade"
            data={opcoesEspecialidade}
            value={filtroEspecialidade}
            onChange={aoFiltrar}
            clearable
            w={{ base: '100%', xs: 240 }}
          />
        </Group>
        <Table.ScrollContainer minWidth={520}>
          <Table verticalSpacing="sm">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Nome</Table.Th>
                <Table.Th>CRM</Table.Th>
                <Table.Th visibleFrom="sm">Especialidade</Table.Th>
                <Table.Th>Status</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {medicos.map((medico) => (
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
                </Table.Tr>
              ))}
              {!carregando && medicos.length === 0 && (
                <Table.Tr>
                  <Table.Td colSpan={4}>
                    <Text c="dimmed" ta="center" py="md">
                      Nenhum médico cadastrado ainda.
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
