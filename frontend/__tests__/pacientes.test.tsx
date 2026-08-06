import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, userEvent, within } from '@test-utils';
import { notifications } from '@mantine/notifications';
import PacientesPage from '@/app/(atendente)/pacientes/page';
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

describe('PacientesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // --- CENÁRIOS DE ACERTO (SUCESSO) ---

  it('deve cadastrar paciente com sucesso e exibir na tabela da sessão', async () => {
    const mockPacienteCriado = {
      id: '1',
      nome: 'Maria Silva Santos',
      cpf: '52998224725',
      telefone: '(82) 99999-8888',
      email: 'maria@email.com',
      data_nascimento: '1990-10-10',
    };

    vi.mocked(apiModule.api).mockResolvedValueOnce(mockPacienteCriado);

    render(<PacientesPage />);

    await userEvent.type(screen.getByLabelText(/nome completo/i), 'Maria Silva Santos');
    await userEvent.type(screen.getByLabelText(/cpf/i), '52998224725');
    await userEvent.type(screen.getByLabelText(/telefone/i), '82999998888');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'maria@email.com');

    const dataInput = screen.getByPlaceholderText('Selecione a data');
    await userEvent.type(dataInput, '10/10/1990');

    await userEvent.click(screen.getByRole('button', { name: /cadastrar paciente/i }));

    await vi.waitFor(() => {
      expect(apiModule.api).toHaveBeenCalledWith('/pacientes', {
        method: 'POST',
        body: {
          nome: 'Maria Silva Santos',
          cpf: '529.982.247-25',
          telefone: '(82) 99999-8888',
          email: 'maria@email.com',
          data_nascimento: '1990-10-10',
        },
      });
    });

    expect(notifications.show).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Paciente cadastrado',
        color: 'teal',
      })
    );

    const tabela = await screen.findByRole('table');
    expect(within(tabela).getByText('Maria Silva Santos')).toBeInTheDocument();
    expect(within(tabela).getByText('529.982.247-25')).toBeInTheDocument();
  });

  it('deve formatar o CPF e Telefone automaticamente durante a digitação', async () => {
    render(<PacientesPage />);

    const campoCpf = screen.getByLabelText(/cpf/i);
    await userEvent.type(campoCpf, '52998224725');
    expect(campoCpf).toHaveValue('529.982.247-25');

    const campoTelefone = screen.getByLabelText(/telefone/i);
    await userEvent.type(campoTelefone, '82999998888');
    expect(campoTelefone).toHaveValue('(82) 99999-8888');
  });

  it('deve formatar telefone fixo corretamente (10 dígitos)', async () => {
    render(<PacientesPage />);

    const campoTelefone = screen.getByLabelText(/telefone/i);
    await userEvent.type(campoTelefone, '8233334444');
    expect(campoTelefone).toHaveValue('(82) 3333-4444');
  });

  it('deve permitir cadastro sem preencher campos opcionais (email e data de nascimento)', async () => {
    const mockPacienteSimples = {
      id: '2',
      nome: 'João Pedro Alves',
      cpf: '52998224725',
      telefone: '(82) 98888-7777',
      email: null,
      data_nascimento: null,
    };

    vi.mocked(apiModule.api).mockResolvedValueOnce(mockPacienteSimples);

    render(<PacientesPage />);

    await userEvent.type(screen.getByLabelText(/nome completo/i), 'João Pedro Alves');
    await userEvent.type(screen.getByLabelText(/cpf/i), '52998224725');
    await userEvent.type(screen.getByLabelText(/telefone/i), '82988887777');

    await userEvent.click(screen.getByRole('button', { name: /cadastrar paciente/i }));

    await vi.waitFor(() => {
      expect(apiModule.api).toHaveBeenCalledWith('/pacientes', {
        method: 'POST',
        body: {
          nome: 'João Pedro Alves',
          cpf: '529.982.247-25',
          telefone: '(82) 98888-7777',
          email: null,
          data_nascimento: null,
        },
      });
    });
  });

  // --- CENÁRIOS DE ERRO (FALHAS) ---

  it('deve exibir mensagens de validação ao submeter formulário inválido', async () => {
    render(<PacientesPage />);

    await userEvent.type(screen.getByLabelText(/nome completo/i), 'Ana');
    await userEvent.type(screen.getByLabelText(/cpf/i), '11111111111');
    await userEvent.type(screen.getByLabelText(/telefone/i), '123');
    await userEvent.type(screen.getByLabelText(/e-mail/i), 'email-invalido');

    await userEvent.click(screen.getByRole('button', { name: /cadastrar paciente/i }));

    expect(await screen.findByText('CPF inválido')).toBeInTheDocument();
    expect(screen.getByText('E-mail inválido')).toBeInTheDocument();
  });

  it('deve exibir notificação de erro quando a API retornar 409 (CPF já cadastrado)', async () => {
    const error409 = new apiModule.ApiError('CPF já cadastrado no sistema', 409);
    vi.mocked(apiModule.api).mockRejectedValueOnce(error409);

    render(<PacientesPage />);

    await userEvent.type(screen.getByLabelText(/nome completo/i), 'Carlos Eduardo');
    await userEvent.type(screen.getByLabelText(/cpf/i), '52998224725');
    await userEvent.type(screen.getByLabelText(/telefone/i), '82999998888');

    await userEvent.click(screen.getByRole('button', { name: /cadastrar paciente/i }));

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Não foi possível cadastrar',
          message: 'CPF já cadastrado no sistema',
          color: 'red',
        })
      );
    });
  });

  it('deve exibir "Falha inesperada" quando ocorrer erro genérico no envio', async () => {
    vi.mocked(apiModule.api).mockRejectedValueOnce(new Error('Network Error'));

    render(<PacientesPage />);

    await userEvent.type(screen.getByLabelText(/nome completo/i), 'Carlos Eduardo');
    await userEvent.type(screen.getByLabelText(/cpf/i), '52998224725');
    await userEvent.type(screen.getByLabelText(/telefone/i), '82999998888');

    await userEvent.click(screen.getByRole('button', { name: /cadastrar paciente/i }));

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Não foi possível cadastrar',
          message: 'Falha inesperada',
          color: 'red',
        })
      );
    });
  });
});
