'use client';

import { Alert, Button, PasswordInput, Stack, TextInput } from '@mantine/core';
import { useForm } from '@mantine/form';

import { formatarCpf } from '@/lib/cpf';
import {
  mensagemCadastroEncontrado,
  validarConfirmacaoDeSenha,
  validarSenha,
} from '@/lib/primeiro-acesso';

interface Props {
  cpf: string;
  nome: string;
  onEnviar: (senha: string) => void;
  carregando: boolean;
}

/**
 * Etapa 2 da US-00, caminho CA4: o atendente ja cadastrou o paciente no balcao,
 * falta so a credencial. CPF e nome ficam em leitura — quem os define e o cadastro.
 */
export function FormularioAtivarLogin({ cpf, nome, onEnviar, carregando }: Props) {
  const form = useForm({
    initialValues: { senha: '', confirmacao: '' },
    validate: {
      senha: (valor) => validarSenha(valor),
      confirmacao: (valor, valores) => validarConfirmacaoDeSenha(valor, valores.senha),
    },
  });

  return (
    <Stack gap="md">
      <Alert color="green" title="Cadastro encontrado">
        {mensagemCadastroEncontrado(nome)}
      </Alert>

      <form onSubmit={form.onSubmit((valores) => onEnviar(valores.senha))}>
        <Stack gap="md">
          <TextInput label="CPF" value={formatarCpf(cpf)} disabled readOnly />
          <TextInput label="Nome" value={nome} disabled readOnly />

          <PasswordInput
            label="Criar senha"
            placeholder="Mínimo 6 caracteres"
            withAsterisk
            {...form.getInputProps('senha')}
          />
          <PasswordInput
            label="Confirmar senha"
            placeholder="Repita a senha"
            withAsterisk
            {...form.getInputProps('confirmacao')}
          />

          <Button type="submit" size="md" fullWidth loading={carregando}>
            Ativar meu acesso
          </Button>
        </Stack>
      </form>
    </Stack>
  );
}
