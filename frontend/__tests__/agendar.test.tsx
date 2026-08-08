import { ModalsProvider } from '@mantine/modals';
import { notifications } from '@mantine/notifications';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import { render, screen, userEvent, waitFor } from '@test-utils';

import { FormularioAgendamento } from '@/app/(paciente)/agendar/FormularioAgendamento';
import { GradeHorarios } from '@/app/(paciente)/agendar/GradeHorarios';
import { api, ApiError } from '@/lib/api';
import dayjs from '@/lib/dayjs';

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
  notifications: { show: vi.fn() },
}));

const pushMock = vi.fn();

vi.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams('medico=10'),
  useRouter: () => ({ push: pushMock }),
}));

const HOJE = dayjs().format('YYYY-MM-DD');
const ROTA_MEDICOS = '/medicos?apenas_agendaveis=true';
const ROTA_HORARIOS_LIVRES = `/medicos/10/horarios-livres?data=${HOJE}`;

const medicos = [
  { id: 10, nome: 'Dr. Silva', email: 'silva@clinica.com', crm: '12345/AL', especialidade_id: 1 },
];

const slot14 = { id: 501, medico_id: 10, data: HOJE, horario: '14:00:00', disponivel: true };
const slot15 = { id: 502, medico_id: 10, data: HOJE, horario: '15:00:00', disponivel: true };

const consultaSolicitada = {
  id: 900,
  medico_nome: 'Dr. Silva',
  data: HOJE,
  horario: '15:00:00',
  status: 'SOLICITADA',
};

const apiMock = api as ReturnType<typeof vi.fn>;

/** Responde `/medicos` sempre e `horarios-livres` com a lista pedida em cada teste. */
function responderCom(horariosLivres: unknown[]) {
  apiMock.mockImplementation((caminho: string) => {
    if (caminho === ROTA_MEDICOS) return Promise.resolve(medicos);
    if (caminho === ROTA_HORARIOS_LIVRES) return Promise.resolve(horariosLivres);
    return Promise.resolve([]);
  });
}

function renderizarFormulario() {
  return render(
    <ModalsProvider>
      <FormularioAgendamento />
    </ModalsProvider>
  );
}

describe('GradeHorarios (US-07)', () => {
  test('CA3 — mostra estado vazio, e nao erro, quando nao ha agenda na data', () => {
    render(
      <GradeHorarios
        horarios={[]}
        horarioEscolhidoId={null}
        carregando={false}
        aoEscolher={vi.fn()}
      />
    );

    expect(
      screen.getByText('Nenhum horário livre nesta data. Escolha outra data ou outro médico.')
    ).toBeInTheDocument();
  });

  test('desenha um chip por horario livre, no formato HH:MM', () => {
    render(
      <GradeHorarios
        horarios={[slot14, slot15]}
        horarioEscolhidoId={null}
        carregando={false}
        aoEscolher={vi.fn()}
      />
    );

    expect(screen.getByText('14:00')).toBeInTheDocument();
    expect(screen.getByText('15:00')).toBeInTheDocument();
    expect(screen.queryByText('14:00:00')).not.toBeInTheDocument();
  });
});

