/**
 * Formatacao dos campos de data e hora que chegam da API (US-07 / US-08).
 *
 * Clean Code: nome significativo e funcao pequena com responsabilidade unica, num
 * lugar so — a grade de horarios e o modal de confirmacao usam as duas.
 */
import dayjs from '@/lib/dayjs';

/** O backend serializa `time` como "HH:MM:SS"; a tela mostra "HH:MM". */
export function formatarHorario(horario: string): string {
  return horario.slice(0, 5);
}

/** O backend serializa `date` como "AAAA-MM-DD"; a tela mostra "DD/MM/AAAA". */
export function formatarData(data: string): string {
  return dayjs(data).format('DD/MM/YYYY');
}
