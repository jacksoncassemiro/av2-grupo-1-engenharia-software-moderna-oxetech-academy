import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MantineProvider } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { vi, describe, test, expect, beforeEach } from 'vitest';

import EspecialidadesPage from '@/app/(atendente)/especialidades/page';
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
  { id: 1, nome: 'Cardiologia', descricao: 'Atendimento do coração', ativo: true },
  { id: 2, nome: 'Pediatria', descricao: 'Atendimento infantil', ativo: false },
];

const renderComProvedor = () =>
  render(
    <MantineProvider>
      <EspecialidadesPage />
    </MantineProvider>
  );

describe('EspecialidadesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('carrega e exibe por padrão apenas as especialidades ativas', async () => {
    (api as ReturnType<typeof vi.fn>).mockResolvedValue([mockEspecialidades[0]]);

    renderComProvedor();

    expect(await screen.findByText('Cardiologia')).toBeInTheDocument();
    expect(screen.getByText('Atendimento do coração')).toBeInTheDocument();
    expect(screen.getByText('Ativa')).toBeInTheDocument();

    expect(api).toHaveBeenCalledWith('/especialidades?apenas_ativas=true');
  });

  test('altera o filtro de status e refaz a busca com o query param correto', async () => {
    const user = userEvent.setup();
    (api as ReturnType<typeof vi.fn>).mockImplementation((endpoint: string) => {
      if (endpoint === '/especialidades?apenas_ativas=true')
        return Promise.resolve([mockEspecialidades[0]]);
      if (endpoint === '/especialidades?apenas_ativas=false')
        return Promise.resolve([mockEspecialidades[1]]);
      return Promise.resolve([]);
    });

    renderComProvedor();
    await screen.findByText('Cardiologia');

    const select = screen.getByRole('combobox', { name: /filtrar por status/i });
    await user.click(select);

    const opcaoInativas = screen.getByRole('option', { name: 'Inativas', hidden: true });
    await user.click(opcaoInativas);

    await waitFor(() => {
      expect(api).toHaveBeenCalledWith('/especialidades?apenas_ativas=false');
    });
    expect(await screen.findByText('Pediatria')).toBeInTheDocument();
  });

  test('cadastra nova especialidade com sucesso', async () => {
    const user = userEvent.setup();
    const novaEspecialidade = { id: 3, nome: 'Dermatologia', descricao: 'Pele', ativo: true };

    (api as ReturnType<typeof vi.fn>).mockImplementation(
      (endpoint: string, options?: { method?: string; body?: unknown }) => {
        if (options?.method === 'POST') return Promise.resolve(novaEspecialidade);
        return Promise.resolve([mockEspecialidades[0]]);
      }
    );

    renderComProvedor();
    await screen.findByText('Cardiologia');

    await user.type(screen.getByLabelText(/nome/i), 'Dermatologia');
    await user.type(screen.getByLabelText(/descrição/i), 'Pele');
    await user.click(screen.getByRole('button', { name: /cadastrar/i }));

    await waitFor(() => {
      expect(api).toHaveBeenCalledWith('/especialidades', {
        method: 'POST',
        body: { nome: 'Dermatologia', descricao: 'Pele' },
      });
    });

    expect(notifications.show).toHaveBeenCalledWith({
      message: 'Especialidade cadastrada',
      color: 'teal',
    });
    expect(await screen.findByText('Dermatologia')).toBeInTheDocument();
  });

  test('exibe notificação de erro ao falhar o cadastro de duplicata (409)', async () => {
    const user = userEvent.setup();

    (api as ReturnType<typeof vi.fn>).mockImplementation(
      (endpoint: string, options?: { method?: string; body?: unknown }) => {
        if (options?.method === 'POST') {
          return Promise.reject(new ApiError('Especialidade já cadastrada', 409));
        }
        return Promise.resolve([mockEspecialidades[0]]);
      }
    );

    renderComProvedor();
    await screen.findByText('Cardiologia');

    await user.type(screen.getByLabelText(/nome/i), 'Cardiologia');
    await user.click(screen.getByRole('button', { name: /cadastrar/i }));

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith({
        title: 'Não foi possível cadastrar',
        message: 'Especialidade já cadastrada',
        color: 'red',
      });
    });
  });

  test('alterna o status da especialidade com sucesso via rota PATCH', async () => {
    const user = userEvent.setup();
    const especialidadeInativada = { ...mockEspecialidades[0], ativo: false };

    (api as ReturnType<typeof vi.fn>).mockImplementation(
      (endpoint: string, options?: { method?: string; body?: unknown }) => {
        if (endpoint === '/especialidades/1/status' && options?.method === 'PATCH') {
          return Promise.resolve(especialidadeInativada);
        }
        return Promise.resolve([mockEspecialidades[0]]);
      }
    );

    renderComProvedor();
    await screen.findByText('Cardiologia');

    const botaoInativar = screen.getByRole('button', { name: /inativar/i });
    await user.click(botaoInativar);

    await waitFor(() => {
      expect(api).toHaveBeenCalledWith('/especialidades/1/status', {
        method: 'PATCH',
      });
    });

    expect(notifications.show).toHaveBeenCalledWith({
      message: 'Especialidade inativada com sucesso!',
      color: 'teal',
    });
  });

  test('exibe mensagem quando nenhuma especialidade for encontrada', async () => {
    (api as ReturnType<typeof vi.fn>).mockResolvedValue([]);

    renderComProvedor();

    expect(await screen.findByText('Nenhuma especialidade encontrada.')).toBeInTheDocument();
  });

  test('exibe notificação de erro quando a chamada da API falha no carregamento', async () => {
    (api as ReturnType<typeof vi.fn>).mockRejectedValue(
      new ApiError('Erro ao carregar dados', 500)
    );

    renderComProvedor();

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith({
        message: 'Erro ao carregar dados',
        color: 'red',
      });
    });
  });
});
