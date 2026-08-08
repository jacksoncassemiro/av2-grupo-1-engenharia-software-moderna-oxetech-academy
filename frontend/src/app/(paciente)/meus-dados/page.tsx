'use client';

import { useEffect, useState } from 'react';

import { Button, Card, Group, LoadingOverlay, Stack, Text, TextInput, Title } from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';

import { api, ApiError } from '@/lib/api';
import dayjs from '@/lib/dayjs';
import { formatarCpf } from '@/lib/cpf';
import { formatarTelefone } from '@/lib/telefone';
import { validarEmailOpcional, validarNomeCompleto, validarTelefone } from '@/lib/validadores';
import type { Paciente } from '@/types/dominio';

export default function MeusDadosPage() {
  const [carregando, setCarregando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [cpf, setCpf] = useState('');

  const form = useForm({
    initialValues: {
      nome: '',
      telefone: '',
      email: '',
      dataNascimento: null as Date | null,
    },
    validate: {
      nome: (valor: string) => validarNomeCompleto(valor),
      telefone: validarTelefone,
      email: validarEmailOpcional,
    },
  });

  useEffect(() => {
    api<Paciente>('/pacientes/me')
      .then((paciente) => {
        setCpf(paciente.cpf);

        form.setValues({
          nome: paciente.nome,
          telefone: paciente.telefone,
          email: paciente.email ?? '',
          dataNascimento: paciente.data_nascimento
            ? dayjs(paciente.data_nascimento).toDate()
            : null,
        });
      })
      .catch((erro) => {
        notifications.show({
          message: erro instanceof ApiError ? erro.message : 'Não foi possível carregar seus dados',
          color: 'red',
        });
      })
      .finally(() => setCarregando(false));

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function salvar(valores: typeof form.values) {
    setEnviando(true);

    try {
      await api('/pacientes/me', {
        method: 'PUT',
        body: {
          nome: valores.nome,
          telefone: valores.telefone,
          email: valores.email || null,
          data_nascimento: valores.dataNascimento
            ? dayjs(valores.dataNascimento).format('YYYY-MM-DD')
            : null,
        },
      });

      notifications.show({
        message: 'Dados atualizados',
        color: 'teal',
      });
    } catch (erro) {
      notifications.show({
        title: 'Não foi possível salvar',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Stack gap="md">
      <Title order={2}>Meus Dados</Title>

      <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }} pos="relative">
        <LoadingOverlay visible={carregando} />

        <form onSubmit={form.onSubmit(salvar)}>
          <Stack gap="md">
            <TextInput
              label="CPF"
              value={formatarCpf(cpf)}
              disabled
              description="CPF não pode ser alterado"
            />

            <TextInput label="Nome completo" withAsterisk {...form.getInputProps('nome')} />

            <TextInput
              label="Telefone"
              placeholder="(82) 99999-0000"
              withAsterisk
              {...form.getInputProps('telefone')}
              onChange={(evento) =>
                form.setFieldValue('telefone', formatarTelefone(evento.currentTarget.value))
              }
            />

            <TextInput label="E-mail" description="Opcional" {...form.getInputProps('email')} />

            <DateInput
              label="Data de nascimento"
              description="Opcional"
              placeholder="Selecione a data"
              valueFormat="DD/MM/YYYY"
              // Mesmo parser do cadastro em (atendente)/pacientes: aceita `10/03/1990` e
              // `10031990` digitados, e recusa o resto. Sem ele as duas telas se comportavam
              // de um jeito diferente para o mesmo campo.
              dateParser={(valor) => {
                const parsed = dayjs(valor, ['DD/MM/YYYY', 'DDMMYYYY'], true);
                return parsed.isValid() ? parsed.toDate() : new Date(NaN);
              }}
              maxDate={new Date()}
              clearable
              maw={{ base: '100%', xs: 300 }}
              {...form.getInputProps('dataNascimento')}
            />

            <Group justify="flex-end">
              <Button type="submit" loading={enviando}>
                Salvar alterações
              </Button>
            </Group>
          </Stack>
        </form>
      </Card>

      <Text size="xs" c="dimmed">
        Cancelamentos e histórico ficam em{' '}
        <Text component="span" fw={600}>
          Minhas Consultas
        </Text>
        , no menu.
      </Text>
    </Stack>
  );
}
