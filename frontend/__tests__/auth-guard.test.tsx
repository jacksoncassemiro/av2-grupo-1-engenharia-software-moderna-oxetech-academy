import { render, screen, waitFor } from '@test-utils';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { AuthGuard } from '@/components/auth/AuthGuard';
import { guardarToken } from '@/lib/api';
import { guardarTipoUsuario } from '@/lib/auth';

const replaceMock = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    replace: replaceMock,
  }),
}));

describe('AuthGuard', () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it('redireciona para /login quando nao ha sessao', async () => {
    render(
      <AuthGuard perfil="PACIENTE">
        <div>conteudo protegido</div>
      </AuthGuard>
    );

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith('/login');
    });
  });

  it('redireciona para a area correta quando o perfil nao coincide', async () => {
    guardarToken('token-fake');
    guardarTipoUsuario('ATENDENTE');

    render(
      <AuthGuard perfil="PACIENTE">
        <div>conteudo protegido</div>
      </AuthGuard>
    );

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith('/agenda');
    });
  });

  it('mantem o conteudo quando o perfil coincide', async () => {
    guardarToken('token-fake');
    guardarTipoUsuario('PACIENTE');

    render(
      <AuthGuard perfil="PACIENTE">
        <div>conteudo protegido</div>
      </AuthGuard>
    );

    await waitFor(() => {
      expect(screen.getByText('conteudo protegido')).toBeInTheDocument();
    });
    expect(replaceMock).not.toHaveBeenCalled();
  });
});
