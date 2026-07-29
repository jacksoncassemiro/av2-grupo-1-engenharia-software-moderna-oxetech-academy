"""Dados cadastrais do paciente. E-mail e opcional (paciente de balcao pode nao ter)."""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Paciente(Base):
    __tablename__ = "paciente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True, index=True)  # RN01
    email: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True)  # RN02
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    usuario: Mapped["Usuario | None"] = relationship(back_populates="paciente")  # noqa: F821
    consultas: Mapped[list["Consulta"]] = relationship(back_populates="paciente")  # noqa: F821
