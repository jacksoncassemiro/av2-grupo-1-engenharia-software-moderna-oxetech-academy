/**
 * Encerramento de sessao no cliente HTTP (CT12 / RN12 / RN13).
 *
 * O AuthGuard so verifica se token e tipo EXISTEM no sessionStorage, nunca se o
 * token continua valido — de proposito: quem decide isso e o backend (RN12), e
 * ler o `exp` do JWT na tela duplicaria regra de negocio no frontend. O que
 * faltava era a outra ponta: reagir ao 401 que o backend ja devolvia.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  api,
  ApiError,
  guardarTipoUsuario,
  guardarToken,
  lerTipoUsuario,
  lerToken,
} from '@/lib/api';

const CAMINHO_ATUAL = { pathname: '/consultas' };
const replaceMock = vi.fn();

function responder(status: number, corpo: unknown) {
  return Promise.resolve({
    status,
    ok: status >= 200 && status < 300,
    json: () => Promise.resolve(corpo),
  } as Response);
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn());
  // `window.location` e read-only no jsdom; redefinir e a forma suportada.
  Object.defineProperty(window, 'location', {
    configurable: true,
    value: {
      get pathname() {
        return CAMINHO_ATUAL.pathname;
      },
      replace: replaceMock,
    },
  });
  sessionStorage.clear();
  replaceMock.mockClear();
  CAMINHO_ATUAL.pathname = '/consultas';
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('api() — sessao invalida (CT12, RN13)', () => {
  it('desloga e volta para /login quando o token e recusado em rota protegida', async () => {
    guardarToken('token-corrompido');
    guardarTipoUsuario('PACIENTE');
    vi.mocked(fetch).mockReturnValue(responder(401, { detail: 'Nao autenticado' }));

    await expect(api('/consultas')).rejects.toBeInstanceOf(ApiError);

    expect(lerToken()).toBeNull();
    expect(lerTipoUsuario()).toBeNull();
    expect(document.cookie).not.toContain('clinica_perfil=PACIENTE');
    expect(replaceMock).toHaveBeenCalledWith('/login');
  });

  it('continua lancando ApiError, para o componente desligar o proprio spinner', async () => {
    guardarToken('token-corrompido');
    vi.mocked(fetch).mockReturnValue(responder(401, { detail: 'Nao autenticado' }));

    await expect(api('/pacientes/me')).rejects.toMatchObject({ status: 401 });
  });
});

describe('api() — 401 que NAO e de sessao (US-00 / CA7)', () => {
  it('nao desloga quando o login e recusado por credencial errada', async () => {
    CAMINHO_ATUAL.pathname = '/login';
    vi.mocked(fetch).mockReturnValue(responder(401, { detail: 'Login ou senha invalidos' }));

    // Deslogar aqui apagaria a mensagem que o usuario precisa ler.
    await expect(
      api('/auth/login', { method: 'POST', body: { login: 'x', senha: 'y' } })
    ).rejects.toMatchObject({ message: 'Login ou senha invalidos' });

    expect(replaceMock).not.toHaveBeenCalled();
  });

  it('nao redireciona a tela de login para ela mesma, mesmo com token velho guardado', async () => {
    // Cenario real: token expirado sobrou no sessionStorage e o `api()` o envia
    // junto no login. Sem a guarda de rota, isso viraria loop de redirecionamento.
    CAMINHO_ATUAL.pathname = '/login';
    guardarToken('token-velho');
    vi.mocked(fetch).mockReturnValue(responder(401, { detail: 'Login ou senha invalidos' }));

    await expect(api('/auth/login', { method: 'POST', body: {} })).rejects.toBeInstanceOf(ApiError);

    expect(replaceMock).not.toHaveBeenCalled();
  });

  it('nao mexe na sessao em erro que nao e 401', async () => {
    guardarToken('token-bom');
    guardarTipoUsuario('PACIENTE');
    vi.mocked(fetch).mockReturnValue(responder(409, { detail: 'Horario indisponivel' }));

    await expect(api('/consultas', { method: 'POST', body: {} })).rejects.toMatchObject({
      status: 409,
    });

    expect(lerToken()).toBe('token-bom');
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it('403 de perfil errado nao desloga: a sessao continua valida (RN12)', async () => {
    guardarToken('token-bom');
    guardarTipoUsuario('PACIENTE');
    vi.mocked(fetch).mockReturnValue(
      responder(403, { detail: 'Acesso restrito ao perfil ATENDENTE' })
    );

    await expect(api('/atendente/consultas')).rejects.toMatchObject({ status: 403 });

    expect(lerToken()).toBe('token-bom');
    expect(replaceMock).not.toHaveBeenCalled();
  });
});
