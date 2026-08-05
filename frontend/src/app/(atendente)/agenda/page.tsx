'use client';

import { useEffect, useState } from 'react';

import { Badge, Button, Card, Group, Pill, Select, Stack, Text, Title } from '@mantine/core';
import { DateInput, TimeInput } from '@mantine/dates';
import { notifications } from '@mantine/notifications';
import { CalendarClock, Plus } from 'lucide-react';

import { api, ApiError } from '@/lib/api';
import dayjs from '@/lib/dayjs';
import type { HorarioDisponivel, Medico } from '@/types/dominio';

const HORA_ABERTURA = '08:00';
const HORA_FECHAMENTO = '18:00'; // RN09 - exclusivo (nao aceita 18:00)

export default function AgendaPage() {
  const [medicos, setMedicos] = useState<Medico[]>([]);
  const [medicoId, setMedicoId] = useState<string | null>(null);
  const [data, setData] = useState<string | null>(null);
  const [horarioParaAdicionar, setHorarioParaAdicionar] = useState('');
  const [horarios, setHorarios] = useState<string[]>([]);
  const [criados, setCriados] = useState<HorarioDisponivel[]>([]);
  const [enviando, setEnviando] = useState(false);

  // Calcula se o expediente de hoje ja encerrou para definir a data minima permitida
  const agora = dayjs();
  const horaAtual = agora.format('HH:mm');
  const expedienteEncerradoHoje = horaAtual >= HORA_FECHAMENTO;
  const minDate = expedienteEncerradoHoje ? agora.add(1, 'day').toDate() : agora.toDate();

  useEffect(() => {
    api<Medico[]>('/medicos')
      .then(setMedicos)
      .catch((erro) =>
        notifications.show({
          message: erro instanceof ApiError ? erro.message : 'Não foi possível carregar os médicos',
          color: 'red',
        })
      );
  }, []);

  const opcoesMedico = medicos.map((m) => ({ value: String(m.id), label: m.nome }));

  function adicionarHorario() {
    if (!horarioParaAdicionar) return;

    // Impede adicionar horarios passados caso a data selecionada seja o dia de hoje
    if (data && dayjs(data).isSame(agora, 'day') && horarioParaAdicionar <= horaAtual) {
      notifications.show({
        title: 'Horário ultrapassado',
        message: 'Não é possível adicionar um horário que já passou no dia de hoje.',
        color: 'red',
      });
      return;
    }

    if (horarioParaAdicionar < HORA_ABERTURA || horarioParaAdicionar >= HORA_FECHAMENTO) {
      notifications.show({
        title: 'Horário fora do expediente',
        message: `A agenda funciona das ${HORA_ABERTURA} às ${HORA_FECHAMENTO}`, // RN09
        color: 'red',
      });
      return;
    }

    if (horarios.includes(horarioParaAdicionar)) return;
    setHorarios((atual) => [...atual, horarioParaAdicionar].sort());
    setHorarioParaAdicionar('');
  }

  function removerHorario(horario: string) {
    setHorarios((atual) => atual.filter((h) => h !== horario));
  }

  async function gerarGrade() {
    if (!medicoId || !data || horarios.length === 0) {
      notifications.show({
        message: 'Selecione o médico, a data e ao menos um horário',
        color: 'red',
      });
      return;
    }
    setEnviando(true);
    try {
      const criadosAgora = await api<HorarioDisponivel[]>(`/medicos/${medicoId}/agenda`, {
        method: 'POST',
        body: { data, horarios },
      });
      setCriados((atual) => [...criadosAgora, ...atual]);
      setHorarios([]);
      notifications.show({
        message: `${criadosAgora.length} horário(s) criado(s) para ${data}`,
        color: 'teal',
      });
    } catch (erro) {
      notifications.show({
        title: 'Não foi possível gerar a grade',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Stack gap="lg">
      <Group gap="xs">
        <CalendarClock size={22} />
        <Title order={2} size="h3">
          Agenda de horários
        </Title>
      </Group>

      <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
        <Text fw={600} mb="md">
          Lançar horários disponíveis
        </Text>
        <Stack gap="md">
          <Group grow align="flex-start" wrap="wrap">
            <Select
              label="Médico"
              placeholder="Selecione"
              data={opcoesMedico}
              value={medicoId}
              onChange={setMedicoId}
              withAsterisk
            />
            <DateInput
              label="Data"
              placeholder="Selecione a data"
              valueFormat="DD/MM/YYYY"
              dateParser={(valor) => dayjs(valor, 'DD/MM/YYYY').format('YYYY-MM-DD')}
              minDate={minDate}
              value={data}
              onChange={setData}
              withAsterisk
            />
          </Group>

          <Group align="flex-end" gap="sm" wrap="wrap">
            <TimeInput
              label="Adicionar horário"
              description={`Expediente ${HORA_ABERTURA}–${HORA_FECHAMENTO} (RN09)`}
              value={horarioParaAdicionar}
              onChange={(evento) => setHorarioParaAdicionar(evento.currentTarget.value)}
              w={{ base: '100%', xs: 180 }}
            />
            <Button variant="light" leftSection={<Plus size={16} />} onClick={adicionarHorario}>
              Adicionar
            </Button>
          </Group>

          {horarios.length > 0 && (
            <Group gap="xs">
              {horarios.map((horario) => (
                <Pill key={horario} withRemoveButton onRemove={() => removerHorario(horario)}>
                  {horario}
                </Pill>
              ))}
            </Group>
          )}

          <Group justify="flex-end">
            <Button onClick={gerarGrade} loading={enviando}>
              Gerar grade
            </Button>
          </Group>
        </Stack>
      </Card>

      {criados.length > 0 && (
        <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
          <Text fw={600} mb="md">
            Horários criados nesta sessão
          </Text>
          <Group gap="xs">
            {criados.map((slot) => (
              <Badge key={slot.id} color="teal" variant="light">
                {slot.data} · {slot.horario}
              </Badge>
            ))}
          </Group>
        </Card>
      )}
    </Stack>
  );
}
