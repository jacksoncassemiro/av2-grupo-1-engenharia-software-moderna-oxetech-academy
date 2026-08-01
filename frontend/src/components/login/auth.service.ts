import { api, guardarToken } from '@/lib/api';
import { guardarTipoUsuario } from '@/lib/auth';
import { LoginPayload, LoginResponse } from './auth.types';

export async function realizarLogin(payload: LoginPayload): Promise<LoginResponse> {
    const resposta = await api<LoginResponse>('/auth/login', {
        method: 'POST',
        body: payload,
    });

    guardarToken(resposta.access_token);
    guardarTipoUsuario(resposta.tipo_usuario);
    return resposta;
}