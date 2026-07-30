from datetime import date, time

from sqlalchemy import select

from app.models.horario_disponivel import HorarioDisponivel
from app.repositories.base import RepositorioBase


class HorarioRepository(RepositorioBase[HorarioDisponivel]):
    modelo = HorarioDisponivel

    def buscar_slot(self, medico_id: int, data: date, horario: time) -> HorarioDisponivel | None:
        """RN05 - checa se o medico ja tem esse slot cadastrado."""
        return self.db.scalars(
            select(HorarioDisponivel).where(
                HorarioDisponivel.medico_id == medico_id,
                HorarioDisponivel.data == data,
                HorarioDisponivel.horario == horario,
            )
        ).first()

    def listar_livres(self, medico_id: int, data: date) -> list[HorarioDisponivel]:
        """RN03 - somente slots ainda disponiveis."""
        return list(
            self.db.scalars(
                select(HorarioDisponivel)
                .where(
                    HorarioDisponivel.medico_id == medico_id,
                    HorarioDisponivel.data == data,
                    HorarioDisponivel.disponivel.is_(True),
                )
                .order_by(HorarioDisponivel.horario)
            ).all()
        )

    def buscar_para_reserva(self, horario_id: int) -> HorarioDisponivel | None:
        """SELECT ... FOR UPDATE - evita corrida de dois pacientes no mesmo slot (US-08)."""
        return self.db.scalars(
            select(HorarioDisponivel).where(HorarioDisponivel.id == horario_id).with_for_update()
        ).first()
