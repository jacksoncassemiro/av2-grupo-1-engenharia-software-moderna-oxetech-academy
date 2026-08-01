import { api, guardarToken } from '@/lib/api';
import { LoginPayload, LoginResponse } from '../types/auth.types';

export async function realizarLogin(payload: LoginPayload): Promise<LoginResponse> {
    const resposta = await api<LoginResponse>('/auth/login', {
        method: 'POST',
        body: payload,
    });

    guardarToken(resposta.token);
    return resposta;
}