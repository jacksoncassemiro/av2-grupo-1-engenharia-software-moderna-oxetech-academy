from sqlalchemy import func, select

from app.models.especialidade import Especialidade
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
        return list(self.db.scalars(self._filtrar_especialidade(consulta, especialidade_id)).all())

    def listar_agendaveis(self, especialidade_id: int | None = None) -> list[Medico]:
        """Medicos que podem receber consulta nova: RN16 (medico) + RN17 (especialidade).

        Separado de `listar_ativos` de proposito: o atendente precisa continuar
        enxergando o medico ativo cuja especialidade foi inativada, senao ele
        desaparece da gestao e ninguem entende por que parou de receber consulta.
        """
        consulta = (
            select(Medico)
            .join(Medico.especialidade)
            .where(Medico.ativo.is_(True), Especialidade.ativo.is_(True))
        )
        return list(self.db.scalars(self._filtrar_especialidade(consulta, especialidade_id)).all())

    @staticmethod
    def _filtrar_especialidade(consulta, especialidade_id: int | None):
        if especialidade_id is None:
            return consulta
        return consulta.where(Medico.especialidade_id == especialidade_id)
