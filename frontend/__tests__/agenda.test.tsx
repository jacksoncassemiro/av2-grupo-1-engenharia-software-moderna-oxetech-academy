import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, userEvent, fireEvent } from '@test-utils';
import { notifications } from '@mantine/notifications';
import AgendaPage from '@/app/(atendente)/agenda/page';
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

describe('AgendaPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Fixa o relógio em 10/08/2026 às 10:00 para testes previsíveis
    vi.useFakeTimers({ toFake: ['Date'] });
    vi.setSystemTime(new Date(2026, 7, 10, 10, 0, 0));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('deve carregar a lista de médicos ao montar o componente', async () => {
    const mockMedicos = [
      { id: 1, nome: 'Dr. Silva', crm: '12345', especialidade_id: 1, ativo: true },
    ];
    vi.mocked(apiModule.api).mockResolvedValueOnce(mockMedicos);

    render(<AgendaPage />);

    expect(apiModule.api).toHaveBeenCalledWith('/medicos');
    expect(await screen.findByText('Lançar horários disponíveis')).toBeInTheDocument();
  });

  it('deve exibir notificação de erro quando a API falhar ao carregar os médicos', async () => {
    vi.mocked(apiModule.api).mockRejectedValueOnce(new Error('Erro de conexão'));

    render(<AgendaPage />);

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Não foi possível carregar os médicos',
          color: 'red',
        })
      );
    });
  });

  it('deve exibir notificação de aviso se tentar gerar grade sem preencher os campos obrigatórios', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Dr. Silva' }]);

    render(<AgendaPage />);

    const btnGerar = await screen.findByRole('button', { name: /gerar grade/i });
    await userEvent.click(btnGerar);

    expect(notifications.show).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Selecione o médico, a data e ao menos um horário',
        color: 'red',
      })
    );
  });

  it('deve recusar inclusão de horário fora do expediente comercial (RN09 / CA3)', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Dr. Silva' }]);

    render(<AgendaPage />);

    const timeInput = await screen.findByLabelText(/adicionar horário/i);
    const btnAdicionar = screen.getByRole('button', { name: /adicionar/i });

    // Testa horário antes das 08:00
    fireEvent.change(timeInput, { target: { value: '07:30' } });
    await userEvent.click(btnAdicionar);

    expect(notifications.show).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Horário fora do expediente',
        color: 'red',
      })
    );

    // Testa horário igual a 18:00 (limite exclusivo)
    fireEvent.change(timeInput, { target: { value: '18:00' } });
    await userEvent.click(btnAdicionar);

    expect(notifications.show).toHaveBeenLastCalledWith(
      expect.objectContaining({
        title: 'Horário fora do expediente',
        color: 'red',
      })
    );
  });

  it('deve recusar horário ultrapassado caso a data selecionada seja hoje', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Dr. Silva' }]);

    render(<AgendaPage />);

    const dateInput = await screen.findByLabelText(/data/i);
    const timeInput = screen.getByLabelText(/adicionar horário/i);
    const btnAdicionar = screen.getByRole('button', { name: /adicionar/i });

    // Preenche a data como hoje (10/08/2026)
    fireEvent.change(dateInput, { target: { value: '10/08/2026' } });

    // Tenta adicionar 09:00 (sendo que a hora mockada é 10:00)
    fireEvent.change(timeInput, { target: { value: '09:00' } });
    await userEvent.click(btnAdicionar);

    expect(notifications.show).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Horário ultrapassado',
        message: 'Não é possível adicionar um horário que já passou no dia de hoje.',
        color: 'red',
      })
    );
  });

  it('deve permitir adicionar e remover horários válidos da lista (Pill)', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Dr. Silva' }]);

    render(<AgendaPage />);

    const timeInput = await screen.findByLabelText(/adicionar horário/i);
    const btnAdicionar = screen.getByRole('button', { name: /adicionar/i });

    fireEvent.change(timeInput, { target: { value: '11:00' } });
    await userEvent.click(btnAdicionar);

    expect(screen.getByText('11:00')).toBeInTheDocument();

    // Localiza o elemento do Pill e o botão de remoção interno
    const pillLabel = screen.getByText('11:00');
    const pillRoot = pillLabel.closest('.mantine-Pill-root')!;
    const removePillBtn = pillRoot.querySelector('button')!;
    await userEvent.click(removePillBtn);

    expect(screen.queryByText('11:00')).not.toBeInTheDocument();
  });

  it('deve gerar a grade de horários com sucesso (CA1)', async () => {
    const mockMedicos = [{ id: 1, nome: 'Dr. Silva' }];
    const mockCriados = [
      { id: 101, medico_id: 1, data: '2026-08-11', horario: '11:00', disponivel: true },
    ];

    vi.mocked(apiModule.api).mockResolvedValueOnce(mockMedicos); // GET /medicos
    vi.mocked(apiModule.api).mockResolvedValueOnce(mockCriados); // POST /medicos/1/agenda

    render(<AgendaPage />);

    // Seleciona médico
    const selectMedico = await screen.findByPlaceholderText('Selecione');
    await userEvent.click(selectMedico);
    await userEvent.click(await screen.findByRole('option', { name: 'Dr. Silva' }));

    // Define data
    const dateInput = screen.getByLabelText(/data/i);
    fireEvent.change(dateInput, { target: { value: '11/08/2026' } });

    // Adiciona horário
    const timeInput = screen.getByLabelText(/adicionar horário/i);
    fireEvent.change(timeInput, { target: { value: '11:00' } });
    await userEvent.click(screen.getByRole('button', { name: /adicionar/i }));

    // Submete a grade
    await userEvent.click(screen.getByRole('button', { name: /gerar grade/i }));

    await vi.waitFor(() => {
      // O DateInput converte '11/08/2026' para '2026-08-11' no corpo da requisição
      expect(apiModule.api).toHaveBeenCalledWith('/medicos/1/agenda', {
        method: 'POST',
        body: { data: '2026-08-11', horarios: ['11:00'] },
      });
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          message: expect.stringMatching(/1 horário\(s\) criado\(s\)/),
          color: 'teal',
        })
      );
    });

    // Valida exibição da badge do horário criado
    expect(await screen.findByText(/11:00/i)).toBeInTheDocument();
  });

  it('deve exibir notificação de erro ao falhar na geração de grade (ApiError 409 / RN05)', async () => {
    vi.mocked(apiModule.api).mockResolvedValueOnce([{ id: 1, nome: 'Dr. Silva' }]);

    render(<AgendaPage />);

    // Preenche os campos minimos
    const selectMedico = await screen.findByPlaceholderText('Selecione');
    await userEvent.click(selectMedico);
    await userEvent.click(await screen.findByRole('option', { name: 'Dr. Silva' }));

    fireEvent.change(screen.getByLabelText(/data/i), { target: { value: '11/08/2026' } });
    fireEvent.change(screen.getByLabelText(/adicionar horário/i), { target: { value: '11:00' } });
    await userEvent.click(screen.getByRole('button', { name: /adicionar/i }));

    // Simula erro 409 de duplicidade da API
    const erro409 = new apiModule.ApiError('Horário já cadastrado para este médico', 409);
    vi.mocked(apiModule.api).mockRejectedValueOnce(erro409);

    await userEvent.click(screen.getByRole('button', { name: /gerar grade/i }));

    await vi.waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Não foi possível gerar a grade',
          message: 'Horário já cadastrado para este médico',
          color: 'red',
        })
      );
    });
  });
});
