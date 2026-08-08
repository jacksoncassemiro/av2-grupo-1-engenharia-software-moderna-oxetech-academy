import { beforeEach, describe, expect, it, vi } from 'vitest';

import { render, screen, userEvent } from '@test-utils';

import { PrimeiroAcesso } from '@/components/primeiro-acesso/PrimeiroAcesso';
import { api, guardarTipoUsuario, guardarToken } from '@/lib/api';

// `ApiError` precisa continuar sendo a classe real: o componente usa `instanceof`.
vi.mock('@/lib/api', async (importarOriginal) => {
  const original = await importarOriginal<typeof import('@/lib/api')>();
  return {
    ...original,
    api: vi.fn(),
    guardarToken: vi.fn(),
    guardarTipoUsuario: vi.fn(),
  };
});

const substituirRota = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: substituirRota, push: vi.fn(), refresh: vi.fn() }),
}));

const apiMock = vi.mocked(api);
const CPF_VALIDO = '529.982.247-25';

async function verificarCpf(cpf = CPF_VALIDO) {
  await userEvent.type(screen.getByLabelText(/CPF/i), cpf);
  await userEvent.click(screen.getByRole('button', { name: /verificar/i }));
}

describe('PrimeiroAcesso (US-00)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('RN07 - CPF invalido nao chega a chamar a API', async () => {
    render(<PrimeiroAcesso />);
    await verificarCpf('111.111.111-11');

    expect(await screen.findByText('CPF inválido')).toBeInTheDocument();
    expect(apiMock).not.toHaveBeenCalled();
  });

  it('CA4 - cadastro sem login pede so a senha, com a mensagem do criterio', async () => {
    apiMock.mockResolvedValueOnce({
      cadastro_existe: true,
      login_ativo: false,
      nome: 'Carlos Silva',
    });
    render(<PrimeiroAcesso />);
    await verificarCpf();

    expect(
      await screen.findByText(
        'Encontramos seu cadastro, Carlos! Crie uma senha para ativar seu login.'
      )
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /ativar meu acesso/i })).toBeInTheDocument();
    // O paciente ja existe: nao se pede nome nem telefone de novo.
    expect(screen.queryByLabelText(/telefone/i)).not.toBeInTheDocument();
  });

  it('CA4 - manda o CPF sem mascara e sem os campos de auto-cadastro', async () => {
    apiMock
      .mockResolvedValueOnce({ cadastro_existe: true, login_ativo: false, nome: 'Carlos Silva' })
      .mockResolvedValueOnce({
        access_token: 'token-de-teste',
        token_type: 'bearer',
        tipo_usuario: 'PACIENTE',
      });
    render(<PrimeiroAcesso />);
    await verificarCpf();

    await userEvent.type(await screen.findByLabelText(/criar senha/i), 'senha123');
    await userEvent.type(screen.getByLabelText(/confirmar senha/i), 'senha123');
    await userEvent.click(screen.getByRole('button', { name: /ativar meu acesso/i }));

    expect(apiMock).toHaveBeenLastCalledWith('/auth/vincular-ou-criar', {
      method: 'POST',
      body: { cpf: '52998224725', senha: 'senha123' },
    });
    expect(substituirRota).toHaveBeenCalledWith('/consultas');
  });

  it('CA5 - CPF sem cadastro abre o formulario completo', async () => {
    apiMock.mockResolvedValueOnce({ cadastro_existe: false, login_ativo: false, nome: null });
    render(<PrimeiroAcesso />);
    await verificarCpf();

    expect(await screen.findByText('CPF não encontrado')).toBeInTheDocument();
    expect(screen.getByLabelText(/nome completo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/telefone/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /criar minha conta/i })).toBeInTheDocument();
  });

  it('CA5 - e-mail em branco e omitido do corpo, para nao quebrar o EmailStr', async () => {
    apiMock
      .mockResolvedValueOnce({ cadastro_existe: false, login_ativo: false, nome: null })
      .mockResolvedValueOnce({
        access_token: 'token-de-teste',
        token_type: 'bearer',
        tipo_usuario: 'PACIENTE',
      });
    render(<PrimeiroAcesso />);
    await verificarCpf();

    await userEvent.type(await screen.findByLabelText(/nome completo/i), 'Maria das Dores');
    await userEvent.type(screen.getByLabelText(/telefone/i), '(82) 99999-0000');
    await userEvent.type(screen.getByLabelText(/criar senha/i), 'senha123');
    await userEvent.type(screen.getByLabelText(/confirmar senha/i), 'senha123');
    await userEvent.click(screen.getByRole('button', { name: /criar minha conta/i }));

    expect(apiMock).toHaveBeenLastCalledWith('/auth/vincular-ou-criar', {
      method: 'POST',
      body: {
        cpf: '52998224725',
        nome: 'Maria das Dores',
        telefone: '(82) 99999-0000',
        senha: 'senha123',
      },
    });
  });

  it('CA5 - guarda o perfil junto com o token, senao o guard devolve para /login', async () => {
    // Regressao: o fluxo gravava so o token. Sem `clinica.tipoUsuario` (e sem o
    // cookie que o proxy.ts le), o AuthGuard nao reconhecia a sessao recem-criada
    // e mandava o paciente de volta para a tela de login logo apos o cadastro.
    apiMock
      .mockResolvedValueOnce({ cadastro_existe: false, login_ativo: false, nome: null })
      .mockResolvedValueOnce({
        access_token: 'token-de-teste',
        token_type: 'bearer',
        tipo_usuario: 'PACIENTE',
      });
    render(<PrimeiroAcesso />);
    await verificarCpf();

    await userEvent.type(await screen.findByLabelText(/nome completo/i), 'Maria das Dores');
    await userEvent.type(screen.getByLabelText(/telefone/i), '(82) 99999-0000');
    await userEvent.type(screen.getByLabelText(/criar senha/i), 'senha123');
    await userEvent.type(screen.getByLabelText(/confirmar senha/i), 'senha123');
    await userEvent.click(screen.getByRole('button', { name: /criar minha conta/i }));

    expect(vi.mocked(guardarToken)).toHaveBeenCalledWith('token-de-teste');
    expect(vi.mocked(guardarTipoUsuario)).toHaveBeenCalledWith('PACIENTE');
    expect(substituirRota).toHaveBeenCalledWith('/consultas');
  });

  it('CA5 - formata o telefone durante a digitacao no auto-cadastro', async () => {
    apiMock.mockResolvedValueOnce({ cadastro_existe: false, login_ativo: false, nome: null });
    render(<PrimeiroAcesso />);
    await verificarCpf();

    const campo = await screen.findByLabelText(/telefone/i);
    await userEvent.type(campo, '82999998888');

    expect(campo).toHaveValue('(82) 99999-8888');
  });

  it('CA5 - telefone com menos de 10 digitos nao chega a chamar a API', async () => {
    apiMock.mockResolvedValueOnce({ cadastro_existe: false, login_ativo: false, nome: null });
    render(<PrimeiroAcesso />);
    await verificarCpf();

    await userEvent.type(await screen.findByLabelText(/nome completo/i), 'Maria das Dores');
    await userEvent.type(screen.getByLabelText(/telefone/i), '829999');
    await userEvent.type(screen.getByLabelText(/criar senha/i), 'senha123');
    await userEvent.type(screen.getByLabelText(/confirmar senha/i), 'senha123');
    await userEvent.click(screen.getByRole('button', { name: /criar minha conta/i }));

    expect(await screen.findByText(/Informe DDD e número/i)).toBeInTheDocument();
    // A primeira chamada (verificar-cpf) aconteceu; a de cadastro nao.
    expect(apiMock).toHaveBeenCalledTimes(1);
  });

  it('CA6 - CPF com login ativo nao mostra formulario, e sim o caminho do login', async () => {
    apiMock.mockResolvedValueOnce({
      cadastro_existe: true,
      login_ativo: true,
      nome: 'Carlos Silva',
    });
    render(<PrimeiroAcesso />);
    await verificarCpf();

    expect(await screen.findByText('Este CPF já possui login ativo')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /ir para o login/i })).toHaveAttribute(
      'href',
      '/login'
    );
    expect(screen.queryByLabelText(/criar senha/i)).not.toBeInTheDocument();
  });
});
