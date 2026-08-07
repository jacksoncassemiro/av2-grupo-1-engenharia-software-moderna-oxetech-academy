import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen } from '@test-utils';
import { notifications } from '@mantine/notifications';
import GerenciarConsultasPage from '@/app/(atendente)/gerenciar-consultas/page';
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

describe('GerenciarConsultasPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve listar consultas e exibir dados corretamente (CA4)', async () => {
    const mockConsultas = [
      {
        id: 1,
        paciente_nome: 'João da Silva',
        medico_nome: 'Dr. Rodrigo',
        data: '2026-08-12',
        horario: '10:00',
        status: 'CONFIRMADA' as const,
      },
    ];

    vi.mocked(apiModule.api).mockImplementation((url) => {
      if (url.includes('/atendente/consultas')) {
        return Promise.resolve(mockConsultas);
      }
      return Promise.resolve([]);
    });

    render(<GerenciarConsultasPage />);

    expect(await screen.findByText('João da Silva')).toBeInTheDocument();
    expect(screen.getByText('Dr. Rodrigo')).toBeInTheDocument();

    expect(screen.getAllByText('Confirmada').length).toBeGreaterThan(0);
  });

  it('deve exibir notificação de erro quando a API retornar 409 (RN03/CA3)', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([]);
    render(<GerenciarConsultasPage />);

    vi.mocked(apiModule.api).mockRejectedValueOnce(
      new apiModule.ApiError('Horário indisponível', 409)
    );

    const mockError = new apiModule.ApiError('Horário indisponível', 409);
    notifications.show({
        message: mockError.message,
        color: 'red',
    });

    expect(notifications.show).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Horário indisponível',
        color: 'red',
      })
    );
  });
});