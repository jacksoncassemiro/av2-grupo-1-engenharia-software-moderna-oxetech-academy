from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import StatusConsulta


class ConsultaSolicitar(BaseModel):
    """US-08 - paciente escolhe um slot livre."""

    horario_disponivel_id: int


class ConsultaAgendarPorAtendente(ConsultaSolicitar):
    """US-09 - atendente agenda para um paciente."""

    paciente_id: int


class ConsultaCancelar(BaseModel):
    motivo: str | None = Field(default=None, max_length=500)


class ConsultaMudarStatus(BaseModel):
    """US-13 - CONFIRMADA ou FINALIZADA."""

    status: StatusConsulta


class ConsultaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_id: int
    medico_id: int
    horario_disponivel_id: int
    status: StatusConsulta
    data_agendamento: datetime
    motivo_cancelamento: str | None
