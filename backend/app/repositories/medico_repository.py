from sqlalchemy import func, select

from app.models.medico import Medico
from app.repositories.base import RepositorioBase


class MedicoRepository(RepositorioBase[Medico]):
    modelo = Medico

    def buscar_por_email(self, email: str) -> Medico | None:
        return self.db.scalars(
            select(Medico).where(func.lower(Medico.email) == email.strip().lower())
        ).first()

    def buscar_por_crm(self, crm: str) -> Medico | None:
        return self.db.scalars(
            select(Medico).where(func.lower(Medico.crm) == crm.strip().lower())
        ).first()

    def listar_ativos(
        self, especialidade_id: int | None = None, apenas_ativos: bool | None = None
    ) -> list[Medico]:
        consulta = select(Medico)
        if apenas_ativos is not None:
            consulta = consulta.where(Medico.ativo.is_(apenas_ativos))
        if especialidade_id is not None:
            consulta = consulta.where(Medico.especialidade_id == especialidade_id)
        return list(self.db.scalars(consulta).all())
