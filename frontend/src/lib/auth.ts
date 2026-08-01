import type { TipoUsuario } from '@/types/dominio';

const CHAVE_TIPO_USUARIO = 'clinica.tipo_usuario';

export function guardarTipoUsuario(tipoUsuario: TipoUsuario): void {
    sessionStorage.setItem(CHAVE_TIPO_USUARIO, tipoUsuario);
}

export function lerTipoUsuario(): TipoUsuario | null {
    if (typeof window === 'undefined') return null;
    return sessionStorage.getItem(CHAVE_TIPO_USUARIO) as TipoUsuario | null;
}

export function limparTipoUsuario(): void {
    sessionStorage.removeItem(CHAVE_TIPO_USUARIO);
}