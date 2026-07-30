from sqlalchemy import select

from app.models.usuario import Usuario
from app.repositories.base import RepositorioBase


class UsuarioRepository(RepositorioBase[Usuario]):
    modelo = Usuario

    def buscar_por_login(self, login: str) -> Usuario | None:
        return self.db.scalars(select(Usuario).where(Usuario.login == login)).first()

    def buscar_por_paciente_id(self, paciente_id: int) -> Usuario | None:
        return self.db.scalars(select(Usuario).where(Usuario.paciente_id == paciente_id)).first()

    def existe_atendente(self) -> bool:
        from app.models.enums import TipoUsuario

        return (
            self.db.scalars(
                select(Usuario.id).where(Usuario.tipo_usuario == TipoUsuario.ATENDENTE).limit(1)
            ).first()
            is not None
        )
