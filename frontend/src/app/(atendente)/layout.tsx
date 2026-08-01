'use client';

import type { ReactNode } from 'react';

import { AuthGuard } from '@/components/auth/AuthGuard';

export default function AtendenteLayout({ children }: { children: ReactNode }) {
    return <AuthGuard perfil="ATENDENTE">{children}</AuthGuard>;
}