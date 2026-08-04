from sqlalchemy import func, select

from app.models.especialidade import Especialidade
from app.repositories.base import RepositorioBase


class EspecialidadeRepository(RepositorioBase[Especialidade]):
    modelo = Especialidade

    def buscar_por_nome(self, nome: str) -> Especialidade | None:
        return self.db.scalars(
            select(Especialidade).where(func.lower(Especialidade.nome) == nome.strip().lower())
        ).first()

    def listar_ativas(self, apenas_ativas: bool = True) -> list[Especialidade]:
        consulta = select(Especialidade)
        if apenas_ativas:
            consulta = consulta.where(Especialidade.ativo.is_(True))
        return list(self.db.scalars(consulta).all())
