'use client';

import { useRouter } from 'next/navigation';
import type { ReactNode } from 'react';
import { useEffect, useState } from 'react';

import { lerTipoUsuario, lerToken } from '@/lib/api';
import { HOME_POR_PERFIL } from '@/lib/rotas';
import type { TipoUsuario } from '@/types/dominio';

export { HOME_POR_PERFIL };

type AuthGuardProps = {
  /** Perfil que este layout serve. Usuários de outro perfil são redirecionados. */
  perfil: TipoUsuario;
  children: ReactNode;
};

/**
 * Guard de UX (RF18). A autorização real é do backend (RN12).
 *
 * Retorna `null` enquanto a sessão está sendo verificada no cliente para evitar
 * flash de conteúdo protegido antes do redirecionamento.
 */
export function AuthGuard({ perfil, children }: AuthGuardProps) {
  const router = useRouter();
  // null = ainda verificando | false = não autorizado | true = ok
  const [autorizado, setAutorizado] = useState<boolean | null>(null);

  useEffect(() => {
    const token = lerToken();
    const tipoUsuario = lerTipoUsuario();

    if (!token || !tipoUsuario) {
      router.replace('/login');
      return;
    }

    if (tipoUsuario !== perfil) {
      router.replace(HOME_POR_PERFIL[tipoUsuario as TipoUsuario] ?? '/login');
      return;
    }

    queueMicrotask(() => setAutorizado(true));
  }, [perfil, router]);

  if (!autorizado) return null;

  return <>{children}</>;
}
