"""Camada Model do MVC - entidades SQLAlchemy.

Importar tudo aqui garante que o Alembic e o metadata enxerguem todas as tabelas.
"""

from app.models.consulta import Consulta
from app.models.especialidade import Especialidade
from app.models.enums import StatusConsulta, TipoUsuario
from app.models.horario_disponivel import HorarioDisponivel
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.usuario import Usuario

__all__ = [
    "Consulta",
    "Especialidade",
    "HorarioDisponivel",
    "Medico",
    "Paciente",
    "StatusConsulta",
    "TipoUsuario",
    "Usuario",
]
