'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';

import { apenasDigitos, cpfEhValido, formatarCpf, pareceEmail } from '@/lib/cpf';
import { realizarLogin } from '../_services/auth.service';

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

    const handleLoginChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const rawValue = event.currentTarget.value;
        const contemLetraOuAt = /[a-zA-Z@]/.test(rawValue);

        if (contemLetraOuAt) {
            const semMascaraCpf = rawValue
                .replace(/^(\d{3})\.(\d{3})\.(\d{3})-(\d{1,2})/, '$1$2$3$4')
                .replace(/^(\d{3})\.(\d{3})\.(.*)/, '$1$2$3')
                .replace(/^(\d{3})\.(.*)/, '$1$2')
                .replace(/-/g, '');

            form.setFieldValue('login', semMascaraCpf);
        } else {
            form.setFieldValue('login', formatarCpf(rawValue));
        }
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

            if (resposta.tipo_usuario === 'PACIENTE') {
                router.push('/consultas');
            } else if (resposta.tipo_usuario === 'ATENDENTE') {
                router.push('/agenda');
            }
        } catch {
            notifications.show({
                title: 'Erro ao entrar',
                message: 'Login ou senha invalidos',
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