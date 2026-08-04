'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { Anchor, Button, Divider, PasswordInput, Stack, Text, TextInput, Title } from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { Sparkles } from 'lucide-react';

import { AuthShell } from '@/components/AuthShell';
import { api, ApiError, guardarTipoUsuario, guardarToken } from '@/lib/api';
import { formatarCpf } from '@/lib/cpf';
import type { TokenResposta } from '@/types/dominio';

export default function LoginPage() {
  const router = useRouter();
  const [enviando, setEnviando] = useState(false);

  const form = useForm({
    initialValues: { login: '', senha: '' },
    validate: {
      login: (valor) => (valor.trim().length < 3 ? 'Informe seu CPF ou e-mail' : null),
      senha: (valor) => (valor.length < 6 ? 'A senha deve ter ao menos 6 caracteres' : null),
    },
  });

  function aoDigitarLogin(valor: string) {
    // CA2: aplica mascara de CPF enquanto digita, mas so quando o que foi digitado ate
    // agora e compativel com CPF (so digitos/pontuacao) - senao a mascara mutila um
    // e-mail que o usuario ainda esta no meio de digitar (US-00).
    const podeSerCpf = /^[\d.-]*$/.test(valor);
    form.setFieldValue('login', podeSerCpf ? formatarCpf(valor) : valor);
  }

  async function enviar(valores: typeof form.values) {
    setEnviando(true);
    try {
      const resposta = await api<TokenResposta>('/auth/login', {
        method: 'POST',
        body: { login: valores.login, senha: valores.senha },
      });
      guardarToken(resposta.access_token);
      guardarTipoUsuario(resposta.tipo_usuario);

      router.push(resposta.tipo_usuario === 'ATENDENTE' ? '/gerenciar-consultas' : '/consultas');
    } catch (erro) {
      // CA7: credencial invalida chega aqui como 401 com mensagem pronta do backend.
      notifications.show({
        title: 'Não foi possível entrar',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada. Tente novamente.',
        color: 'red',
      });
    } finally {
      setEnviando(false);
    }
  }

  return (
    <AuthShell>
      <Title order={1} size="h3" ta="center" mb={4}>
        Bem-vindo de volta
      </Title>
      <Text c="dimmed" size="sm" ta="center" mb="lg">
        Entre com suas credenciais para acessar o sistema
      </Text>

      <form onSubmit={form.onSubmit(enviar)}>
        <Stack gap="md">
          <TextInput
            label="CPF ou E-mail"
            placeholder="Digite seu CPF ou e-mail"
            description="Paciente: digite o CPF · Atendente: digite o e-mail profissional"
            withAsterisk
            {...form.getInputProps('login')}
            onChange={(evento) => aoDigitarLogin(evento.currentTarget.value)}
          />
          <PasswordInput
            label="Senha"
            placeholder="Sua senha"
            withAsterisk
            {...form.getInputProps('senha')}
          />
          <Button type="submit" size="md" fullWidth loading={enviando} mt="xs">
            Entrar
          </Button>
        </Stack>
      </form>

      <Divider label="ou" my="lg" />

      <Button
        component={Link}
        href="/primeiro-acesso"
        variant="light"
        fullWidth
        leftSection={<Sparkles size={16} />}
      >
        Primeiro acesso
      </Button>
      <Text ta="center" size="xs" c="dimmed" mt="sm">
        Nunca entrou no sistema?{' '}
        <Anchor component={Link} href="/primeiro-acesso" size="xs">
          Ative seu login pelo CPF
        </Anchor>
      </Text>
    </AuthShell>
  );
}
