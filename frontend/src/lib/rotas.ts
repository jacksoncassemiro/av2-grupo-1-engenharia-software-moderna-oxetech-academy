/**
 * Home de cada perfil — fonte unica de verdade.
 *
 * Modulo sem React de proposito: e importado tanto pelo `proxy.ts` (Edge, no
 * servidor) quanto pelo `AuthGuard` e pelas telas de login/primeiro acesso.
 * Enquanto cada um mantinha a sua copia, o login mandava o atendente para uma
 * rota e o guard o redirecionava para outra em seguida.
 */

import type { TipoUsuario } from '@/types/dominio';

export const HOME_POR_PERFIL: Record<TipoUsuario, string> = {
  PACIENTE: '/consultas',
  ATENDENTE: '/gerenciar-consultas',
};
