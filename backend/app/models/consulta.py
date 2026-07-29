"""Consulta agendada. Ver ADR-006 sobre o indice parcial que garante a RN03."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import StatusConsulta

# RN03 - somente consultas SOLICITADA/CONFIRMADA ocupam o slot. Consultas CANCELADAS
# (ou FINALIZADAS) ficam fora do indice, o que permite reagendar o slot liberado.
_SLOT_OCUPADO = text("status IN ('SOLICITADA', 'CONFIRMADA')")


class Consulta(Base):
    __tablename__ = "consulta"
    __table_args__ = (
        Index(
            "uq_slot_ativo",
            "horario_disponivel_id",
            unique=True,
            postgresql_where=_SLOT_OCUPADO,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("paciente.id"), nullable=False)
    medico_id: Mapped[int] = mapped_column(ForeignKey("medico.id"), nullable=False)
    horario_disponivel_id: Mapped[int] = mapped_column(
        ForeignKey("horario_disponivel.id"), nullable=False
    )
    status: Mapped[StatusConsulta] = mapped_column(
        Enum(StatusConsulta, name="status_consulta"),
        nullable=False,
        default=StatusConsulta.SOLICITADA,
    )
    data_agendamento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    motivo_cancelamento: Mapped[str | None] = mapped_column(Text, nullable=True)

    paciente: Mapped["Paciente"] = relationship(back_populates="consultas")  # noqa: F821
    horario: Mapped["HorarioDisponivel"] = relationship(back_populates="consultas")  # noqa: F821
