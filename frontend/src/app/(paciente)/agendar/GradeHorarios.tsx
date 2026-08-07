'use client';

import { Chip, SimpleGrid, Skeleton, Text } from '@mantine/core';

import type { HorarioDisponivel } from '@/types/dominio';

import { formatarHorario } from './formatacao';

const QUANTIDADE_ESQUELETOS = 6;

interface GradeHorariosProps {
  horarios: HorarioDisponivel[];
  horarioEscolhidoId: number | null;
  carregando: boolean;
  aoEscolher: (horarioId: number) => void;
}

/**
 * US-07 — grade dos horarios livres de um medico numa data.
 *
 * Componente de apresentacao apenas: quem decide o que esta livre e o backend
 * (RN03), dentro do expediente (RN09) e no fuso America/Maceio (RN15). A tela nao
 * recalcula nada — desenha exatamente a lista que a API devolveu.
 */
export function GradeHorarios({
  horarios,
  horarioEscolhidoId,
  carregando,
  aoEscolher,
}: GradeHorariosProps) {
  if (carregando) {
    return (
      <SimpleGrid cols={{ base: 3, xs: 4, sm: 6 }} spacing="xs">
        {Array.from({ length: QUANTIDADE_ESQUELETOS }, (_, indice) => (
          <Skeleton key={indice} height={32} radius="xl" />
        ))}
      </SimpleGrid>
    );
  }

  // CA3 — medico sem agenda na data vira estado vazio com mensagem clara, nao erro.
  if (horarios.length === 0) {
    return (
      <Text c="dimmed" size="sm">
        Nenhum horário livre nesta data. Escolha outra data ou outro médico.
      </Text>
    );
  }

  return (
    <SimpleGrid cols={{ base: 3, xs: 4, sm: 6 }} spacing="xs">
      {horarios.map((slot) => (
        <Chip
          key={slot.id}
          checked={horarioEscolhidoId === slot.id}
          onChange={() => aoEscolher(slot.id)}
          variant="outline"
        >
          {formatarHorario(slot.horario)}
        </Chip>
      ))}
    </SimpleGrid>
  );
}
