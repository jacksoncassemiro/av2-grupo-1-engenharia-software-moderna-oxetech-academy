"""Credencial de acesso. `login` aceita CPF (paciente) ou e-mail (atendente) - US-00."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import TipoUsuario


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    login: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_usuario: Mapped[TipoUsuario] = mapped_column(
        Enum(TipoUsuario, name="tipo_usuario"), nullable=False
    )
    paciente_id: Mapped[int | None] = mapped_column(
        ForeignKey("paciente.id"), nullable=True, unique=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    paciente: Mapped["Paciente | None"] = relationship(back_populates="usuario")  # noqa: F821
