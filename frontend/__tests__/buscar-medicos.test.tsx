import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MantineProvider } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { vi, describe, test, expect, beforeEach } from 'vitest';

import MedicosPage from '@/app/(paciente)/buscar-medicos/page';
import { api, ApiError } from '@/lib/api';

vi.mock('@/lib/api', () => ({
  api: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(
      public message: string,
      public status: number,
      public codigo?: string
    ) {
      super(message);
    }
  },
}));

vi.mock('@mantine/notifications', () => ({
  notifications: {
    show: vi.fn(),
  },
}));

const mockEspecialidades = [
  { id: 1, nome: 'Cardiologia' },
  { id: 2, nome: 'Dermatologia' },
];

const mockMedicos = [{ id: 10, nome: 'Dr. Carlos', crm: '12345/SP', especialidade_id: 1 }];

const renderComProvedor = () =>
  render(
    <MantineProvider>
      <MedicosPage />
    </MantineProvider>
  );

describe('MedicosPage (US-06)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('carrega e exibe a lista de médicos com os atributos do botão da US-06', async () => {
    (api as ReturnType<typeof vi.fn>).mockImplementation((endpoint: string) => {
      if (endpoint === '/especialidades?apenas_ativas=true')
        return Promise.resolve(mockEspecialidades);
      if (endpoint === '/medicos?apenas_agendaveis=true') return Promise.resolve(mockMedicos);
      return Promise.resolve([]);
    });

    renderComProvedor();

    expect(await screen.findByText('Dr. Carlos')).toBeInTheDocument();
    expect(screen.getByText('CRM 12345/SP')).toBeInTheDocument();
    expect(screen.getAllByText('Cardiologia')[0]).toBeInTheDocument();

    const linkAgendar = screen.getByRole('link', { name: /agendar/i });
    expect(linkAgendar).toBeInTheDocument();
    expect(linkAgendar).toHaveAttribute('href', '/agendar?medico=10');
  });

  test('RN16/RN17 — pede ao backend só quem pode receber consulta nova', async () => {
    // A tela não decide quem é agendável: ela pergunta. `apenas_ativos=true` filtrava
    // só o médico e deixava passar o médico ativo de especialidade inativada.
    (api as ReturnType<typeof vi.fn>).mockResolvedValue([]);

    renderComProvedor();

    await waitFor(() => {
      expect(api).toHaveBeenCalledWith('/medicos?apenas_agendaveis=true');
    });
    expect(api).not.toHaveBeenCalledWith(expect.stringContaining('apenas_ativos'));
  });

  test('refaz a busca na API ao selecionar uma especialidade no filtro', async () => {
    const user = userEvent.setup();
    (api as ReturnType<typeof vi.fn>).mockImplementation((endpoint: string) => {
      if (endpoint === '/especialidades?apenas_ativas=true')
        return Promise.resolve(mockEspecialidades);
      if (endpoint === '/medicos?apenas_agendaveis=true') return Promise.resolve(mockMedicos);
      if (endpoint === '/medicos?apenas_agendaveis=true&especialidade_id=1')
        return Promise.resolve(mockMedicos);
      return Promise.resolve([]);
    });

    renderComProvedor();
    await screen.findByText('Dr. Carlos');

    const select = screen.getByPlaceholderText('Todas as especialidades');
    await user.click(select);

    const opcaoCardiologia = screen.getByRole('option', { name: 'Cardiologia', hidden: true });
    await user.click(opcaoCardiologia);

    await waitFor(() => {
      expect(api).toHaveBeenCalledWith('/medicos?apenas_agendaveis=true&especialidade_id=1');
    });
  });

  test('exibe mensagem quando não houver médicos para o filtro selecionado', async () => {
    (api as ReturnType<typeof vi.fn>).mockImplementation((endpoint: string) => {
      if (endpoint === '/especialidades?apenas_ativas=true')
        return Promise.resolve(mockEspecialidades);
      if (endpoint === '/medicos?apenas_agendaveis=true') return Promise.resolve([]);
      return Promise.resolve([]);
    });

    renderComProvedor();

    expect(
      await screen.findByText('Nenhum médico disponível nesta especialidade.')
    ).toBeInTheDocument();
  });

  test('exibe notificação de erro quando a chamada da API falha', async () => {
    (api as ReturnType<typeof vi.fn>).mockImplementation((endpoint: string) => {
      if (endpoint === '/especialidades?apenas_ativas=true')
        return Promise.resolve(mockEspecialidades);
      if (endpoint.startsWith('/medicos')) {
        return Promise.reject(new ApiError('Erro ao conectar ao servidor', 500));
      }
      return Promise.resolve([]);
    });

    renderComProvedor();

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith({
        message: 'Erro ao conectar ao servidor',
        color: 'red',
      });
    });
  });

  test('recarrega todos os médicos ao limpar o filtro de especialidade', async () => {
    const user = userEvent.setup();

    (api as ReturnType<typeof vi.fn>).mockImplementation((endpoint: string) => {
      if (endpoint === '/especialidades?apenas_ativas=true')
        return Promise.resolve(mockEspecialidades);
      return Promise.resolve(mockMedicos);
    });

    renderComProvedor();
    await screen.findByText('Dr. Carlos');

    const select = screen.getByPlaceholderText('Todas as especialidades');
    await user.click(select);
    const opcao = screen.getByRole('option', { name: 'Cardiologia', hidden: true });
    await user.click(opcao);

    const botaoLimpar =
      document.querySelector('.mantine-Select-clear') ||
      screen.getByRole('button', { hidden: true });

    expect(botaoLimpar).toBeInTheDocument();
    await user.click(botaoLimpar);

    await waitFor(() => {
      expect(api).toHaveBeenLastCalledWith('/medicos?apenas_agendaveis=true');
    });
  });
});
