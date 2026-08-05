'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

import { AppShell, Burger, Group, NavLink, Text, Title } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { Building2, Calendar, ClipboardList, LogOut, Stethoscope, Tag, Users } from 'lucide-react';

import { AuthGuard } from '@/components/auth/AuthGuard';
import { encerrarSessao } from '@/lib/api';

const ICON_SIZE = 18;

const ROTA_GERAL = { href: '/gerenciar-consultas', rotulo: 'Consultas', Icone: ClipboardList };

const ROTAS_CADASTRO = [
  { href: '/especialidades', rotulo: 'Especialidades', Icone: Tag },
  { href: '/medicos', rotulo: 'Médicos', Icone: Stethoscope },
  { href: '/pacientes', rotulo: 'Pacientes', Icone: Users },
  { href: '/agenda', rotulo: 'Agenda', Icone: Calendar },
];

export default function LayoutAtendente({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [opened, { toggle, close }] = useDisclosure(false);

  function sair() {
    encerrarSessao();
    router.replace('/login');
  }

  return (
    <AuthGuard perfil="ATENDENTE">
      <AppShell
        header={{ height: 60 }}
        navbar={{ width: 260, breakpoint: 'sm', collapsed: { mobile: !opened } }}
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
          <Text size="xs" tt="uppercase" c="dimmed" fw={600} mb="xs">
            Geral
          </Text>
          <NavLink
            component={Link}
            href={ROTA_GERAL.href}
            label={ROTA_GERAL.rotulo}
            leftSection={<ROTA_GERAL.Icone size={ICON_SIZE} />}
            active={pathname === ROTA_GERAL.href}
            onClick={close}
          />
          <Text size="xs" tt="uppercase" c="dimmed" fw={600} mt="md" mb="xs">
            Cadastros
          </Text>
          {ROTAS_CADASTRO.map((rota) => (
            <NavLink
              key={rota.href}
              component={Link}
              href={rota.href}
              label={rota.rotulo}
              leftSection={<rota.Icone size={ICON_SIZE} />}
              active={pathname === rota.href}
              onClick={close}
            />
          ))}
        </AppShell.Navbar>

        <AppShell.Main>{children}</AppShell.Main>
      </AppShell>
    </AuthGuard>
  );
}
