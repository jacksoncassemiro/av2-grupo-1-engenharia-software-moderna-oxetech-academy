'use client';

import { Alert, Anchor, Button, Card, Divider, Stack, Stepper, Text, Title } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { FormularioAtivarLogin } from '@/components/primeiro-acesso/FormularioAtivarLogin';
import { FormularioAutoCadastro } from '@/components/primeiro-acesso/FormularioAutoCadastro';
import { FormularioCpf } from '@/components/primeiro-acesso/FormularioCpf';
import { api, ApiError, guardarToken } from '@/lib/api';
import { apenasDigitos } from '@/lib/cpf';
import { decidirEtapa, type EtapaPrimeiroAcesso } from '@/lib/primeiro-acesso';
import type {
  PrimeiroAcessoRequisicao,
  TokenResposta,
  VerificarCpfResposta,
} from '@/types/dominio';

/**
 * Painel inicial do paciente (US-10). A tela ainda nao existe — chega junto com a
 * lista de consultas. E o destino correto por especificacao: apos o primeiro acesso
 * o paciente ja esta autenticado e pode solicitar consulta (CA5).
 */
const ROTA_INICIAL_DO_PACIENTE = '/consultas';

/** Fluxo de duas etapas da US-00: verifica o CPF, depois pede o que faltar. */
export function PrimeiroAcesso() {
  const router = useRouter();
  const [etapa, setEtapa] = useState<EtapaPrimeiroAcesso>('cpf');
  const [cpf, setCpf] = useState('');
  const [nome, setNome] = useState('');
  const [carregando, setCarregando] = useState(false);

  async function verificarCpf(cpfDigitado: string) {
    const cpfLimpo = apenasDigitos(cpfDigitado);
    setCarregando(true);
    try {
      const resposta = await api<VerificarCpfResposta>(`/auth/verificar-cpf/${cpfLimpo}`);
      setCpf(cpfLimpo);
      setNome(resposta.nome ?? '');
      setEtapa(decidirEtapa(resposta));
    } catch (erro) {
      notificarFalha(erro);
    } finally {
      setCarregando(false);
    }
  }

  async function concluir(dados: PrimeiroAcessoRequisicao) {
    setCarregando(true);
    try {
      const token = await api<TokenResposta>('/auth/vincular-ou-criar', {
        method: 'POST',
        body: dados,
      });
      guardarToken(token.access_token);
      notifications.show({
        message: 'Acesso ativado. Bem-vindo!',
        color: 'green',
      });
      router.replace(ROTA_INICIAL_DO_PACIENTE);
    } catch (erro) {
      notificarFalha(erro);
    } finally {
      setCarregando(false);
    }
  }

  function notificarFalha(erro: unknown) {
    // CA6 tambem cai aqui: o backend recusa o vinculo de um CPF que ja tem login.
    notifications.show({
      message: erro instanceof ApiError ? erro.message : 'Falha inesperada. Tente de novo.',
      color: 'red',
    });
  }

  function renderizarEtapa() {
    switch (etapa) {
      case 'cpf':
        return <FormularioCpf onVerificar={verificarCpf} carregando={carregando} />;
      case 'ativar-login':
        return (
          <FormularioAtivarLogin
            cpf={cpf}
            nome={nome}
            onEnviar={(senha) => concluir({ cpf, senha })}
            carregando={carregando}
          />
        );
      case 'auto-cadastro':
        return (
          <FormularioAutoCadastro
            cpf={cpf}
            onEnviar={(dados) => concluir({ ...dados, cpf })}
            carregando={carregando}
          />
        );
      case 'login-ja-ativo':
        return <AvisoLoginJaAtivo />;
    }
  }

  return (
    <Card withBorder shadow="sm" radius="md" padding="xl">
      <Stack gap="lg">
        <div>
          <Title order={1} size="h3">
            Primeiro acesso
          </Title>
          <Text c="dimmed" size="sm">
            Clínica Médica
          </Text>
        </div>

        <Stepper active={etapa === 'cpf' ? 0 : 1} size="sm">
          <Stepper.Step label="CPF" />
          <Stepper.Step label="Dados" />
        </Stepper>

        {renderizarEtapa()}

        <Divider />

        <Text size="sm" ta="center">
          <Anchor component={Link} href="/login">
            Já tenho login, voltar para entrar
          </Anchor>
        </Text>
      </Stack>
    </Card>
  );
}

/** CA6 - CPF que ja possui login nao passa por aqui: vai para a tela de login. */
function AvisoLoginJaAtivo() {
  return (
    <Stack gap="md">
      <Alert color="yellow" title="Este CPF já possui login ativo">
        Você já criou sua senha anteriormente. Use a tela de login.
      </Alert>
      <Button component={Link} href="/login" size="md" fullWidth>
        Ir para o login
      </Button>
    </Stack>
  );
}
