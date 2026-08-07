import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, userEvent, waitFor } from '@test-utils';
import { notifications } from '@mantine/notifications';
import MeusDadosPage from '@/app/(paciente)/meus-dados/page';
import * as apiModule from '@/lib/api';
import { api } from '@/lib/api';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof apiModule>('@/lib/api');
  return {
    ...actual,
    api: vi.fn(),
  };
});

vi.mock('@mantine/notifications', () => ({
  notifications: {
    show: vi.fn(),
  },
}));

describe('MeusDadosPage', () => {
  const mockPaciente = {
    id: '1',
    nome: 'Carlos Eduardo Santos',
    cpf: '52998224725',
    telefone: '(82) 99999-8888',
    email: 'carlos@email.com',
    data_nascimento: '1995-05-15',
  };

  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(api).mockImplementation(async (url, config) => {
      if (url === '/pacientes/me' && (!config || config.method === 'GET')) {
        return mockPaciente;
      }
      return {};
    });
  });

  // --- CENÁRIOS DE CARREGAMENTO INICIAL ---

  it('deve carregar e preencher os dados do paciente nos campos', async () => {
    render(<MeusDadosPage />);

    await waitFor(() => {
      expect(screen.getByLabelText(/cpf/i)).toHaveValue('529.982.247-25');
    });

    expect(screen.getByLabelText(/cpf/i)).toBeDisabled();
    expect(screen.getByLabelText(/nome completo/i)).toHaveValue('Carlos Eduardo Santos');
    expect(screen.getByLabelText(/telefone/i)).toHaveValue('(82) 99999-8888');
    expect(screen.getByLabelText(/e-mail/i)).toHaveValue('carlos@email.com');
  });

  it('deve exibir notificação de erro quando falhar ao carregar dados com ApiError', async () => {
    const erroApi = new apiModule.ApiError('Sessão expirada', 401);
    vi.mocked(api).mockRejectedValueOnce(erroApi);

    render(<MeusDadosPage />);

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith({
        message: 'Sessão expirada',
        color: 'red',
      });
    });
  });

  it('deve exibir mensagem padrão de erro quando ocorrer falha inesperada no carregamento', async () => {
    vi.mocked(api).mockRejectedValueOnce(new Error('Network Failure'));

    render(<MeusDadosPage />);

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith({
        message: 'Não foi possível carregar seus dados',
        color: 'red',
      });
    });
  });

  // --- CENÁRIOS DE ACERTO (SUCESSO NA EDIÇÃO) ---

  it('deve atualizar os dados do paciente com sucesso', async () => {
    vi.mocked(api).mockImplementation(async (url, config) => {
      if (url === '/pacientes/me' && (!config || config.method === 'GET')) {
        return mockPaciente;
      }
      if (url === '/pacientes/me' && config?.method === 'PUT') {
        return { ...mockPaciente, nome: 'Carlos Eduardo Editado' };
      }
      return {};
    });

    render(<MeusDadosPage />);

    await waitFor(() => {
      expect(screen.getByLabelText(/nome completo/i)).toHaveValue('Carlos Eduardo Santos');
    });

    const inputNome = screen.getByLabelText(/nome completo/i);
    await userEvent.clear(inputNome);
    await userEvent.type(inputNome, 'Carlos Eduardo Editado');

    await userEvent.click(screen.getByRole('button', { name: /salvar alterações/i }));

    await waitFor(() => {
      expect(api).toHaveBeenCalledWith('/pacientes/me', {
        method: 'PUT',
        body: {
          nome: 'Carlos Eduardo Editado',
          telefone: '(82) 99999-8888',
          email: 'carlos@email.com',
          data_nascimento: '1995-05-15',
        },
      });
    });

    expect(notifications.show).toHaveBeenCalledWith({
      message: 'Dados atualizados',
      color: 'teal',
    });
  });

  it('deve enviar null para campos opcionais (e-mail e data) quando estiverem vazios', async () => {
    const mockPacienteSemOpcionais = {
      ...mockPaciente,
      email: null,
      data_nascimento: null,
    };

    vi.mocked(api).mockImplementation(async (url, config) => {
      if (url === '/pacientes/me' && (!config || config.method === 'GET')) {
        return mockPacienteSemOpcionais;
      }
      if (url === '/pacientes/me' && config?.method === 'PUT') {
        return mockPacienteSemOpcionais;
      }
      return {};
    });

    render(<MeusDadosPage />);

    await waitFor(() => {
      expect(screen.getByLabelText(/nome completo/i)).toHaveValue('Carlos Eduardo Santos');
    });

    await userEvent.click(screen.getByRole('button', { name: /salvar alterações/i }));

    await waitFor(() => {
      expect(api).toHaveBeenCalledWith('/pacientes/me', {
        method: 'PUT',
        body: {
          nome: 'Carlos Eduardo Santos',
          telefone: '(82) 99999-8888',
          email: null,
          data_nascimento: null,
        },
      });
    });
  });

  // --- CENÁRIOS DE ERRO (FALHAS NO SALVAMENTO) ---

  it('deve exibir notificação com mensagem da API quando o salvamento falhar com ApiError', async () => {
    const error400 = new apiModule.ApiError('E-mail já está em uso por outro usuário', 400);

    vi.mocked(api).mockImplementation(async (url, config) => {
      if (url === '/pacientes/me' && (!config || config.method === 'GET')) {
        return mockPaciente;
      }
      if (url === '/pacientes/me' && config?.method === 'PUT') {
        throw error400;
      }
      return {};
    });

    render(<MeusDadosPage />);

    await waitFor(() => {
      expect(screen.getByLabelText(/nome completo/i)).toHaveValue('Carlos Eduardo Santos');
    });

    await userEvent.click(screen.getByRole('button', { name: /salvar alterações/i }));

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith({
        title: 'Não foi possível salvar',
        message: 'E-mail já está em uso por outro usuário',
        color: 'red',
      });
    });
  });

  it('deve exibir "Falha inesperada" quando ocorrer erro genérico ao salvar', async () => {
    vi.mocked(api).mockImplementation(async (url, config) => {
      if (url === '/pacientes/me' && (!config || config.method === 'GET')) {
        return mockPaciente;
      }
      if (url === '/pacientes/me' && config?.method === 'PUT') {
        throw new Error('Internal Server Error');
      }
      return {};
    });

    render(<MeusDadosPage />);

    await waitFor(() => {
      expect(screen.getByLabelText(/nome completo/i)).toHaveValue('Carlos Eduardo Santos');
    });

    await userEvent.click(screen.getByRole('button', { name: /salvar alterações/i }));

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith({
        title: 'Não foi possível salvar',
        message: 'Falha inesperada',
        color: 'red',
      });
    });
  });
});
