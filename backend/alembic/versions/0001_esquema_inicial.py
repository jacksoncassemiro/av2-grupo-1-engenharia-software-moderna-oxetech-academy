"""Esquema inicial: usuario, paciente, especialidade, medico, horario_disponivel, consulta

Materializa no banco as regras de negocio que dependem de constraint:

  RN01  UNIQUE (paciente.cpf)
  RN02  UNIQUE (paciente.email), UNIQUE (medico.email), UNIQUE (usuario.login)
  RN03  indice PARCIAL uq_slot_ativo em consulta - ver nota abaixo
  RN05  UNIQUE (medico_id, data, horario) em horario_disponivel
  RN06  ENUM status_consulta

Nota sobre a RN03 (ADR-006): o indice e PARCIAL de proposito. Um UNIQUE comum em
consulta.horario_disponivel_id tornaria o slot inutilizavel para sempre depois do
primeiro cancelamento, porque a linha CANCELADA continuaria ocupando o indice -
quebrando a US-11, que diz que o horario volta a ficar disponivel. O `WHERE status
IN ('SOLICITADA','CONFIRMADA')` deixa consultas CANCELADAS/FINALIZADAS fora do
indice, liberando o slot para reagendamento.

O `alembic revision --autogenerate` NAO detecta indice parcial. Se regenerar esta
migracao, confira se o `postgresql_where` continua presente.

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_esquema_inicial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Os ENUMs sao declarados com create_type=False para que a criacao/remocao do tipo
# seja explicita, e nao um efeito colateral do create_table.
tipo_usuario = sa.Enum("PACIENTE", "ATENDENTE", name="tipo_usuario", create_type=False)
status_consulta = sa.Enum(
    "SOLICITADA",
    "CONFIRMADA",
    "CANCELADA",
    "FINALIZADA",
    name="status_consulta",
    create_type=False,
)


def upgrade() -> None:
    conexao = op.get_bind()
    tipo_usuario.create(conexao, checkfirst=True)
    status_consulta.create(conexao, checkfirst=True)

    # ------------------------------------------------------------------ especialidade
    op.create_table(
        "especialidade",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id", name="pk_especialidade"),
        sa.UniqueConstraint("nome", name="uq_especialidade_nome"),
    )

    # ----------------------------------------------------------------------- paciente
    op.create_table(
        "paciente",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        # RN01 - CPF unico
        sa.Column("cpf", sa.String(length=11), nullable=False),
        # RN02 - e-mail unico, mas NULLABLE: paciente de balcao pode nao ter e-mail.
        # Em PostgreSQL, UNIQUE permite multiplos NULL - que e o comportamento desejado.
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("telefone", sa.String(length=20), nullable=False),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_paciente"),
        sa.UniqueConstraint("cpf", name="uq_paciente_cpf"),
        sa.UniqueConstraint("email", name="uq_paciente_email"),
    )
    op.create_index("ix_paciente_cpf", "paciente", ["cpf"])

    # ------------------------------------------------------------------------- medico
    op.create_table(
        "medico",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("crm", sa.String(length=20), nullable=False),
        sa.Column("especialidade_id", sa.Integer(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id", name="pk_medico"),
        sa.UniqueConstraint("email", name="uq_medico_email"),
        sa.UniqueConstraint("crm", name="uq_medico_crm"),
        sa.ForeignKeyConstraint(
            ["especialidade_id"],
            ["especialidade.id"],
            name="fk_medico_especialidade",
        ),
    )

    # ------------------------------------------------------------------------ usuario
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        # US-00 - guarda CPF (paciente) ou e-mail (atendente). RN02.
        sa.Column("login", sa.String(length=120), nullable=False),
        # RN11 - hash bcrypt, nunca senha em texto claro
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("tipo_usuario", tipo_usuario, nullable=False),
        # Nulo para ATENDENTE; unico para garantir uma credencial por paciente.
        sa.Column("paciente_id", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_usuario"),
        sa.UniqueConstraint("login", name="uq_usuario_login"),
        sa.UniqueConstraint("paciente_id", name="uq_usuario_paciente"),
        sa.ForeignKeyConstraint(
            ["paciente_id"], ["paciente.id"], name="fk_usuario_paciente"
        ),
    )
    op.create_index("ix_usuario_login", "usuario", ["login"])

    # -------------------------------------------------------------- horario_disponivel
    op.create_table(
        "horario_disponivel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("medico_id", sa.Integer(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("horario", sa.Time(), nullable=False),
        # RN03 - flag de disponibilidade consultada pela US-07
        sa.Column("disponivel", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id", name="pk_horario_disponivel"),
        sa.ForeignKeyConstraint(
            ["medico_id"], ["medico.id"], name="fk_horario_medico"
        ),
        # RN05 - o mesmo medico nao pode ter dois slots no mesmo dia/hora
        sa.UniqueConstraint(
            "medico_id", "data", "horario", name="uq_medico_data_horario"
        ),
    )

    # ----------------------------------------------------------------------- consulta
    op.create_table(
        "consulta",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("paciente_id", sa.Integer(), nullable=False),
        sa.Column("medico_id", sa.Integer(), nullable=False),
        sa.Column("horario_disponivel_id", sa.Integer(), nullable=False),
        # RN06
        sa.Column("status", status_consulta, nullable=False),
        sa.Column(
            "data_agendamento",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("motivo_cancelamento", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_consulta"),
        sa.ForeignKeyConstraint(
            ["paciente_id"], ["paciente.id"], name="fk_consulta_paciente"
        ),
        sa.ForeignKeyConstraint(["medico_id"], ["medico.id"], name="fk_consulta_medico"),
        sa.ForeignKeyConstraint(
            ["horario_disponivel_id"],
            ["horario_disponivel.id"],
            name="fk_consulta_horario",
        ),
    )

    # RN03 - indice PARCIAL. Ver a nota no topo do arquivo e o ADR-006.
    op.create_index(
        "uq_slot_ativo",
        "consulta",
        ["horario_disponivel_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('SOLICITADA', 'CONFIRMADA')"),
    )


def downgrade() -> None:
    op.drop_index("uq_slot_ativo", table_name="consulta")
    op.drop_table("consulta")
    op.drop_table("horario_disponivel")
    op.drop_index("ix_usuario_login", table_name="usuario")
    op.drop_table("usuario")
    op.drop_table("medico")
    op.drop_index("ix_paciente_cpf", table_name="paciente")
    op.drop_table("paciente")
    op.drop_table("especialidade")

    conexao = op.get_bind()
    status_consulta.drop(conexao, checkfirst=True)
    tipo_usuario.drop(conexao, checkfirst=True)
