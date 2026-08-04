/**
 * Validadores de formulario reutilizados entre os cadastros (paciente, medico,
 * especialidade, perfil). Validacao de formato apenas - a regra de negocio (RN01,
 * RN02) e sempre revalidada pelo backend.
 */

const REGEX_EMAIL = /^\S+@\S+\.\S+$/;

export function validarTextoMinimo(valor: string, minimo: number, mensagem: string): string | null {
    return valor.trim().length < minimo ? mensagem : null;
}

export function validarNomeCompleto(valor: string, mensagem = 'Informe o nome completo'): string | null {
    return validarTextoMinimo(valor, 3, mensagem);
}

export function validarTelefone(valor: string): string | null {
    return validarTextoMinimo(valor, 10, 'Informe um telefone válido');
}

export function validarEmailObrigatorio(valor: string): string | null {
    return REGEX_EMAIL.test(valor) ? null : 'E-mail inválido'; // RN08
}

export function validarEmailOpcional(valor: string): string | null {
    return !valor || REGEX_EMAIL.test(valor) ? null : 'E-mail inválido'; // RN08
}
