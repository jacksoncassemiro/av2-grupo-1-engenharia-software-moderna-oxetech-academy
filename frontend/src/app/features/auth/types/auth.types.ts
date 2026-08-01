export type TipoUsuario = 'PACIENTE' | 'ATENDENTE';

export interface LoginPayload {
  login: string;
  senha: string;
}

export interface LoginResponse {
  token: string;
  tipo_usuario: TipoUsuario;
}