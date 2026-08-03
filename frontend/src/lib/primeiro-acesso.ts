/**
 * Regras de apresentacao do primeiro acesso (US-00).
 *
 * Funcoes puras: sem React e sem HTTP, para serem testadas sem renderizar nada
 * (ADR-007). A decisao de negocio continua no backend — aqui so traduzimos a
 * resposta de `/auth/verificar-cpf` na etapa que a tela deve mostrar.
 */

import { apenasDigitos } from '@/lib/cpf';
import type { VerificarCpfResposta } from '@/types/dominio';

export type EtapaPrimeiroAcesso = 'cpf' | 'ativar-login' | 'auto-cadastro' | 'login-ja-ativo';

/** Minimo aceito pelo backend em `PrimeiroAcesso.senha` (Field(min_length=6)). */
const TAMANHO_MINIMO_SENHA = 6;

/** Telefone brasileiro com DDD: 10 digitos (fixo) ou 11 (celular). */
const DIGITOS_TELEFONE = [10, 11];

/**
 * CA5 - CPF sem cadastro segue para o auto-cadastro completo.
 * CA6 - CPF que ja tem login e mandado para a tela de login.
 * CA4 - cadastro existente sem login so precisa criar a senha.
 */
export function decidirEtapa(resposta: VerificarCpfResposta): EtapaPrimeiroAcesso {
  if (!resposta.cadastro_existe) return 'auto-cadastro';
  if (resposta.login_ativo) return 'login-ja-ativo';
  return 'ativar-login';
}

export function primeiroNome(nomeCompleto: string): string {
  return nomeCompleto.trim().split(/\s+/)[0] ?? '';
}

/** Texto exato exigido pelo CA4 da US-00. */
export function mensagemCadastroEncontrado(nomeCompleto: string): string {
  return `Encontramos seu cadastro, ${primeiroNome(nomeCompleto)}! Crie uma senha para ativar seu login.`;
}

export function validarSenha(valor: string): string | null {
  return valor.length < TAMANHO_MINIMO_SENHA
    ? `A senha precisa de no mínimo ${TAMANHO_MINIMO_SENHA} caracteres`
    : null;
}

export function validarConfirmacaoDeSenha(valor: string, senha: string): string | null {
  return valor === senha ? null : 'As senhas não conferem';
}

export function validarNome(valor: string): string | null {
  return valor.trim().length < 3 ? 'Informe o nome completo' : null;
}

export function validarTelefone(valor: string): string | null {
  return DIGITOS_TELEFONE.includes(apenasDigitos(valor).length)
    ? null
    : 'Informe DDD e número, ex.: (82) 99999-0000';
}

/** RN08 - e-mail e opcional no cadastro de paciente, mas se vier tem de ser valido. */
export function validarEmailOpcional(valor: string): string | null {
  if (valor.trim() === '') return null;
  return /^\S+@\S+\.\S+$/.test(valor.trim()) ? null : 'E-mail inválido';
}
