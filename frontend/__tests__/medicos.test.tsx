import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, userEvent, within } from '@test-utils';
import { notifications } from '@mantine/notifications';
import MedicosPage from '@/app/(atendente)/medicos/page';
import * as apiModule from '@/lib/api';

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

describe('MedicosPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockApiPadrao = (
    medicos: unknown[] = [],
    especialidades = [{ id: 1, nome: 'Cardiologia', ativo: true }]
  ) => {
    vi.mocked(apiModule.api).mockImplementation(async (endpoint) => {
      if (endpoint.includes('/especialidades')) return especialidades;
      if (endpoint.includes('/medicos')) return medicos;
      return [];
    });
  };

  it('deve exibir erro ao tentar cadastrar sem especialidade (CA1)', async () => {
    mockApiPadrao();

    render(<MedicosPage />);

    await screen.findByPlaceholderText('Selecione');
    await userEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    expect(await screen.findByText('Selecione uma especialidade')).toBeInTheDocument();
  });

  it('deve listar medicos corretamente (CA4)', async () => {
    const mockMedicos = [
      { id: 1, nome: 'Dr. Teste', crm: '12345', especialidade_id: 1, ativo: true },
    ];
    mockApiPadrao(mockMedicos);

    render(<MedicosPage />);

    const tabela = await screen.findByRole('table');
    expect(within(tabela).getByText('Dr. Teste')).toBeInTheDocument();
    expect(within(tabela).getByText('12345')).toBeInTheDocument();
    expect(within(tabela).getByText('Cardiologia')).toBeInTheDocument();
  });

  it('deve exibir erros de validação nos campos quando enviados com dados inválidos', async () => {
    mockApiPadrao();

    render(<MedicosPage />);

    await screen.findByPlaceholderText('Selecione');

    await userEvent.type(screen.getByLabelText(/nome/i), 'Ab');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'email-invalido');
    await userEvent.type(screen.getByLabelText(/crm/i), '12');

    await userEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    expect(
      await screen.findByText((content, element) => {
        const tag = element?.tagName.toLowerCase();
        return /nome/i.test(content) && tag !== 'label' && tag !== 'th';
      })
    ).toBeInTheDocument();

    expect(screen.getByText('E-mail inválido')).toBeInTheDocument();
    expect(screen.getByText('CRM inválido')).toBeInTheDocument();
    expect(screen.getByText('Selecione uma especialidade')).toBeInTheDocument();
  });

  it('deve exibir notificação de erro quando a API falhar ao carregar os dados iniciais', async () => {
    vi.mocked(apiModule.api).mockRejectedValue(new Error('Erro de conexão'));

    render(<MedicosPage />);

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Não foi possível carregar as especialidades',
          color: 'red',
        })
      );
    });
  });

  it('deve exibir alerta informativo quando não houver especialidades ativas cadastradas', async () => {
    mockApiPadrao([], []);

    render(<MedicosPage />);

    expect(
      await screen.findByText('Cadastre e ative uma especialidade antes de cadastrar um médico.')
    ).toBeInTheDocument();
  });

  it('deve exibir notificação quando a API retornar 409 com conflito de e-mail', async () => {
    mockApiPadrao();

    render(<MedicosPage />);

    await userEvent.type(await screen.findByLabelText(/nome/i), 'Dr. João Silva');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'joao@teste.com');
    await userEvent.type(screen.getByLabelText(/crm/i), '123456');

    const select = screen.getByPlaceholderText('Selecione');
    await userEvent.click(select);
    await userEvent.click(await screen.findByRole('option', { name: 'Cardiologia' }));

    const error409 = new apiModule.ApiError('Este e-mail já está cadastrado', 409);
    vi.mocked(apiModule.api).mockImplementation(async (endpoint, options) => {
      if (options?.method === 'POST') throw error409;
      if (endpoint.includes('/especialidades'))
        return [{ id: 1, nome: 'Cardiologia', ativo: true }];
      return [];
    });

    await userEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Não foi possível cadastrar',
          message: 'Este e-mail já está cadastrado',
          color: 'red',
        })
      );
    });
  });

  it('deve exibir notificação quando a API retornar 409 com conflito de CRM', async () => {
    mockApiPadrao();

    render(<MedicosPage />);

    await userEvent.type(await screen.findByLabelText(/nome/i), 'Dr. João Silva');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'joao@teste.com');
    await userEvent.type(screen.getByLabelText(/crm/i), '123456');

    const select = screen.getByPlaceholderText('Selecione');
    await userEvent.click(select);
    await userEvent.click(await screen.findByRole('option', { name: 'Cardiologia' }));

    const error409 = new apiModule.ApiError('CRM já cadastrado no sistema', 409);
    vi.mocked(apiModule.api).mockImplementation(async (endpoint, options) => {
      if (options?.method === 'POST') throw error409;
      if (endpoint.includes('/especialidades'))
        return [{ id: 1, nome: 'Cardiologia', ativo: true }];
      return [];
    });

    await userEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Não foi possível cadastrar',
          message: 'CRM já cadastrado no sistema',
          color: 'red',
        })
      );
    });
  });

  it('deve exibir notificação quando a API retornar ApiError com erro do servidor (500)', async () => {
    mockApiPadrao();

    render(<MedicosPage />);

    await userEvent.type(await screen.findByLabelText(/nome/i), 'Dr. João Silva');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'joao@teste.com');
    await userEvent.type(screen.getByLabelText(/crm/i), '123456');

    const select = screen.getByPlaceholderText('Selecione');
    await userEvent.click(select);
    await userEvent.click(await screen.findByRole('option', { name: 'Cardiologia' }));

    const error500 = new apiModule.ApiError('Erro interno no servidor', 500);
    vi.mocked(apiModule.api).mockImplementation(async (endpoint, options) => {
      if (options?.method === 'POST') throw error500;
      if (endpoint.includes('/especialidades'))
        return [{ id: 1, nome: 'Cardiologia', ativo: true }];
      return [];
    });

    await userEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Não foi possível cadastrar',
          message: 'Erro interno no servidor',
        })
      );
    });
  });

  it('deve exibir "Falha inesperada" ao ocorrer um erro genérico no cadastro', async () => {
    mockApiPadrao();

    render(<MedicosPage />);

    await userEvent.type(await screen.findByLabelText(/nome/i), 'Dr. João Silva');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'joao@teste.com');
    await userEvent.type(screen.getByLabelText(/crm/i), '123456');

    const select = screen.getByPlaceholderText('Selecione');
    await userEvent.click(select);
    await userEvent.click(await screen.findByRole('option', { name: 'Cardiologia' }));

    vi.mocked(apiModule.api).mockImplementation(async (endpoint, options) => {
      if (options?.method === 'POST') throw new Error('Network drop');
      if (endpoint.includes('/especialidades'))
        return [{ id: 1, nome: 'Cardiologia', ativo: true }];
      return [];
    });

    await userEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Não foi possível cadastrar',
          message: 'Falha inesperada',
        })
      );
    });
  });

  it('deve alternar status do médico com sucesso via rota PATCH', async () => {
    const mockMedico = { id: 1, nome: 'Dr. Teste', crm: '12345', especialidade_id: 1, ativo: true };
    const mockMedicoInativado = { ...mockMedico, ativo: false };

    vi.mocked(apiModule.api).mockImplementation(
      async (endpoint: string, options?: { method?: string }) => {
        if (endpoint === '/medicos/1/status' && options?.method === 'PATCH') {
          return mockMedicoInativado;
        }
        if (endpoint.startsWith('/medicos')) return [mockMedico];
        if (endpoint.startsWith('/especialidades'))
          return [{ id: 1, nome: 'Cardiologia', ativo: true }];
        return [];
      }
    );

    render(<MedicosPage />);

    const tabela = await screen.findByRole('table');
    expect(within(tabela).getByText('Dr. Teste')).toBeInTheDocument();

    const botaoInativar = screen.getByRole('button', { name: /inativar/i });
    await userEvent.click(botaoInativar);

    await vi.waitFor(() => {
      expect(apiModule.api).toHaveBeenCalledWith('/medicos/1/status', { method: 'PATCH' });
    });

    expect(notifications.show).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Médico inativado com sucesso!',
        color: 'teal',
      })
    );
  });
});
