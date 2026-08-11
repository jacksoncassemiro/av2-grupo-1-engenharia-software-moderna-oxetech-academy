import { notifications } from '@mantine/notifications';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { fireEvent, render, screen, userEvent, waitFor } from '@test-utils';

import { AgendarParaPaciente } from '@/app/(atendente)/gerenciar-consultas/AgendaParaPaciente';
import * as apiModule from '@/lib/api';
import dayjs from '@/lib/dayjs';

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof apiModule>('@/lib/api');
  return { ...actual, api: vi.fn() };
});

vi.mock('@mantine/notifications', () => ({
  notifications: { show: vi.fn() },
}));

const AMANHA = dayjs().add(1, 'day');
const DATA_ISO = AMANHA.format('YYYY-MM-DD');
const ROTA_HORARIOS = `/medicos/1/horarios-livres?data=${DATA_ISO}`;
const CPF_VALIDO = '529.982.247-25';

const paciente = { id: 7, nome: 'Maria Oliveira', cpf: CPF_VALIDO };
const slot14 = { id: 501, medico_id: 1, data: DATA_ISO, horario: '14:00:00', disponivel: true };

/** `delay: null` mantém o teste rápido: sao muitos eventos ate a grade aparecer. */
const usuario = userEvent.setup({ delay: null });

/** Preenche CPF, médico e data até a grade de horários aparecer. */
async function abrirGradeDeHorarios() {
  render(<AgendarParaPaciente onAgendado={vi.fn()} />);

  fireEvent.change(screen.getByLabelText(/CPF do paciente/i), { target: { value: CPF_VALIDO } });
  await usuario.click(screen.getByRole('button', { name: /buscar/i }));
  await screen.findByText('Maria Oliveira');

  await usuario.click(await screen.findByPlaceholderText('Selecione'));
  await usuario.click(await screen.findByRole('option', { name: 'Dr. Silva' }));
  fireEvent.change(screen.getByPlaceholderText('Selecione a data'), {
    target: { value: AMANHA.format('DD/MM/YYYY') },
  });

  await usuario.click(await screen.findByText('14:00'));
}

function buscasDaGrade() {
  return vi.mocked(apiModule.api).mock.calls.filter((chamada) => chamada[0] === ROTA_HORARIOS);
}

/** Responde os GETs da tela; o POST do agendamento fica a cargo de cada teste. */
function responderCom(agendamento: () => Promise<unknown>) {
  vi.mocked(apiModule.api).mockImplementation((url, opcoes) => {
    if (url.includes('/medicos?')) return Promise.resolve([{ id: 1, nome: 'Dr. Silva' }]);
    if (url.includes('/pacientes/buscar-por-cpf/')) return Promise.resolve(paciente);
    if (url === ROTA_HORARIOS) return Promise.resolve([slot14]);
    if (url === '/atendente/consultas' && opcoes?.method === 'POST') return agendamento();
    return Promise.resolve([]);
  });
}

describe('AgendarParaPaciente (US-09)', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('recarrega a grade quando o agendamento falha com 409 (RN03 — EXP-02 bug 3)', async () => {
    responderCom(() => Promise.reject(new apiModule.ApiError('Horario indisponivel', 409)));

    await abrirGradeDeHorarios();
    expect(buscasDaGrade()).toHaveLength(1);

    await usuario.click(screen.getByRole('button', { name: /agendar consulta/i }));

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Não foi possível agendar', color: 'red' })
      );
    });

    // O horário que outra sessão acabou de ocupar só some se a grade voltar do
    // backend: sem este refetch o chip continuava marcado e clicável após o erro.
    await waitFor(() => {
      expect(buscasDaGrade().length).toBeGreaterThan(1);
    });
  });
});
