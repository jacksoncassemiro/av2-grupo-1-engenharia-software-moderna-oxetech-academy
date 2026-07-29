from sqlalchemy import select

from app.models.paciente import Paciente
from app.repositories.base import RepositorioBase


class PacienteRepository(RepositorioBase[Paciente]):
    modelo = Paciente

    def buscar_por_cpf(self, cpf: str) -> Paciente | None:
        return self.db.scalars(select(Paciente).where(Paciente.cpf == cpf)).first()

    def buscar_por_email(self, email: str) -> Paciente | None:
        return self.db.scalars(select(Paciente).where(Paciente.email == email)).first()
