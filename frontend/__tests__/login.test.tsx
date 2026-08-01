import { render, screen, fireEvent, waitFor } from '@test-utils';
import { notifications } from '@mantine/notifications';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import LoginPage from '@/app/login/page';
import * as apiModule from '@/lib/api';

const pushMock = vi.fn();
vi.mock('next/navigation', () => ({
    useRouter: () => ({
        push: pushMock,
    }),
}));

describe('US00 - Tela de Login', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('RN07 - deve aplicar máscara de CPF ao digitar números', () => {
        render(<LoginPage />);
        const input = screen.getByLabelText(/CPF ou E-mail/i) as HTMLInputElement;

        fireEvent.change(input, { target: { value: '52998224725' } });
        expect(input.value).toBe('529.982.247-25');
    });

    it('deve efetuar login do paciente e redirecionar para /consultas (CA1)', async () => {
        const apiSpy = vi.spyOn(apiModule, 'api').mockResolvedValueOnce({
            access_token: 'token-jwt-fake',
            token_type: 'bearer',
            tipo_usuario: 'PACIENTE',
        });

        render(<LoginPage />);

        fireEvent.change(screen.getByLabelText(/CPF ou E-mail/i), {
            target: { value: '529.982.247-25' },
        });
        fireEvent.change(screen.getByLabelText(/Senha/i), {
            target: { value: 'senha123' },
        });

        fireEvent.click(screen.getByRole('button', { name: /Entrar/i }));

        await waitFor(() => {
            expect(apiSpy).toHaveBeenCalledWith('/auth/login', {
                method: 'POST',
                body: { login: '52998224725', senha: 'senha123' },
            });
            expect(pushMock).toHaveBeenCalledWith('/consultas');
        });
    });

    it('CA7 - deve exibir mensagem generica quando o login falha com 401', async () => {
        vi.spyOn(apiModule, 'api').mockRejectedValueOnce(new apiModule.ApiError('Login ou senha invalidos', 401));
        const notificationSpy = vi.spyOn(notifications, 'show').mockImplementation(() => 'notification-id');

        render(<LoginPage />);

        fireEvent.change(screen.getByLabelText(/CPF ou E-mail/i), {
            target: { value: '52998224725' },
        });
        fireEvent.change(screen.getByLabelText(/Senha/i), {
            target: { value: 'senhaerrada' },
        });

        fireEvent.click(screen.getByRole('button', { name: /Entrar/i }));

        await waitFor(() => {
            expect(notificationSpy).toHaveBeenCalledWith(
                expect.objectContaining({
                    title: 'Erro ao entrar',
                    message: 'Login ou senha invalidos',
                    color: 'red',
                })
            );
            expect(pushMock).not.toHaveBeenCalled();
        });
    });
});