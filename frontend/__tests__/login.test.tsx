import { render, screen, fireEvent, waitFor } from '@test-utils';
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

    it('deve aplicar máscara de CPF ao digitar números', () => {
        render(<LoginPage />);
        const input = screen.getByLabelText(/CPF ou E-mail/i) as HTMLInputElement;

        fireEvent.change(input, { target: { value: '52998224725' } });
        expect(input.value).toBe('529.982.247-25');
    });

    it('deve efetuar login do paciente e redirecionar para /consultas (CA1)', async () => {
        const apiSpy = vi.spyOn(apiModule, 'api').mockResolvedValueOnce({
            token: 'token-jwt-fake',
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
});