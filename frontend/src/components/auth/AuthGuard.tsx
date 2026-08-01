'use client';

import type { ReactNode } from 'react';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { lerToken } from '@/lib/api';
import { lerTipoUsuario } from '@/lib/auth';
import type { TipoUsuario } from '@/types/dominio';

const DESTINOS_POR_PERFIL: Record<TipoUsuario, string> = {
    PACIENTE: '/consultas',
    ATENDENTE: '/agenda',
};

type AuthGuardProps = {
    perfil: TipoUsuario;
    children: ReactNode;
};

export function AuthGuard({ perfil, children }: AuthGuardProps) {
    const router = useRouter();

    useEffect(() => {
        const token = lerToken();
        const tipoUsuario = lerTipoUsuario();

        if (!token || !tipoUsuario) {
            router.replace('/login');
            return;
        }

        if (tipoUsuario !== perfil) {
            router.replace(DESTINOS_POR_PERFIL[tipoUsuario]);
        }
    }, [perfil, router]);

    return <>{children}</>;
}