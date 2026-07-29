from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field, field_validator

HORA_ABERTURA = time(8, 0)
HORA_FECHAMENTO = time(18, 0)


class GradeHorariaCriar(BaseModel):
    """US-05 - lanca varios slots de uma vez para o mesmo dia."""

    data: date
    horarios: list[time] = Field(min_length=1)

    @field_validator("horarios")
    @classmethod
    def _validar_horario_comercial(cls, valores: list[time]) -> list[time]:
        """RN09 - so aceita horarios dentro do funcionamento da clinica."""
        fora = [h for h in valores if not (HORA_ABERTURA <= h < HORA_FECHAMENTO)]
        if fora:
            raise ValueError(
                f"Horarios fora do funcionamento (08:00-18:00): "
                f"{', '.join(h.isoformat() for h in fora)}"
            )
        return valores


class HorarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medico_id: int
    data: date
    horario: time
    disponivel: bool