describe('FormularioAgendamento (US-07 / US-08)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('US-07 CA1 (RN03) — exibe apenas os horarios que a API devolveu como livres', async () => {
    // O slot das 14:00 ja foi reservado, entao o backend so devolve as 15:00.
    responderCom([slot15]);

    renderizarFormulario();

    expect(await screen.findByText('15:00')).toBeInTheDocument();
    expect(screen.queryByText('14:00')).not.toBeInTheDocument();
    expect(api).toHaveBeenCalledWith(ROTA_HORARIOS_LIVRES);
  });

  test('US-07 CA3 — estado vazio quando o medico nao tem agenda na data', async () => {
    responderCom([]);

    renderizarFormulario();

    expect(
      await screen.findByText(
        'Nenhum horário livre nesta data. Escolha outra data ou outro médico.'
      )
    ).toBeInTheDocument();
  });

  test('US-08 CA1 (RN06) — confirmar no modal envia POST /consultas com o slot escolhido', async () => {
    const usuario = userEvent.setup();
    responderCom([slot15]);
    apiMock.mockImplementation((caminho: string, opcoes?: { method?: string }) => {
      if (caminho === ROTA_MEDICOS) return Promise.resolve(medicos);
      if (caminho === ROTA_HORARIOS_LIVRES) return Promise.resolve([slot15]);
      if (caminho === '/consultas' && opcoes?.method === 'POST') {
        return Promise.resolve(consultaSolicitada);
      }
      return Promise.resolve([]);
    });

    renderizarFormulario();
    await usuario.click(await screen.findByText('15:00'));
    await usuario.click(screen.getByRole('button', { name: 'Confirmar agendamento' }));

    // O modal e o passo de confirmacao exigido pela US-08.
    expect(await screen.findByText('Sim, agendar')).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: 'Sim, agendar' }));

    await waitFor(() => {
      expect(api).toHaveBeenCalledWith('/consultas', {
        method: 'POST',
        body: { horario_disponivel_id: 502 },
      });
    });

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Consulta com Dr. Silva solicitada',
          color: 'teal',
        })
      );
    });
  });

  test('US-08 → US-10 — sucesso leva o paciente para Minhas Consultas', async () => {
    const usuario = userEvent.setup();
    apiMock.mockImplementation((caminho: string, opcoes?: { method?: string }) => {
      if (caminho === ROTA_MEDICOS) return Promise.resolve(medicos);
      if (caminho === ROTA_HORARIOS_LIVRES) return Promise.resolve([slot15]);
      if (caminho === '/consultas' && opcoes?.method === 'POST') {
        return Promise.resolve(consultaSolicitada);
      }
      return Promise.resolve([]);
    });

    renderizarFormulario();
    await usuario.click(await screen.findByText('15:00'));
    await usuario.click(screen.getByRole('button', { name: 'Confirmar agendamento' }));
    await usuario.click(await screen.findByRole('button', { name: 'Sim, agendar' }));

    // A notificacao ja diz "aguarde a confirmacao em Minhas Consultas": a tela tem de
    // levar o paciente ate la, senao ele fica na grade sem ver o que acabou de pedir.
    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith('/consultas');
    });
  });

  test('US-08 CA2/CA3 — o erro mantem o paciente na grade, sem navegar', async () => {
    const usuario = userEvent.setup();
    apiMock.mockImplementation((caminho: string, opcoes?: { method?: string }) => {
      if (caminho === ROTA_MEDICOS) return Promise.resolve(medicos);
      if (caminho === ROTA_HORARIOS_LIVRES) return Promise.resolve([slot15]);
      if (caminho === '/consultas' && opcoes?.method === 'POST') {
        return Promise.reject(new ApiError('Horario indisponivel', 409));
      }
      return Promise.resolve([]);
    });

    renderizarFormulario();
    await usuario.click(await screen.findByText('15:00'));
    await usuario.click(screen.getByRole('button', { name: 'Confirmar agendamento' }));
    await usuario.click(await screen.findByRole('button', { name: 'Sim, agendar' }));

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Não foi possível agendar' })
      );
    });
    expect(pushMock).not.toHaveBeenCalled();
  });

  test('US-08 CA2/CA3 (RN03) — 409 do backend notifica e recarrega a grade', async () => {
    const usuario = userEvent.setup();
    apiMock.mockImplementation((caminho: string, opcoes?: { method?: string }) => {
      if (caminho === ROTA_MEDICOS) return Promise.resolve(medicos);
      if (caminho === ROTA_HORARIOS_LIVRES) return Promise.resolve([slot15]);
      if (caminho === '/consultas' && opcoes?.method === 'POST') {
        return Promise.reject(new ApiError('Horario indisponivel', 409));
      }
      return Promise.resolve([]);
    });

    renderizarFormulario();
    await usuario.click(await screen.findByText('15:00'));
    await usuario.click(screen.getByRole('button', { name: 'Confirmar agendamento' }));
    await usuario.click(await screen.findByRole('button', { name: 'Sim, agendar' }));

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith({
        title: 'Não foi possível agendar',
        message: 'Horario indisponivel',
        color: 'red',
      });
    });

    // CA4 — a grade sempre volta do backend, nunca e recalculada na tela.
    await waitFor(() => {
      const buscasDaGrade = apiMock.mock.calls.filter(
        (chamada) => chamada[0] === ROTA_HORARIOS_LIVRES
      );
      expect(buscasDaGrade.length).toBeGreaterThan(1);
    });
  });

  test('nao deixa confirmar enquanto nenhum horario estiver escolhido', async () => {
    responderCom([slot15]);

    renderizarFormulario();
    await screen.findByText('15:00');

    expect(screen.getByRole('button', { name: 'Confirmar agendamento' })).toBeDisabled();
  });
});
