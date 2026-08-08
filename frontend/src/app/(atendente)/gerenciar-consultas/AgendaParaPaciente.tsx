// src\app\(atendente)\gerenciar-consultas\AgendaParaPaciente.tsx
'use client';

import { useEffect, useState } from 'react';

import {
  Button,
  Card,
  Chip,
  Group,
  Select,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
} from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { notifications } from '@mantine/notifications';
import { Search } from 'lucide-react';

import { api, ApiError } from '@/lib/api';
import { apenasDigitos, cpfEhValido, formatarCpf } from '@/lib/cpf';
import dayjs from '@/lib/dayjs';
import type { Consulta, HorarioDisponivel, Medico, Paciente } from '@/types/dominio';

interface AgendarParaPacienteProps {
  onAgendado: () => void;
}

export function AgendarParaPaciente({ onAgendado }: AgendarParaPacienteProps) {
  const [cpfBusca, setCpfBusca] = useState('');
  const [pacienteEncontrado, setPacienteEncontrado] = useState<Paciente | null>(null);
  const [buscandoPaciente, setBuscandoPaciente] = useState(false);
  const [medicos, setMedicos] = useState<Medico[]>([]);
  const [medicoId, setMedicoId] = useState<string | null>(null);
  const [data, setData] = useState<Date | null>(null);
  const [horariosLivres, setHorariosLivres] = useState<HorarioDisponivel[]>([]);
  const [horarioEscolhido, setHorarioEscolhido] = useState<number | null>(null);
  const [agendando, setAgendando] = useState(false);

  useEffect(() => {
    // RN16 + RN17 - a lista vinha sem filtro nenhum e oferecia medico inativo ao
    // atendente; o POST respondia 409 so depois de escolher paciente, medico e slot.
    api<Medico[]>('/medicos?apenas_agendaveis=true')
      .then(setMedicos)
      .catch((erro) =>
        notifications.show({
          message: erro instanceof ApiError ? erro.message : 'Não foi possível carregar os médicos',
          color: 'red',
        })
      );
  }, []);

  async function buscarPaciente() {
    if (!cpfEhValido(cpfBusca)) {
      notifications.show({ message: 'CPF inválido', color: 'red' });
      return;
    }
    setBuscandoPaciente(true);
    setPacienteEncontrado(null);
    try {
      const paciente = await api<Paciente>(`/pacientes/buscar-por-cpf/${apenasDigitos(cpfBusca)}`);
      setPacienteEncontrado(paciente);
    } catch (erro) {
      notifications.show({
        title: 'Paciente não encontrado',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    } finally {
      setBuscandoPaciente(false);
    }
  }

  useEffect(() => {
    if (!medicoId || !data) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setHorariosLivres([]);
      return;
    }
    setHorarioEscolhido(null);

    const dataFormatada = dayjs(data).format('YYYY-MM-DD');

    api<HorarioDisponivel[]>(`/medicos/${medicoId}/horarios-livres?data=${dataFormatada}`)
      .then(setHorariosLivres)
      .catch((erro) => {
        // Sem limpar a lista, os horarios do medico/data anteriores continuariam
        // na tela e o atendente agendaria em um slot que nao e o exibido.
        setHorariosLivres([]);
        notifications.show({
          message:
            erro instanceof ApiError ? erro.message : 'Não foi possível carregar os horários',
          color: 'red',
        });
      });
  }, [medicoId, data]);

  async function agendarParaPaciente() {
    if (!pacienteEncontrado || !horarioEscolhido) return;
    setAgendando(true);
    try {
      await api<Consulta>('/atendente/consultas', {
        method: 'POST',
        body: { paciente_id: pacienteEncontrado.id, horario_disponivel_id: horarioEscolhido },
      });
      notifications.show({
        message: `Consulta agendada para ${pacienteEncontrado.nome}`,
        color: 'teal',
      });
      setCpfBusca('');
      setPacienteEncontrado(null);
      setMedicoId(null);
      setData(null);
      setHorariosLivres([]);
      setHorarioEscolhido(null);
      onAgendado();
    } catch (erro) {
      // CA2 (RN03/RN05, conflito de horario) chega aqui como 409.
      notifications.show({
        title: 'Não foi possível agendar',
        message: erro instanceof ApiError ? erro.message : 'Falha inesperada',
        color: 'red',
      });
    } finally {
      setAgendando(false);
    }
  }

  const opcoesMedico = medicos.map((m) => ({ value: String(m.id), label: m.nome }));

  return (
    <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
      <Text fw={600} mb="md">
        Agendar para paciente
      </Text>
      <Stack gap="md">
        <Group align="flex-end" gap="sm" wrap="wrap">
          <TextInput
            label="CPF do paciente"
            placeholder="000.000.000-00"
            value={cpfBusca}
            onChange={(evento) => setCpfBusca(formatarCpf(evento.currentTarget.value))}
            w={{ base: '100%', xs: 220 }}
          />
          <Button
            variant="light"
            leftSection={<Search size={16} />}
            loading={buscandoPaciente}
            onClick={buscarPaciente}
          >
            Buscar
          </Button>
        </Group>

        {pacienteEncontrado && (
          <>
            <Text size="sm">
              Paciente:{' '}
              <Text component="span" fw={600}>
                {pacienteEncontrado.nome}
              </Text>
            </Text>
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
                minDate={new Date()}
                value={data}
                onChange={(valor) => {
                  if (!valor) {
                    setData(null);
                    return;
                  }
                  const dataConvertida = dayjs(valor).toDate();
                  setData(isNaN(dataConvertida.getTime()) ? null : dataConvertida);
                }}
                withAsterisk
              />
            </Group>

            {medicoId && data && (
              <>
                <Text size="sm" fw={600}>
                  Horários livres
                </Text>
                {horariosLivres.length === 0 && (
                  <Text c="dimmed" size="sm">
                    Nenhum horário livre nesta data.
                  </Text>
                )}
                <SimpleGrid cols={{ base: 3, xs: 4, sm: 6 }} spacing="xs">
                  {horariosLivres.map((slot) => (
                    <Chip
                      key={slot.id}
                      checked={horarioEscolhido === slot.id}
                      onChange={() => setHorarioEscolhido(slot.id)}
                      variant="outline"
                    >
                      {slot.horario.slice(0, 5)}
                    </Chip>
                  ))}
                </SimpleGrid>
              </>
            )}

            <Group justify="flex-end">
              <Button
                onClick={agendarParaPaciente}
                disabled={!horarioEscolhido}
                loading={agendando}
              >
                Agendar consulta
              </Button>
            </Group>
          </>
        )}
      </Stack>
    </Card>
  );
}
