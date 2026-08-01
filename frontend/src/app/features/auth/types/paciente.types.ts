export interface ConsultaPaciente {
    id: string;
    dataHorario: string;
    nomeMedico: string;
    especialidade: string;
    status: 'AGENDADA' | 'REALIZADA' | 'CANCELADA';
}

export interface PacientePerfil {
    cpf: string;
    telefone: string;
    dataNascimento: string;
}