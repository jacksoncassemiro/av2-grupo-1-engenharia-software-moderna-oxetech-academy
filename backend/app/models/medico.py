from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Medico(Base):
    __tablename__ = "medico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)  # RN02
    crm: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    especialidade_id: Mapped[int] = mapped_column(ForeignKey("especialidade.id"), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    especialidade: Mapped["Especialidade"] = relationship(back_populates="medicos")  # noqa: F821
    horarios: Mapped[list["HorarioDisponivel"]] = relationship(  # noqa: F821
        back_populates="medico"
    )
