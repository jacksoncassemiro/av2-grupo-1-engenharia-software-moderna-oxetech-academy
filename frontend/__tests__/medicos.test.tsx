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

// Mock do módulo de notificações do Mantine
vi.mock('@mantine/notifications', () => ({
  notifications: {
    show: vi.fn(),
  },
}));

describe('MedicosPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve exibir erro ao tentar cadastrar sem especialidade (CA1)', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([]); // medicos
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Cardiologia' }]); // especialidades

    render(<MedicosPage />);

    await screen.findByPlaceholderText('Selecione');

    await userEvent.click(screen.getByRole('button', { name: /cadastrar/i }));

    expect(await screen.findByText('Selecione uma especialidade')).toBeInTheDocument();
  });

  it('deve listar medicos corretamente (CA4)', async () => {
    const mockMedicos = [
      { id: 1, nome: 'Dr. Teste', crm: '12345', especialidade_id: 1, ativo: true },
    ];
    vi.mocked(apiModule.api).mockResolvedValueOnce(mockMedicos); // medicos
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Cardiologia' }]); // especialidades

    render(<MedicosPage />);

    expect(await screen.findByText('Dr. Teste')).toBeInTheDocument();

    const tabela = screen.getByRole('table');
    expect(within(tabela).getByText('Dr. Teste')).toBeInTheDocument();
    expect(within(tabela).getByText('12345')).toBeInTheDocument();
    expect(within(tabela).getByText('Cardiologia')).toBeInTheDocument();
  });

  it('deve exibir erros de validação nos campos quando enviados com dados inválidos', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([]); // medicos
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Cardiologia' }]); // especialidades

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
    vi.mocked(apiModule.api).mockRejectedValueOnce(new Error('Erro de conexão'));

    render(<MedicosPage />);

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Não foi possível carregar os médicos',
          color: 'red',
        })
      );
    });
  });

  it('deve exibir alerta informativo quando não houver especialidades cadastradas', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([]); // medicos
    vi.mocked(apiModule.api).mockResolvedValueOnce([]); // especialidades vazias

    render(<MedicosPage />);

    expect(
      await screen.findByText('Cadastre uma especialidade antes de cadastrar um médico.')
    ).toBeInTheDocument();
  });

  it('deve exibir notificação quando a API retornar 409 com conflito de e-mail', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([]);
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Cardiologia' }]);

    render(<MedicosPage />);

    await userEvent.type(await screen.findByLabelText(/nome/i), 'Dr. João Silva');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'joao@teste.com');
    await userEvent.type(screen.getByLabelText(/crm/i), '123456');

    const select = screen.getByPlaceholderText('Selecione');
    await userEvent.click(select);
    await userEvent.click(await screen.findByRole('option', { name: 'Cardiologia' }));

    const error409 = new apiModule.ApiError('Este e-mail já está cadastrado', 409);
    vi.mocked(apiModule.api).mockRejectedValueOnce(error409);

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
    vi.mocked(apiModule.api).mockResolvedValueOnce([]);
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Cardiologia' }]);

    render(<MedicosPage />);

    await userEvent.type(await screen.findByLabelText(/nome/i), 'Dr. João Silva');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'joao@teste.com');
    await userEvent.type(screen.getByLabelText(/crm/i), '123456');

    const select = screen.getByPlaceholderText('Selecione');
    await userEvent.click(select);
    await userEvent.click(await screen.findByRole('option', { name: 'Cardiologia' }));

    const error409 = new apiModule.ApiError('CRM já cadastrado no sistema', 409);
    vi.mocked(apiModule.api).mockRejectedValueOnce(error409);

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
    vi.mocked(apiModule.api).mockResolvedValueOnce([]);
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Cardiologia' }]);

    render(<MedicosPage />);

    await userEvent.type(await screen.findByLabelText(/nome/i), 'Dr. João Silva');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'joao@teste.com');
    await userEvent.type(screen.getByLabelText(/crm/i), '123456');

    const select = screen.getByPlaceholderText('Selecione');
    await userEvent.click(select);
    await userEvent.click(await screen.findByRole('option', { name: 'Cardiologia' }));

    const error500 = new apiModule.ApiError('Erro interno no servidor', 500);
    vi.mocked(apiModule.api).mockRejectedValueOnce(error500);

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
    vi.mocked(apiModule.api).mockResolvedValueOnce([]);
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Cardiologia' }]);

    render(<MedicosPage />);

    await userEvent.type(await screen.findByLabelText(/nome/i), 'Dr. João Silva');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'joao@teste.com');
    await userEvent.type(screen.getByLabelText(/crm/i), '123456');

    const select = screen.getByPlaceholderText('Selecione');
    await userEvent.click(select);
    await userEvent.click(await screen.findByRole('option', { name: 'Cardiologia' }));

    vi.mocked(apiModule.api).mockRejectedValueOnce(new Error('Network drop'));

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
});