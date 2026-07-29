"""Slot de agenda de um medico. UniqueConstraint garante a RN05."""

from datetime import date, time

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HorarioDisponivel(Base):
    __tablename__ = "horario_disponivel"
    __table_args__ = (
        # RN05 - o mesmo medico nao pode ter dois slots no mesmo dia/hora.
        UniqueConstraint("medico_id", "data", "horario", name="uq_medico_data_horario"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    medico_id: Mapped[int] = mapped_column(ForeignKey("medico.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    horario: Mapped[time] = mapped_column(Time, nullable=False)
    disponivel: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)  # RN03

    medico: Mapped["Medico"] = relationship(back_populates="horarios")  # noqa: F821
    consultas: Mapped[list["Consulta"]] = relationship(back_populates="horario")  # noqa: F821
