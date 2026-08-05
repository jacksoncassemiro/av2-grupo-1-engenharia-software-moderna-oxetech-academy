'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

import { AppShell, Burger, Group, NavLink, Title } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { Building2, CalendarDays, ClipboardList, LogOut, Search, UserRound } from 'lucide-react';

import { AuthGuard } from '@/components/auth/AuthGuard';
import { encerrarSessao } from '@/lib/api';

const ICON_SIZE = 18;

const ROTAS_PACIENTE = [
  { href: '/consultas', rotulo: 'Minhas Consultas', Icone: ClipboardList },
  { href: '/buscar-medicos', rotulo: 'Buscar Médicos', Icone: Search },
  { href: '/agendar', rotulo: 'Agendar Consulta', Icone: CalendarDays },
  { href: '/meus-dados', rotulo: 'Meus Dados', Icone: UserRound },
];

export default function LayoutPaciente({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [opened, { toggle, close }] = useDisclosure(false);

  function sair() {
    encerrarSessao();
    router.replace('/login');
  }

  return (
    <AuthGuard perfil="PACIENTE">
      <AppShell
        header={{ height: 60 }}
        navbar={{ width: 240, breakpoint: 'sm', collapsed: { mobile: !opened } }}
        padding="md"
      >
        <AppShell.Header>
          <Group h="100%" px="md" justify="space-between">
            <Group gap="sm">
              <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
              <Group gap={8}>
                <Building2 size={22} />
                <Title order={4}>Clínica Médica</Title>
              </Group>
            </Group>
            <NavLink
              label="Sair"
              onClick={sair}
              w="auto"
              c="red"
              leftSection={<LogOut size={16} />}
            />
          </Group>
        </AppShell.Header>

        <AppShell.Navbar p="md">
          {ROTAS_PACIENTE.map((rota) => (
            <NavLink
              key={rota.href}
              component={Link}
              href={rota.href}
              label={rota.rotulo}
              leftSection={<rota.Icone size={ICON_SIZE} />}
              active={pathname === rota.href || pathname.startsWith(rota.href + '/')}
              onClick={close}
            />
          ))}
        </AppShell.Navbar>

        <AppShell.Main>{children}</AppShell.Main>
      </AppShell>
    </AuthGuard>
  );
}
