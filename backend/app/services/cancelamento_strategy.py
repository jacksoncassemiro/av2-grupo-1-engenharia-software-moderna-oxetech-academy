"""Strategy Pattern (Design Pattern 1 - ADR-006).

Problema: a regra de cancelamento depende de QUEM cancela.
  - Paciente  -> so pode cancelar com >= 24h de antecedencia (RN04)
  - Atendente -> pode cancelar a qualquer momento (US-12)

Sem Strategy isso viraria um `if perfil == "PACIENTE" ... elif ...` dentro do
service - exatamente o antipadrao que o OCP do SOLID pede para evitar. Com
Strategy, adicionar um terceiro perfil (ex.: MEDICO) e criar uma classe nova,
sem tocar em codigo que ja funciona.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.exceptions.dominio import CancelamentoNaoPermitido
from app.models.consulta import Consulta
from app.models.enums import TipoUsuario


def momento_agendado(consulta: Consulta) -> datetime:
    """Combina data + horario do slot no fuso de referencia da clinica (RN15)."""
    slot = consulta.horario
    return datetime.combine(slot.data, slot.horario, tzinfo=ZoneInfo(settings.TIMEZONE))


class CancelamentoStrategy(ABC):
    """Contrato de validacao de cancelamento."""

    @abstractmethod
    def validar(self, consulta: Consulta, agora: datetime) -> None:
        """Levanta CancelamentoNaoPermitido quando o cancelamento nao e permitido."""


class CancelamentoPorPaciente(CancelamentoStrategy):
    """RN04 - exige antecedencia minima."""

    def __init__(self, antecedencia_minima_horas: int = 24):
        self.antecedencia_minima = timedelta(hours=antecedencia_minima_horas)

    def validar(self, consulta: Consulta, agora: datetime) -> None:
        if momento_agendado(consulta) - agora < self.antecedencia_minima:
            raise CancelamentoNaoPermitido


class CancelamentoPorAtendente(CancelamentoStrategy):
    """US-12 - atendente cancela sem restricao de prazo."""

    def validar(self, consulta: Consulta, agora: datetime) -> None:  # noqa: ARG002
        return None


def obter_strategy(perfil: TipoUsuario, antecedencia_horas: int = 24) -> CancelamentoStrategy:
    """Factory simples que resolve a estrategia a partir do perfil autenticado."""
    if perfil is TipoUsuario.PACIENTE:
        return CancelamentoPorPaciente(antecedencia_horas)
    return CancelamentoPorAtendente()
