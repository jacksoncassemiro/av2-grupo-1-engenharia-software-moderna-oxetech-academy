'use client';

import type { ReactNode } from 'react';

import { AuthGuard } from '@/components/auth/AuthGuard';

export default function PacienteLayout({ children }: { children: ReactNode }) {
  return <AuthGuard perfil="PACIENTE">{children}</AuthGuard>;
}
