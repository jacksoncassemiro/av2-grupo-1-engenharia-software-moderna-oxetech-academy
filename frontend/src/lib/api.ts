/**
 * Cliente HTTP unico do frontend.
 *
 * Clean Code: um lugar so para montar URL, injetar o token e traduzir erro da API
 * em Error com mensagem legivel. Nenhum componente chama `fetch` direto.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '/api';
const CHAVE_TOKEN = 'clinica.token';

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly codigo?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export function guardarToken(token: string): void {
  sessionStorage.setItem(CHAVE_TOKEN, token);
}

export function lerToken(): string | null {
  if (typeof window === 'undefined') return null;
  return sessionStorage.getItem(CHAVE_TOKEN);
}

export function limparToken(): void {
  sessionStorage.removeItem(CHAVE_TOKEN);
}

type Opcoes = Omit<RequestInit, 'body'> & { body?: unknown };

export async function api<T>(caminho: string, opcoes: Opcoes = {}): Promise<T> {
  const { body, headers, ...resto } = opcoes;
  const token = lerToken();

  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    ...resto,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });

  if (resposta.status === 204) return undefined as T;

  const conteudo = await resposta.json().catch(() => null);

  if (!resposta.ok) {
    throw new ApiError(
      extrairMensagem(conteudo) ?? `Falha na requisicao (${resposta.status})`,
      resposta.status,
      conteudo?.erro
    );
  }

  return conteudo as T;
}

function extrairMensagem(conteudo: unknown): string | null {
  if (conteudo === null || typeof conteudo !== 'object') return null;
  const detalhe = (conteudo as { detail?: unknown }).detail;
  if (typeof detalhe === 'string') return detalhe;
  // Erro de validacao do Pydantic vem como lista de objetos.
  if (Array.isArray(detalhe)) {
    return detalhe.map((item) => (item as { msg?: string }).msg).filter(Boolean).join('; ');
  }
  return null;
}
