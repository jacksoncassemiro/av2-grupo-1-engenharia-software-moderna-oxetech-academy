'use client';

import { useEffect, useState } from 'react';

import {
  Alert,
  Button,
  Card,
  Group,
  Skeleton,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { Info, UsersRound } from 'lucide-react';

import { api, ApiError } from '@/lib/api';
import { cpfEhValido, formatarCpf } from '@/lib/cpf';
import { formatarTelefone } from '@/lib/telefone';
import dayjs from '@/lib/dayjs';
import { validarEmailOpcional, validarNomeCompleto, validarTelefone } from '@/lib/validadores';
import type { Paciente } from '@/types/dominio';

export default function PacientesPage() {
  const [enviando, setEnviando] = useState(false);
  const [carregando, setCarregando] = useState(true);
  const [pacientes, setPacientes] = useState<Paciente[]>([]);

  // Busca os pacientes do backend ao carregar a página
  useEffect(() => {
    async function carregarPacientes() {
      try {
        const dados = await api<Paciente[]>('/pacientes');
        setPacientes(dados);
      } catch (erro) {
        notifications.show({
          title: 'Erro ao carregar pacientes',
          message: erro instanceof ApiError ? erro.message : 'Falha ao buscar dados',
          color: 'red',
        });
      } finally {
        setCarregando(false);
      }
    }

    carregarPacientes();
  }, []);

  const form = useForm({
    initialValues: {
      nome: '',
      cpf: '',
      telefone: '',
      email: '',
      dataNascimento: null as Date | null,
    },
    validate: {
      nome: (valor: string) => validarNomeCompleto(valor),
      cpf: (valor) => (cpfEhValido(valor) ? null : 'CPF inválido'),
      telefone: validarTelefone,
      email: validarEmailOpcional,
    },
  });

  async function cadastrar(valores: typeof form.values) {
    setEnviando(true);
    try {
      const criado = await api<Paciente>('/pacientes', {
        method: 'POST',
        body: {
          nome: valores.nome,
          cpf: valores.cpf,
          telefone: valores.telefone,
          email: valores.email || null,
          data_nascimento: valores.dataNascimento
            ? dayjs(valores.dataNascimento).format('YYYY-MM-DD')
            : null,
        },
      });
      setPacientes((atual) => [criado, ...atual]);
      notifications.show({ message: 'Paciente cadastrado', color: 'teal' });
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

  return (
    <Stack gap="lg">
      <Group gap="xs">
        <UsersRound size={22} />
        <Title order={2} size="h3">
          Pacientes
        </Title>
      </Group>

      <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
        <Text fw={600} mb="md">
          Cadastrar novo paciente
        </Text>
        <form onSubmit={form.onSubmit(cadastrar)}>
          <Stack gap="md">
            <Group grow align="flex-start" wrap="wrap">
              <TextInput
                label="Nome completo"
                placeholder="Nome do paciente"
                description="Como no documento"
                withAsterisk
                {...form.getInputProps('nome')}
              />
              <TextInput
                label="CPF"
                placeholder="000.000.000-00"
                description="Validado por dígitos verificadores (RN07)"
                withAsterisk
                {...form.getInputProps('cpf')}
                onChange={(evento) =>
                  form.setFieldValue('cpf', formatarCpf(evento.currentTarget.value))
                }
              />
            </Group>
            <Group grow align="flex-start" wrap="wrap">
              <TextInput
                label="Telefone"
                placeholder="(82) 99999-0000"
                description="Com DDD"
                withAsterisk
                {...form.getInputProps('telefone')}
                onChange={(evento) =>
                  form.setFieldValue('telefone', formatarTelefone(evento.currentTarget.value))
                }
              />
              <TextInput
                label="E-mail"
                description="Opcional"
                placeholder="paciente@email.com"
                {...form.getInputProps('email')}
              />
            </Group>
            <DateInput
              label="Data de nascimento"
              description="Opcional"
              placeholder="Selecione a data"
              valueFormat="DD/MM/YYYY"
              dateParser={(valor) => {
                const parsed = dayjs(valor, ['DD/MM/YYYY', 'DDMMYYYY'], true);
                return parsed.isValid() ? parsed.toDate() : new Date(NaN);
              }}
              maxDate={new Date()}
              clearable
              maw={{ base: '100%', xs: 300 }}
              {...form.getInputProps('dataNascimento')}
            />

            <Alert color="blue" variant="light" icon={<Info size={18} />}>
              Este cadastro não cria credencial de login. O paciente ativa o acesso usando
              &quot;Primeiro acesso&quot; (US-00).
            </Alert>

            <Group justify="flex-end">
              <Button type="submit" loading={enviando}>
                Cadastrar paciente
              </Button>
            </Group>
          </Stack>
        </form>
      </Card>

      <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
        <Text fw={600} mb="md">
          Pacientes cadastrados
        </Text>

        {carregando ? (
          <Stack gap="xs">
            <Skeleton height={30} radius="sm" />
            <Skeleton height={30} radius="sm" />
          </Stack>
        ) : pacientes.length === 0 ? (
          <Text c="dimmed" size="sm">
            Nenhum paciente cadastrado até o momento.
          </Text>
        ) : (
          <Table.ScrollContainer minWidth={480}>
            <Table verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Nome</Table.Th>
                  <Table.Th>CPF</Table.Th>
                  <Table.Th visibleFrom="sm">Telefone</Table.Th>
                  <Table.Th visibleFrom="sm">E-mail</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {pacientes.map((paciente) => (
                  <Table.Tr key={paciente.id}>
                    <Table.Td>{paciente.nome}</Table.Td>
                    <Table.Td>{formatarCpf(paciente.cpf)}</Table.Td>
                    <Table.Td visibleFrom="sm">{paciente.telefone}</Table.Td>
                    <Table.Td visibleFrom="sm">
                      <Text c="dimmed" size="sm">
                        {paciente.email || '—'}
                      </Text>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Card>
    </Stack>
  );
}
