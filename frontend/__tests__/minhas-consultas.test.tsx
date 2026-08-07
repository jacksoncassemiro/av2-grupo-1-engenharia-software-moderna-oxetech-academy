import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, userEvent, within } from '@test-utils';
import { notifications } from '@mantine/notifications';
import ConsultasPage from '@/app/(paciente)/consultas/page';
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

describe('ConsultasPage', () => {
  const consultaSolicitada = {
    id: 1,
    medico_nome: 'Dr. Teste',
    especialidade_nome: 'Cardiologia',
    data: '2026-08-10',
    horario: '14:00:00',
    status: 'SOLICITADA',
    pode_cancelar: true,
    motivo_cancelamento: null,
  };

  const consultaCancelada = {
    id: 2,
    medico_nome: 'Dra. Ana Souza',
    especialidade_nome: 'Dermatologia',
    data: '2026-08-05',
    horario: '09:30:00',
    status: 'CANCELADA',
    pode_cancelar: false,
    motivo_cancelamento: 'Imprevisto pessoal',
  };

  const consultaFinalizada = {
    id: 3,
    medico_nome: 'Dr. Carlos Lima',
    especialidade_nome: 'Ortopedia',
    data: '2026-07-01',
    horario: '11:00:00',
    status: 'FINALIZADA',
    pode_cancelar: false,
    motivo_cancelamento: null,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockApiPadrao = (consultas: unknown[] = []) => {
    vi.mocked(apiModule.api).mockImplementation(async (endpoint: string) => {
      if (endpoint.startsWith('/consultas')) return consultas;
      return [];
    });
  };

  it('deve exibir mensagem quando não houver consultas agendadas (estado vazio)', async () => {
    mockApiPadrao([]);

    render(<ConsultasPage />);

    expect(await screen.findByText('Você ainda não tem consultas agendadas.')).toBeInTheDocument();
    expect(
      screen.getByRole('link', { name: /agendar minha primeira consulta/i })
    ).toBeInTheDocument();
  });

  it('deve listar consultas corretamente (CA)', async () => {
    mockApiPadrao([consultaSolicitada]);

    render(<ConsultasPage />);

    const tabela = await screen.findByRole('table');
    expect(within(tabela).getByText('Dr. Teste')).toBeInTheDocument();
    expect(within(tabela).getByText('Cardiologia')).toBeInTheDocument();
    expect(within(tabela).getByText('10/08/2026')).toBeInTheDocument();
    expect(within(tabela).getByText('14:00')).toBeInTheDocument();
    expect(within(tabela).getByText('Solicitada')).toBeInTheDocument();
  });

  it('deve exibir o motivo do cancelamento quando a consulta estiver cancelada', async () => {
    mockApiPadrao([consultaCancelada]);

    render(<ConsultasPage />);

    const tabela = await screen.findByRole('table');
    expect(within(tabela).getByText('Cancelada')).toBeInTheDocument();
    expect(within(tabela).getByText('Imprevisto pessoal')).toBeInTheDocument();
  });

  it('não deve exibir o botão de cancelar quando pode_cancelar for falso', async () => {
    mockApiPadrao([consultaFinalizada]);

    render(<ConsultasPage />);

    const tabela = await screen.findByRole('table');
    expect(within(tabela).queryByRole('button', { name: /cancelar/i })).not.toBeInTheDocument();
    expect(within(tabela).getByText('—')).toBeInTheDocument();
  });

  it('deve exibir notificação de erro quando a API falhar ao carregar as consultas', async () => {
    vi.mocked(apiModule.api).mockRejectedValue(new Error('Erro de conexão'));

    render(<ConsultasPage />);

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Não foi possível carregar suas consultas',
          color: 'red',
        })
      );
    });
  });

  it('deve exibir a mensagem de erro vinda da ApiError quando o carregamento falhar', async () => {
    vi.mocked(apiModule.api).mockRejectedValue(new apiModule.ApiError('Sessão expirada', 401));

    render(<ConsultasPage />);

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Sessão expirada',
          color: 'red',
        })
      );
    });
  });

  it('deve abrir o modal de cancelamento com os dados da consulta selecionada', async () => {
    mockApiPadrao([consultaSolicitada]);

    render(<ConsultasPage />);

    await screen.findByRole('table');
    await userEvent.click(screen.getByRole('button', { name: /cancelar/i }));

    const modal = await screen.findByRole('dialog');
    expect(within(modal).getByText(/dr\. teste/i)).toBeInTheDocument();
    expect(within(modal).getByText(/10\/08\/2026/)).toBeInTheDocument();
    expect(within(modal).getByText(/14:00/)).toBeInTheDocument();
  });

  it('deve fechar o modal sem cancelar ao clicar em Voltar', async () => {
    mockApiPadrao([consultaSolicitada]);

    render(<ConsultasPage />);

    await screen.findByRole('table');
    await userEvent.click(screen.getByRole('button', { name: /cancelar/i }));

    await screen.findByRole('dialog');
    await userEvent.click(screen.getByRole('button', { name: /voltar/i }));

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(apiModule.api).not.toHaveBeenCalledWith(
      expect.stringContaining('/cancelar'),
      expect.anything()
    );
  });

  it('deve cancelar uma consulta com sucesso e recarregar a listagem', async () => {
    const consultaCanceladaApos = { ...consultaSolicitada, status: 'CANCELADA' };

    vi.mocked(apiModule.api).mockImplementation(
      async (endpoint: string, options?: { method?: string }) => {
        if (endpoint === '/consultas/1/cancelar' && options?.method === 'PATCH') {
          return consultaCanceladaApos;
        }
        if (endpoint.startsWith('/consultas')) return [consultaSolicitada];
        return [];
      }
    );

    render(<ConsultasPage />);

    await screen.findByRole('table');
    await userEvent.click(screen.getByRole('button', { name: /cancelar/i }));

    const modal = await screen.findByRole('dialog');
    await userEvent.type(within(modal).getByLabelText(/motivo/i), 'Imprevisto de última hora');
    await userEvent.click(within(modal).getByRole('button', { name: /confirmar cancelamento/i }));

    await vi.waitFor(() => {
      expect(apiModule.api).toHaveBeenCalledWith('/consultas/1/cancelar', {
        method: 'PATCH',
        body: { motivo: 'Imprevisto de última hora' },
      });
    });

    expect(notifications.show).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Consulta cancelada',
        color: 'teal',
      })
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('deve enviar motivo nulo quando o campo motivo for deixado em branco', async () => {
    vi.mocked(apiModule.api).mockImplementation(
      async (endpoint: string, options?: { method?: string }) => {
        if (endpoint === '/consultas/1/cancelar' && options?.method === 'PATCH') {
          return { ...consultaSolicitada, status: 'CANCELADA' };
        }
        if (endpoint.startsWith('/consultas')) return [consultaSolicitada];
        return [];
      }
    );

    render(<ConsultasPage />);

    await screen.findByRole('table');
    await userEvent.click(screen.getByRole('button', { name: /cancelar/i }));

    await screen.findByRole('dialog');
    await userEvent.click(screen.getByRole('button', { name: /confirmar cancelamento/i }));

    await vi.waitFor(() => {
      expect(apiModule.api).toHaveBeenCalledWith('/consultas/1/cancelar', {
        method: 'PATCH',
        body: { motivo: null },
      });
    });
  });

  it('deve exibir a mensagem de erro do backend quando o cancelamento violar a regra das 24h (CA1/RN04)', async () => {
    const erroRegraNegocio = new apiModule.ApiError(
      'Cancelamento não permitido: consultas só podem ser canceladas com mais de 24 horas de antecedência.',
      422
    );

    vi.mocked(apiModule.api).mockImplementation(
      async (endpoint: string, options?: { method?: string }) => {
        if (endpoint === '/consultas/1/cancelar' && options?.method === 'PATCH') {
          throw erroRegraNegocio;
        }
        if (endpoint.startsWith('/consultas')) return [consultaSolicitada];
        return [];
      }
    );

    render(<ConsultasPage />);

    await screen.findByRole('table');
    await userEvent.click(screen.getByRole('button', { name: /cancelar/i }));

    await screen.findByRole('dialog');
    await userEvent.click(screen.getByRole('button', { name: /confirmar cancelamento/i }));

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Não foi possível cancelar',
          message:
            'Cancelamento não permitido: consultas só podem ser canceladas com mais de 24 horas de antecedência.',
          color: 'red',
        })
      );
    });

    // Em caso de erro, o modal permanece aberto para o usuário tentar novamente
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('deve exibir "Falha inesperada" quando ocorrer um erro genérico ao cancelar', async () => {
    vi.mocked(apiModule.api).mockImplementation(
      async (endpoint: string, options?: { method?: string }) => {
        if (endpoint === '/consultas/1/cancelar' && options?.method === 'PATCH') {
          throw new Error('Network drop');
        }
        if (endpoint.startsWith('/consultas')) return [consultaSolicitada];
        return [];
      }
    );

    render(<ConsultasPage />);

    await screen.findByRole('table');
    await userEvent.click(screen.getByRole('button', { name: /cancelar/i }));

    await screen.findByRole('dialog');
    await userEvent.click(screen.getByRole('button', { name: /confirmar cancelamento/i }));

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Não foi possível cancelar',
          message: 'Falha inesperada',
          color: 'red',
        })
      );
    });
  });

  it('deve desabilitar o botão de confirmar durante o cancelamento (estado de loading)', async () => {
    let resolverPatch: (value: unknown) => void = () => {};
    const patchPromise = new Promise((resolve) => {
      resolverPatch = resolve;
    });

    vi.mocked(apiModule.api).mockImplementation(
      async (endpoint: string, options?: { method?: string }) => {
        if (endpoint === '/consultas/1/cancelar' && options?.method === 'PATCH') {
          return patchPromise;
        }
        if (endpoint.startsWith('/consultas')) return [consultaSolicitada];
        return [];
      }
    );

    render(<ConsultasPage />);

    await screen.findByRole('table');
    await userEvent.click(screen.getByRole('button', { name: /cancelar/i }));

    await screen.findByRole('dialog');
    const botaoConfirmar = screen.getByRole('button', { name: /confirmar cancelamento/i });
    await userEvent.click(botaoConfirmar);

    expect(botaoConfirmar).toHaveAttribute('data-loading', 'true');

    resolverPatch({ ...consultaSolicitada, status: 'CANCELADA' });

    await vi.waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });
});
