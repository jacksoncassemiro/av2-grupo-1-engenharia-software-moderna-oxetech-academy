/**
 * Validadores de formulario reutilizados entre os cadastros (paciente, medico,
 * especialidade, perfil). Validacao de formato apenas - a regra de negocio (RN01,
 * RN02) e sempre revalidada pelo backend.
 */

const REGEX_EMAIL = /^\S+@\S+\.\S+$/;

export function validarTextoMinimo(valor: string, minimo: number, mensagem: string): string | null {
  return valor.trim().length < minimo ? mensagem : null;
}

export function validarNomeCompleto(
  valor: string,
  mensagem = 'Informe o nome completo'
): string | null {
  return validarTextoMinimo(valor, 3, mensagem);
}

/**
 * Telefone brasileiro com DDD: 10 digitos (fixo) ou 11 (celular).
 *
 * Conta digitos, nao caracteres: com a mascara, "(82) 9999-" tem 10 caracteres
 * mas so 6 digitos, e passava como valido.
 */
export function validarTelefone(valor: string): string | null {
  const digitos = valor.replace(/\D/g, '').length;
  return digitos === 10 || digitos === 11 ? null : 'Informe DDD e número, ex.: (82) 99999-0000';
}

export function validarEmailObrigatorio(valor: string): string | null {
  return REGEX_EMAIL.test(valor) ? null : 'E-mail inválido'; // RN08
}

export function validarEmailOpcional(valor: string): string | null {
  return !valor || REGEX_EMAIL.test(valor) ? null : 'E-mail inválido'; // RN08
}
