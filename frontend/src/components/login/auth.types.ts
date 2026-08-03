import type { TokenResposta } from '@/types/dominio';

export interface LoginPayload {
  login: string;
  senha: string;
}

export type LoginResponse = TokenResposta;
