"""Enums de dominio. Nomes explicitos em vez de codigos magicos (Clean Code)."""

from enum import Enum


class StrEnum(str, Enum):
    """Compat 3.10+: mesmo comportamento de enum.StrEnum (Python 3.11+)."""

    def __str__(self) -> str:
        return str(self.value)


class TipoUsuario(StrEnum):
    PACIENTE = "PACIENTE"
    ATENDENTE = "ATENDENTE"


class StatusConsulta(StrEnum):
    """RN06 - estados possiveis de uma consulta."""

    SOLICITADA = "SOLICITADA"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"


# RN10 - maquina de estados: de onde para onde uma consulta pode ir.
TRANSICOES_PERMITIDAS: dict[StatusConsulta, set[StatusConsulta]] = {
    StatusConsulta.SOLICITADA: {StatusConsulta.CONFIRMADA, StatusConsulta.CANCELADA},
    StatusConsulta.CONFIRMADA: {StatusConsulta.FINALIZADA, StatusConsulta.CANCELADA},
    StatusConsulta.CANCELADA: set(),
    StatusConsulta.FINALIZADA: set(),
}

STATUS_QUE_OCUPAM_SLOT: set[StatusConsulta] = {
    StatusConsulta.SOLICITADA,
    StatusConsulta.CONFIRMADA,
}
