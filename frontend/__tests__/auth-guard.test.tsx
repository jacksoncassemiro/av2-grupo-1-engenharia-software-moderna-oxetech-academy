import { render, screen, waitFor } from '@test-utils';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { AuthGuard } from '@/components/auth/AuthGuard';
// Usa guardarTipoUsuario de api.ts (chave 'clinica.tipoUsuario') — a mesma que
// o AuthGuard lê via lerTipoUsuario(). O arquivo auth.ts usa uma chave diferente
// ('clinica.tipo_usuario') e não deve ser usado nos testes do AuthGuard.
import { guardarTipoUsuario, guardarToken } from '@/lib/api';

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

  it('redireciona para a home correta quando o perfil nao coincide (ATENDENTE tentando area de PACIENTE)', async () => {
    guardarToken('token-fake');
    // ATENDENTE logado tentando acessar uma rota de PACIENTE
    guardarTipoUsuario('ATENDENTE');

    render(
      <AuthGuard perfil="PACIENTE">
        <div>conteudo protegido</div>
      </AuthGuard>
    );

    // ATENDENTE deve ser mandado para sua home: /gerenciar-consultas (corrigido de /agenda)
    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith('/gerenciar-consultas');
    });
  });

  it('redireciona para a home correta quando o perfil nao coincide (PACIENTE tentando area de ATENDENTE)', async () => {
    guardarToken('token-fake');
    // PACIENTE logado tentando acessar uma rota de ATENDENTE
    guardarTipoUsuario('PACIENTE');

    render(
      <AuthGuard perfil="ATENDENTE">
        <div>conteudo protegido</div>
      </AuthGuard>
    );

    // PACIENTE deve ser mandado para sua home: /consultas
    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith('/consultas');
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
