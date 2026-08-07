'use client';

import { useState, type ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';

import { HOME_POR_PERFIL } from '@/components/auth/AuthGuard';
import { ApiError } from '@/lib/api';
import { apenasDigitos, cpfEhValido, formatarCpf, pareceEmail } from '@/lib/cpf';
import { realizarLogin } from './auth.service';

export function useLogin() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const form = useForm({
    initialValues: {
      login: '',
      senha: '',
    },
    validate: {
      login: (value) => {
        const val = value.trim();
        if (!val) return 'Informe o CPF ou E-mail';

        if (pareceEmail(val)) {
          const emailRegex = /^\S+@\S+\.\S+$/;
          return emailRegex.test(val) ? null : 'E-mail em formato inválido';
        }

        return cpfEhValido(val) ? null : 'CPF inválido';
      },
      senha: (value) => (value ? null : 'Informe a senha'),
    },
  });

  const handleLoginChange = (event: ChangeEvent<HTMLInputElement>) => {
    const rawValue = event.currentTarget.value;

    if (/[a-zA-Z@]/.test(rawValue)) {
      form.setFieldValue('login', rawValue);
      return;
    }

    form.setFieldValue('login', formatarCpf(rawValue));
  };

  const handleSubmit = async (values: typeof form.values) => {
    setLoading(true);

    try {
      const loginLimpo = pareceEmail(values.login)
        ? values.login.trim().toLowerCase()
        : apenasDigitos(values.login);

      const resposta = await realizarLogin({
        login: loginLimpo,
        senha: values.senha,
      });

      // Uma unica fonte de verdade para a home de cada perfil (a mesma que o
      // AuthGuard e o proxy.ts usam), senao o login manda para uma rota e o
      // guard redireciona para outra logo em seguida.
      router.push(HOME_POR_PERFIL[resposta.tipo_usuario] ?? '/login');
    } catch (erro) {
      const mensagem =
        erro instanceof ApiError && erro.status === 401
          ? 'Login ou senha invalidos'
          : 'Falha ao entrar. Tente novamente.';

      notifications.show({
        title: 'Erro ao entrar',
        message: mensagem,
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  return {
    form,
    loading,
    handleLoginChange,
    handleSubmit: form.onSubmit(handleSubmit),
  };
}
