/** Tipos espelhando os schemas do backend. Fonte da verdade: /openapi.json */

export type TipoUsuario = 'PACIENTE' | 'ATENDENTE';

export type StatusConsulta = 'SOLICITADA' | 'CONFIRMADA' | 'CANCELADA' | 'FINALIZADA';

export interface TokenResposta {
  access_token: string;
  token_type: string;
  tipo_usuario: TipoUsuario;
}

export interface VerificarCpfResposta {
  cadastro_existe: boolean;
  login_ativo: boolean;
  nome: string | null;
}

/**
 * Espelha `PrimeiroAcesso` do backend (US-00). Um endpoint, dois caminhos (ADR-005):
 * `nome`, `telefone` e `email` só vão junto quando o CPF ainda não tem cadastro.
 */
export interface PrimeiroAcessoRequisicao {
  cpf: string;
  senha: string;
  nome?: string;
  telefone?: string;
  email?: string;
}

export interface Paciente {
  id: number;
  nome: string;
  cpf: string;
  email: string | null;
  telefone: string;
  data_nascimento: string | null;
  ativo: boolean;
}

export interface Especialidade {
  id: number;
  nome: string;
  descricao: string | null;
  ativo: boolean;
}

export interface Medico {
  id: number;
  nome: string;
  email: string;
  crm: string;
  especialidade_id: number;
  ativo: boolean;
}

export interface HorarioDisponivel {
  id: number;
  medico_id: number;
  data: string;
  horario: string;
  disponivel: boolean;
}

export interface Consulta {
  id: number;
  paciente_id: number;
  paciente_nome: string;
  medico_id: number;
  medico_nome: string;
  especialidade_nome: string;
  horario_disponivel_id: number;
  data: string;
  horario: string;
  status: StatusConsulta;
  data_agendamento: string;
  motivo_cancelamento: string | null;
  pode_cancelar: boolean;
}

