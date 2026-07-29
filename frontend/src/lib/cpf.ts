/** Validacao e formatacao de CPF no cliente (RN07). Espelha a regra do backend. */

export function apenasDigitos(valor: string): string {
  return valor.replace(/\D/g, '');
}

export function formatarCpf(valor: string): string {
  const cpf = apenasDigitos(valor).slice(0, 11);
  return cpf
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
}

export function cpfEhValido(valor: string): boolean {
  const cpf = apenasDigitos(valor);
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;

  for (const tamanho of [9, 10]) {
    let soma = 0;
    for (let i = 0; i < tamanho; i += 1) {
      soma += Number(cpf[i]) * (tamanho + 1 - i);
    }
    const digito = ((soma * 10) % 11) % 10;
    if (digito !== Number(cpf[tamanho])) return false;
  }
  return true;
}

/** O campo de login aceita CPF ou e-mail (US-00). */
export function pareceEmail(valor: string): boolean {
  return valor.includes('@');
}
