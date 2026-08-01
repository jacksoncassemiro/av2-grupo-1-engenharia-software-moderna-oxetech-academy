import { describe, expect, it } from 'vitest';

import {
  decidirEtapa,
  mensagemCadastroEncontrado,
  primeiroNome,
  validarConfirmacaoDeSenha,
  validarEmailOpcional,
  validarSenha,
  validarTelefone,
} from '@/lib/primeiro-acesso';

describe('decidirEtapa (US-00)', () => {
  it('CA4 - cadastro existente sem login vai para a ativacao', () => {
    expect(
      decidirEtapa({ cadastro_existe: true, login_ativo: false, nome: 'Carlos Silva' })
    ).toBe('ativar-login');
  });

  it('CA5 - CPF sem cadastro vai para o auto-cadastro', () => {
    expect(decidirEtapa({ cadastro_existe: false, login_ativo: false, nome: null })).toBe(
      'auto-cadastro'
    );
  });

  it('CA6 - CPF que ja tem login e mandado para a tela de login', () => {
    expect(
      decidirEtapa({ cadastro_existe: true, login_ativo: true, nome: 'Carlos Silva' })
    ).toBe('login-ja-ativo');
  });
});

describe('mensagemCadastroEncontrado (US-00 CA4)', () => {
  it('usa o primeiro nome, no texto exato do criterio de aceite', () => {
    expect(mensagemCadastroEncontrado('Carlos Silva')).toBe(
      'Encontramos seu cadastro, Carlos! Crie uma senha para ativar seu login.'
    );
  });

  it('tolera espacos extras no nome vindo do backend', () => {
    expect(primeiroNome('  Maria  das  Dores ')).toBe('Maria');
  });
});

describe('validacoes do formulario', () => {
  it('recusa senha com menos de 6 caracteres (limite do backend)', () => {
    expect(validarSenha('12345')).toBe('A senha precisa de no mínimo 6 caracteres');
    expect(validarSenha('123456')).toBeNull();
  });

  it('exige que a confirmacao seja igual a senha', () => {
    expect(validarConfirmacaoDeSenha('senha123', 'senha124')).toBe('As senhas não conferem');
    expect(validarConfirmacaoDeSenha('senha123', 'senha123')).toBeNull();
  });

  it('aceita telefone com 10 ou 11 digitos e recusa o resto', () => {
    expect(validarTelefone('(82) 99999-0000')).toBeNull();
    expect(validarTelefone('8233330000')).toBeNull();
    expect(validarTelefone('99999')).not.toBeNull();
  });

  it('RN08 - e-mail vazio passa, e-mail malformado nao', () => {
    expect(validarEmailOpcional('')).toBeNull();
    expect(validarEmailOpcional('   ')).toBeNull();
    expect(validarEmailOpcional('carlos@email.com')).toBeNull();
    expect(validarEmailOpcional('carlos@email')).toBe('E-mail inválido');
  });
});
