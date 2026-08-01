'use client';

import Link from 'next/link';
import {
    Anchor,
    Button,
    Container,
    Paper,
    PasswordInput,
    Stack,
    Text,
    TextInput,
    Title,
} from '@mantine/core';

import { useLogin } from '../_hooks/useLogin';

export function LoginForm() {
    const { form, loading, handleLoginChange, handleSubmit } = useLogin();

    return (
        <Container size={440} my={80}>
            <Paper withBorder shadow="sm" p={36} radius="lg">
                <Title order={2} ta="left" fw={700} fz={24}>
                    Acesse sua conta
                </Title>
                <Text c="dimmed" size="sm" mt={2} mb={28}>
                    Clínica Médica
                </Text>

                <form onSubmit={handleSubmit}>
                    <Stack gap="md">
                        <TextInput
                            label="CPF ou E-mail"
                            placeholder="000.000.000-00 ou seu@email.com"
                            required
                            {...form.getInputProps('login')}
                            onChange={handleLoginChange}
                            disabled={loading}
                            radius="md"
                            size="md"
                        />

                        <PasswordInput
                            label="Senha"
                            placeholder="Sua senha"
                            required
                            {...form.getInputProps('senha')}
                            disabled={loading}
                            radius="md"
                            size="md"
                        />

                        <Button
                            type="submit"
                            fullWidth
                            loading={loading}
                            disabled={loading}
                            color="#469290"
                            size="md"
                            radius="md"
                            mt="sm"
                        >
                            Entrar
                        </Button>
                    </Stack>
                </form>

                <Text ta="center" mt={24} size="sm" c="dimmed">
                    Ainda não tem acesso?{' '}
                    <Anchor component={Link} href="/primeiro-acesso" size="sm" c="#469290" fw={500}>
                        Primeiro acesso
                    </Anchor>
                </Text>
            </Paper>
        </Container>
    );
}