"""Repository Pattern (Design Pattern 2 - ADR-006).

Isola o SQLAlchemy das regras de negocio. Os Services dependem desta abstracao,
nunca de `Session` diretamente - o que satisfaz o DIP do SOLID e permite trocar
o repositorio por um fake/mock nos testes unitarios sem subir banco.
"""

from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import Base

ModeloT = TypeVar("ModeloT", bound=Base)


class RepositorioBase(ABC, Generic[ModeloT]):
    modelo: type[ModeloT]

    def __init__(self, db: Session):
        self.db = db

    def buscar_por_id(self, id_: int) -> ModeloT | None:
        return self.db.get(self.modelo, id_)

    def listar(self) -> list[ModeloT]:
        return list(self.db.scalars(select(self.modelo)).all())

    def salvar(self, entidade: ModeloT) -> ModeloT:
        self.db.add(entidade)
        self.db.flush()
        return entidade
