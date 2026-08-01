'use client';

import { Alert, Button, Divider, PasswordInput, Stack, TextInput } from '@mantine/core';
import { useForm } from '@mantine/form';

import { formatarCpf } from '@/lib/cpf';
import {
  validarConfirmacaoDeSenha,
  validarEmailOpcional,
  validarNome,
  validarSenha,
  validarTelefone,
} from '@/lib/primeiro-acesso';
import type { PrimeiroAcessoRequisicao } from '@/types/dominio';

type DadosDoCadastro = Omit<PrimeiroAcessoRequisicao, 'cpf'>;

interface Props {
  cpf: string;
  onEnviar: (dados: DadosDoCadastro) => void;
  carregando: boolean;
}

/**
 * Etapa 2 da US-00, caminho CA5: CPF sem cadastro nenhum. Cadastro do paciente e
 * credencial nascem na mesma requisicao — e o que resolve o conflito do enunciado
 * registrado no ADR-005.
 */
export function FormularioAutoCadastro({ cpf, onEnviar, carregando }: Props) {
  const form = useForm({
    initialValues: { nome: '', telefone: '', email: '', senha: '', confirmacao: '' },
    validate: {
      nome: (valor) => validarNome(valor),
      telefone: (valor) => validarTelefone(valor),
      email: (valor) => validarEmailOpcional(valor), // RN08
      senha: (valor) => validarSenha(valor),
      confirmacao: (valor, valores) => validarConfirmacaoDeSenha(valor, valores.senha),
    },
  });

  function enviar(valores: typeof form.values) {
    const email = valores.email.trim();
    onEnviar({
      nome: valores.nome.trim(),
      telefone: valores.telefone.trim(),
      senha: valores.senha,
      // E-mail e opcional (RN02): mandar string vazia quebraria o EmailStr do backend.
      ...(email === '' ? {} : { email }),
    });
  }

  return (
    <Stack gap="md">
      <Alert color="blue" title="CPF não encontrado">
        Preencha seus dados para se cadastrar.
      </Alert>

      <form onSubmit={form.onSubmit(enviar)}>
        <Stack gap="md">
          <TextInput label="CPF" value={formatarCpf(cpf)} disabled readOnly />

          <TextInput
            label="Nome completo"
            placeholder="Seu nome completo"
            withAsterisk
            {...form.getInputProps('nome')}
          />
          <TextInput
            label="Telefone"
            placeholder="(82) 99999-0000"
            withAsterisk
            {...form.getInputProps('telefone')}
          />
          <TextInput
            label="E-mail"
            description="Opcional"
            placeholder="seu@email.com"
            {...form.getInputProps('email')}
          />

          <Divider />

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
            Criar minha conta
          </Button>
        </Stack>
      </form>
    </Stack>
  );
}
