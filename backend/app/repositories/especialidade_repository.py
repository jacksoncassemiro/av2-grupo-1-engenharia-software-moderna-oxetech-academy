from sqlalchemy import select

from app.models.especialidade import Especialidade
from app.repositories.base import RepositorioBase


class EspecialidadeRepository(RepositorioBase[Especialidade]):
    modelo = Especialidade

    def buscar_por_nome(self, nome: str) -> Especialidade | None:
        return self.db.scalars(select(Especialidade).where(Especialidade.nome == nome)).first()

    def listar_ativas(self) -> list[Especialidade]:
        return list(
            self.db.scalars(select(Especialidade).where(Especialidade.ativo.is_(True))).all()
        )
