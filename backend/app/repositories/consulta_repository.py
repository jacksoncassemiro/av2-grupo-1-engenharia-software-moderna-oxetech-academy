from sqlalchemy import select

from app.models.consulta import Consulta
from app.models.enums import STATUS_QUE_OCUPAM_SLOT, StatusConsulta
from app.repositories.base import RepositorioBase


class ConsultaRepository(RepositorioBase[Consulta]):
    modelo = Consulta

    def listar_por_paciente(self, paciente_id: int) -> list[Consulta]:
        return list(
            self.db.scalars(
                select(Consulta)
                .where(Consulta.paciente_id == paciente_id)
                .order_by(Consulta.data_agendamento.desc())
            ).all()
        )

    def existe_ativa_no_slot(self, horario_disponivel_id: int) -> bool:
        """RN03 - ha consulta SOLICITADA/CONFIRMADA ocupando este slot?"""
        return (
            self.db.scalars(
                select(Consulta.id)
                .where(
                    Consulta.horario_disponivel_id == horario_disponivel_id,
                    Consulta.status.in_(STATUS_QUE_OCUPAM_SLOT),
                )
                .limit(1)
            ).first()
            is not None
        )

    def listar_por_status(self, status: StatusConsulta) -> list[Consulta]:
        return list(self.db.scalars(select(Consulta).where(Consulta.status == status)).all())
