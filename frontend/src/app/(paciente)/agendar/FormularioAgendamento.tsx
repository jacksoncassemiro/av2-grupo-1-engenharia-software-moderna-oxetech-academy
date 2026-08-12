'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';

import { Button, Card, Group, Select, Stack, Text } from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';

import { api, ApiError } from '@/lib/api';
import dayjs from '@/lib/dayjs';
import type { Consulta, HorarioDisponivel, Medico } from '@/types/dominio';

import { formatarData, formatarHorario } from './formatacao';
import { GradeHorarios } from './GradeHorarios';

function mensagemDoErro(erro: unknown, padrao: string): string {
  return erro instanceof ApiError ? erro.message : padrao;
}

/**
 * US-07 (escolher horario livre) + US-08 (confirmar a solicitacao da consulta).
 *
 * Nenhuma regra de negocio vive aqui: a grade e o que `GET /medicos/{id}/horarios-livres`
 * devolveu (RN03/RN09/RN15) e o desfecho da reserva e o status que `POST /consultas`
 * respondeu (RN03/RN06). O componente so obedece a API.
 */
export function FormularioAgendamento() {
  const parametros = useSearchParams();
  const router = useRouter();
  // `?medico=` chega de "Buscar Médicos" (US-06); a data comeca em hoje para que a
  // grade ja apareca sem mais um clique.
  const medicoDaUrl = parametros.get('medico');
  const [hoje] = useState(() => dayjs().format('YYYY-MM-DD'));

  const [medicos, setMedicos] = useState<Medico[]>([]);
  const [medicoId, setMedicoId] = useState<string | null>(medicoDaUrl);
  const [data, setData] = useState<string | null>(hoje);
  const [horariosLivres, setHorariosLivres] = useState<HorarioDisponivel[]>([]);
  const [horarioEscolhidoId, setHorarioEscolhidoId] = useState<number | null>(null);
  const [carregandoHorarios, setCarregandoHorarios] = useState(Boolean(medicoDaUrl));
  const [versaoDaGrade, setVersaoDaGrade] = useState(0);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    // RN16 + RN17 - só médico ativo de especialidade ativa recebe consulta nova.
    api<Medico[]>('/medicos?apenas_agendaveis=true')
      .then(setMedicos)
      .catch((erro) =>
        notifications.show({
          message: mensagemDoErro(erro, 'Não foi possível carregar os médicos'),
          color: 'red',
        })
      );
  }, []);

  // US-07 — recarrega a grade a cada troca de medico/data e a cada `versaoDaGrade`
  // (usada depois de agendar: CA4 e a corrida da CA2 exigem grade fresca do backend).
  useEffect(() => {
    if (!medicoId || !data) return;
    let ativo = true;

    async function buscarHorariosLivres() {
      try {
        const livres = await api<HorarioDisponivel[]>(
          `/medicos/${medicoId}/horarios-livres?data=${data}`
        );
        if (ativo) setHorariosLivres(livres);
      } catch (erro) {
        if (!ativo) return;
        setHorariosLivres([]);
        notifications.show({
          message: mensagemDoErro(erro, 'Não foi possível carregar os horários'),
          color: 'red',
        });
      } finally {
        if (ativo) setCarregandoHorarios(false);
      }
    }

    buscarHorariosLivres();

    return () => {
      ativo = false;
    };
  }, [medicoId, data, versaoDaGrade]);

  const opcoesMedico = useMemo(
    () => medicos.map((medico) => ({ value: String(medico.id), label: medico.nome })),
    [medicos]
  );

  const medicoEscolhido = useMemo(
    () => medicos.find((medico) => String(medico.id) === medicoId) ?? null,
    [medicos, medicoId]
  );

  const horarioEscolhido = useMemo(
    () => horariosLivres.find((slot) => slot.id === horarioEscolhidoId) ?? null,
    [horariosLivres, horarioEscolhidoId]
  );

  function limparGrade(medico: string | null, dia: string | null) {
    setHorarioEscolhidoId(null);
    setHorariosLivres([]);
    setCarregandoHorarios(Boolean(medico && dia));
  }

  function aoEscolherMedico(valor: string | null) {
    setMedicoId(valor);
    limparGrade(valor, data);
  }

  function aoEscolherData(valor: string | null) {
    setData(valor);
    limparGrade(medicoId, valor);
  }

  function recarregarGrade() {
    setHorarioEscolhidoId(null);
    setCarregandoHorarios(true);
    setVersaoDaGrade((versao) => versao + 1);
  }

  async function solicitarConsulta(horarioDisponivelId: number) {
    setEnviando(true);
    try {
      const consulta = await api<Consulta>('/consultas', {
        method: 'POST',
        body: { horario_disponivel_id: horarioDisponivelId },
      });
      // CA1 (RN06) — a consulta nasce SOLICITADA; quem confirma e o atendente (US-13).
      notifications.show({
        title: `Consulta com ${consulta.medico_nome} solicitada`,
        message:
          `${formatarData(consulta.data)} às ${formatarHorario(consulta.horario)} — ` +
          'aguarde a confirmação do atendente em Minhas Consultas.',
        color: 'teal',
      });
      // US-08 → US-10: a notificação manda o paciente para "Minhas Consultas", então
      // o fluxo termina lá. Ficar na grade deixava ele sem saber para onde ir e sem
      // ver a consulta que acabou de solicitar.
      router.push('/consultas');
    } catch (erro) {
      // CA2/CA3 (RN03) — 409 "Horario indisponivel" quando outro paciente reservou antes.
      notifications.show({
        title: 'Não foi possível agendar',
        message: mensagemDoErro(erro, 'Falha inesperada'),
        color: 'red',
      });
      // Só no erro: a CA2/CA3 exige grade fresca para o paciente escolher outro
      // horário. No sucesso a tela já está saindo, e recarregar dispararia um
      // setState depois da navegação.
      recarregarGrade();
    } finally {
      setEnviando(false);
    }
  }

  // US-08 — fluxo de confirmacao antes de gravar a solicitacao.
  function abrirConfirmacao() {
    if (!medicoEscolhido || !horarioEscolhido) return;
    const { id, data: dataDoSlot, horario } = horarioEscolhido;

    modals.openConfirmModal({
      title: 'Confirmar agendamento',
      centered: true,
      children: (
        <Text size="sm">
          Solicitar consulta com <b>{medicoEscolhido.nome}</b> em{' '}
          <b>
            {formatarData(dataDoSlot)} às {formatarHorario(horario)}
          </b>
          ?
        </Text>
      ),
      labels: { confirm: 'Sim, agendar', cancel: 'Voltar' },
      confirmProps: { color: 'teal' },
      onConfirm: () => {
        void solicitarConsulta(id);
      },
    });
  }

  return (
    <Card withBorder radius="md" p={{ base: 'md', sm: 'lg' }}>
      <Stack gap="md">
        <Group grow align="flex-start" wrap="wrap">
          <Select
            label="Médico"
            placeholder="Selecione"
            data={opcoesMedico}
            value={medicoId}
            onChange={aoEscolherMedico}
            searchable
            withAsterisk
          />
          <DateInput
            label="Data"
            placeholder="Selecione a data"
            valueFormat="DD/MM/YYYY"
            dateParser={(valor) => dayjs(valor, 'DD/MM/YYYY').format('YYYY-MM-DD')}
            minDate={new Date()}
            value={data}
            onChange={aoEscolherData}
            withAsterisk
          />
        </Group>

        {medicoId && data ? (
          <>
            <Text size="sm" fw={600}>
              Horários livres
            </Text>
            <GradeHorarios
              horarios={horariosLivres}
              horarioEscolhidoId={horarioEscolhidoId}
              carregando={carregandoHorarios}
              aoEscolher={setHorarioEscolhidoId}
            />
          </>
        ) : (
          <Text c="dimmed" size="sm">
            Escolha o médico e a data para ver os horários livres.
          </Text>
        )}

        <Group justify="flex-end">
          <Button onClick={abrirConfirmacao} disabled={!horarioEscolhido} loading={enviando}>
            Confirmar agendamento
          </Button>
        </Group>
      </Stack>
    </Card>
  );
}
