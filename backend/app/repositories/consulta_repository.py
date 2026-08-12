from datetime import datetime

from sqlalchemy import case, select

from app.models.consulta import Consulta
from app.models.enums import STATUS_QUE_OCUPAM_SLOT, StatusConsulta
from app.models.horario_disponivel import HorarioDisponivel
from app.repositories.base import RepositorioBase


class ConsultaRepository(RepositorioBase[Consulta]):
    modelo = Consulta

    def listar_por_paciente(self, paciente_id: int, agora: datetime) -> list[Consulta]:
        """US-10 - futuras primeiro (a proxima no topo), depois o historico mais recente.

        Ordenar por `data_agendamento` colocaria a consulta marcada por ultimo no
        topo, e nao a que acontece primeiro. `agora` vem do service, no fuso da RN15.
        """
        momento_do_slot = HorarioDisponivel.data + HorarioDisponivel.horario
        ja_passou = case((momento_do_slot < agora, 1), else_=0)

        return list(
            self.db.scalars(
                select(Consulta)
                .join(Consulta.horario)
                .where(Consulta.paciente_id == paciente_id)
                .order_by(
                    ja_passou,  # futuras (0) antes do historico (1)
                    case((ja_passou == 0, momento_do_slot), else_=None).asc().nulls_last(),
                    momento_do_slot.desc(),  # dentro do historico, o mais recente primeiro
                )
            ).all()
        )

    def existe_ativa_no_slot(self, horario_disponivel_id: int) -> bool:
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

    def buscar_para_atualizar(self, consulta_id: int) -> Consulta | None:
        """SELECT ... FOR UPDATE - serializa mudancas de status concorrentes (RN06 / RN10).

        Mesmo padrao de `HorarioRepository.buscar_para_reserva`: sem a trava, cancelar
        e confirmar a mesma consulta ao mesmo tempo geram lost update - a escrita que
        leu o estado antigo sobrescreve a outra e deixa `consulta.status` e
        `horario.disponivel` inconsistentes entre si (RN03).
        """
        return self.db.scalars(
            select(Consulta).where(Consulta.id == consulta_id).with_for_update()
        ).first()
