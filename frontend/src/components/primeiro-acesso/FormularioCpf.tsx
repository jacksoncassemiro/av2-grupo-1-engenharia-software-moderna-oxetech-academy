'use client';

import { Button, Stack, Text, TextInput } from '@mantine/core';
import { useForm } from '@mantine/form';

import { cpfEhValido, formatarCpf } from '@/lib/cpf';

interface Props {
  onVerificar: (cpf: string) => void;
  carregando: boolean;
}

/** Etapa 1 da US-00: descobre se o CPF ja tem cadastro e/ou login. */
export function FormularioCpf({ onVerificar, carregando }: Props) {
  const form = useForm({
    initialValues: { cpf: '' },
    validate: {
      cpf: (valor) => (cpfEhValido(valor) ? null : 'CPF inválido'), // RN07
    },
  });

  return (
    <form onSubmit={form.onSubmit((valores) => onVerificar(valores.cpf))}>
      <Stack gap="md">
        <Text c="dimmed" size="sm">
          Informe seu CPF para verificarmos se você já tem cadastro na clínica.
        </Text>

        <TextInput
          label="CPF"
          placeholder="000.000.000-00"
          description="Pode digitar com ou sem pontos e traço"
          withAsterisk
          {...form.getInputProps('cpf')}
          onChange={(evento) => form.setFieldValue('cpf', formatarCpf(evento.currentTarget.value))}
        />

        <Button type="submit" size="md" fullWidth loading={carregando}>
          Verificar
        </Button>
      </Stack>
    </form>
  );
}
