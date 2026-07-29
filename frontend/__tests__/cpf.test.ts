import { describe, expect, it } from 'vitest';

import { apenasDigitos, cpfEhValido, formatarCpf, pareceEmail } from '@/lib/cpf';

describe('validacao de CPF (RN07)', () => {
  it('aceita CPF valido com ou sem mascara', () => {
    expect(cpfEhValido('529.982.247-25')).toBe(true);
    expect(cpfEhValido('52998224725')).toBe(true);
  });

  it('rejeita digito verificador errado e digitos repetidos', () => {
    expect(cpfEhValido('52998224724')).toBe(false);
    expect(cpfEhValido('11111111111')).toBe(false);
    expect(cpfEhValido('123')).toBe(false);
  });

  it('formata progressivamente enquanto o usuario digita', () => {
    expect(formatarCpf('529')).toBe('529');
    expect(formatarCpf('529982')).toBe('529.982');
    expect(formatarCpf('52998224725')).toBe('529.982.247-25');
  });

  it('normaliza para apenas digitos', () => {
    expect(apenasDigitos('529.982.247-25')).toBe('52998224725');
  });
});

describe('campo unico de login (US-00)', () => {
  it('distingue e-mail de CPF', () => {
    expect(pareceEmail('recepcao@clinica.com')).toBe(true);
    expect(pareceEmail('52998224725')).toBe(false);
  });
});
