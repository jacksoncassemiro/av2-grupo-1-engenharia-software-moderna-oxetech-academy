# Visão do produto

## Problema

Uma clínica médica agenda consultas por **telefone e planilhas**. Consequências práticas:

- Agendamento só funciona no horário comercial e ocupa a recepcionista em ligações.
- A planilha não impede dois pacientes no mesmo horário — o conflito só aparece no balcão.
- O paciente não tem como consultar o próprio histórico sem ligar.
- Cancelamento de última hora deixa o horário vazio, porque ninguém sabe que vagou.
- Não há registro confiável de quem alterou o quê.

## Proposta

Um sistema web que substitui a planilha por um banco relacional com **regras de integridade
no próprio banco**, e move o autoatendimento do paciente para a web. O que a planilha
permitia por descuido, o sistema bloqueia por constraint.

## Objetivo do MVP

Entregar, até **10/08/2026** (11 dias corridos), o ciclo completo de agendamento — cadastro, consulta de
disponibilidade, agendamento, cancelamento — para os perfis **Paciente** e **Atendente**,
com as seis regras de negócio obrigatórias demonstráveis por teste automatizado.

Como se trata da AV2 de *Engenharia de Software Moderna*, o MVP é também o veículo para
demonstrar Clean Code, SOLID, Design Patterns, arquitetura em camadas e CI/CD. O critério de
sucesso é **qualidade e rastreabilidade**, não volume de features.

## Público-alvo

| Perfil | Quem é | Dor principal | O que o MVP entrega |
|---|---|---|---|
| **Paciente** | Pessoa que precisa de consulta | Depende de ligação em horário comercial | Vê disponibilidade real e agenda/cancela sozinho, 24h |
| **Atendente** | Recepção da clínica | Perde o dia no telefone e erra na planilha | Cadastros centralizados, agenda com bloqueio automático de conflito |

## Escopo

### Dentro do MVP

- Autenticação JWT com campo único **"CPF ou E-mail"** (paciente usa CPF, atendente usa e-mail)
- Primeiro acesso por CPF: ativa o login de quem foi cadastrado no balcão **ou** faz o
  auto-cadastro completo de quem nunca esteve na clínica
- Cadastro de especialidades, médicos, pacientes e grade de horários
- Consulta de médicos com filtro por especialidade
- Visualização de horários realmente livres
- Solicitação de consulta pelo paciente (status `SOLICITADA`)
- Agendamento pelo atendente (status `CONFIRMADA`)
- Confirmação e finalização de consultas pelo atendente
- Cancelamento pelo paciente com regra de 24h; pelo atendente sem restrição
- Liberação automática do horário ao cancelar
- Histórico de consultas do paciente
- Autorização por perfil em todas as rotas
- Seed idempotente que cria o primeiro atendente
- Ambiente completo em Docker Compose e pipeline de CI

### Fora do MVP (registrado, não esquecido)

| Item | Por que ficou fora |
|---|---|
| Perfil **Médico** com login e prontuário | Não há US no enunciado; triplicaria telas e testes |
| Perfil **Admin** separado | Resolvido por RN14 (atendente cria atendente) com menos escopo |
| Notificação por e-mail/SMS/WhatsApp | Depende de serviço externo, sem valor de avaliação |
| Prontuário eletrônico, prescrição, exames | Outro domínio, com exigências legais próprias |
| Pagamento, convênio, faturamento | Fora do problema descrito |
| Recuperação de senha por e-mail | Paciente pode não ter e-mail; exigiria provedor de envio |
| Reagendamento em um passo | Cancelar + agendar já cobre o caso |
| Relatórios e dashboard gerencial | Não há requisito |
| Deploy em nuvem | Docker Compose local atende a demonstração |
| Auditoria completa (log de alterações) | `criado_em` e `motivo_cancelamento` cobrem o mínimo |
| Médico com múltiplas especialidades | 1:N atende o MVP; migração aditiva depois |

## Proposta de valor

| Antes | Depois |
|---|---|
| Agendar exige ligação em horário comercial | Paciente agenda quando quiser |
| Conflito de horário descoberto no balcão | Banco recusa a operação na hora (RN03, RN05) |
| Cadastro duplicado invisível | CPF e e-mail únicos por constraint (RN01, RN02) |
| Cancelamento sem prazo, horário perdido | Regra de 24h e horário devolvido à agenda (RN04) |
| Status da consulta na cabeça de quem atendeu | Quatro status auditáveis com transição controlada (RN06) |
| Histórico só por telefone | Paciente consulta o próprio histórico |

## Métricas de sucesso (avaliação da AV2)

| Métrica | Meta |
|---|---|
| Regras RN01–RN15 com teste automatizado | 100% |
| Testes unitários por stack | ≥ 5 exigidos · **17 no backend · 11 no frontend** |
| Casos de teste executados com evidência | 14 |
| Pipeline de CI verde em `develop` | Sempre |
| Bugs Críticos ou Altos em aberto no fim da Sprint 2 | 0 |
| Tempo para um novo membro subir o projeto | 1 comando (`make bootstrap`) |
| Práticas de Clean Code documentadas com exemplo ruim/bom | 3 |
| Design Patterns implementados e justificados por ADR | 2 |

## Riscos e mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| 11 dias corridos é curto | Alto | Escopo reduzido a 14 US pelo [ADR-008](ADR-008-Rebaseline-de-Escopo); corte por US inteira, nunca pela metade |
| Equipe com níveis técnicos diferentes | Médio | `CLAUDE.md` + skills em `.claude/skills/` padronizam o "como fazer" |
| Ambiente diferente em cada máquina | Médio | Docker Compose; job de CI prova que sobe do zero |
| Conflito de merge no monorepo | Médio | Divisão backend/frontend por pessoa; PRs pequenos |
| Regra de fuso quebrar a RN04 na demo | Médio | RN15 fixa o fuso; `agora` injetado nos testes |
| Divergência sobre a composição da equipe | Alto | Ver conflito C13 — decidir no Sprint Planning e corrigir o README |

## Fontes do enunciado

1. Case 1 — Sistema de Gestão de Clínica Médica
2. Lista de funcionalidades por perfil + RN01–RN06
3. Backlog do Wiki (US-00 a US-12)
4. Material das aulas em [`material-aulas/`](https://github.com/jacksoncassemiro/av2-grupo-1-engenharia-software-moderna-oxetech-academy/blob/develop/docs/material-aulas)

As divergências entre 1, 2 e 3 estão analisadas em
[14-conflitos-e-decisoes.md](Conflitos-e-Decisoes).


---

> 📄 Esta página é gerada a partir de `docs/` no repositório. **Não edite aqui** — edite o arquivo correspondente e rode `scripts/publicar-wiki.sh`.
