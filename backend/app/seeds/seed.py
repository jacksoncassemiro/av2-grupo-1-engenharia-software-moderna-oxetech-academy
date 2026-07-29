"""Seed idempotente (ADR-004).

Cria o PRIMEIRO atendente para resolver o problema do ovo-e-galinha: sem
atendente ninguem cadastra medico/especialidade/paciente. A partir dai, o
proprio atendente cadastra outros atendentes pela UI (RN14) - nao existe rota
publica de cadastro de atendente, o que seria uma falha de seguranca.

Rodar com:  docker compose exec backend python -m app.seeds.seed
"""

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import gerar_hash_senha
from app.models.enums import TipoUsuario
from app.models.especialidade import Especialidade
from app.models.usuario import Usuario
from app.repositories.especialidade_repository import EspecialidadeRepository
from app.repositories.usuario_repository import UsuarioRepository

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("seed")

ESPECIALIDADES_INICIAIS = [
    ("Clinica Geral", "Atendimento clinico de primeira linha"),
    ("Cardiologia", "Diagnostico e tratamento do sistema cardiovascular"),
    ("Pediatria", "Atendimento de criancas e adolescentes"),
]


def criar_atendente_inicial(db: Session) -> None:
    usuarios = UsuarioRepository(db)
    if usuarios.existe_atendente():
        log.info("Atendente ja existe - nada a fazer.")
        return

    usuarios.salvar(
        Usuario(
            nome=settings.SEED_ATENDENTE_NOME,
            login=settings.SEED_ATENDENTE_LOGIN.lower(),
            senha_hash=gerar_hash_senha(settings.SEED_ATENDENTE_SENHA),
            tipo_usuario=TipoUsuario.ATENDENTE,
        )
    )
    log.info("Atendente inicial criado: %s", settings.SEED_ATENDENTE_LOGIN)


def criar_especialidades_iniciais(db: Session) -> None:
    repositorio = EspecialidadeRepository(db)
    for nome, descricao in ESPECIALIDADES_INICIAIS:
        if repositorio.buscar_por_nome(nome) is None:
            repositorio.salvar(Especialidade(nome=nome, descricao=descricao))
            log.info("Especialidade criada: %s", nome)


def main() -> None:
    with SessionLocal() as db:
        criar_atendente_inicial(db)
        criar_especialidades_iniciais(db)
        db.commit()
    log.info("Seed concluido.")


if __name__ == "__main__":
    main()
