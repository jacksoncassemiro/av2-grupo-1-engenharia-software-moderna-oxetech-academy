"""Guarda de regressao das migracoes Alembic.

Motivacao: o CI ja falhou porque `alembic upgrade head` rodou com SUCESSO sobre uma
pasta `versions/` vazia. Alembic nao reclama quando nao ha revisao nenhuma - ele
simplesmente nao cria nada, e o erro so aparece depois, no seed:

    psycopg.errors.UndefinedTable: relation "usuario" does not exist

Estes testes comparam o esquema declarado nos MODELS com o esquema que a MIGRACAO
realmente produz, sem precisar de banco: a migracao e renderizada em modo offline
(`alembic upgrade head --sql`) e os models sao compilados com um mock engine no
dialeto PostgreSQL.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_mock_engine

from app import models  # noqa: F401  - registra todos os models no metadata
from app.core.database import Base

BACKEND = Path(__file__).resolve().parents[2]
VERSIONS = BACKEND / "alembic" / "versions"

# Colunas nao entram nesta comparacao com o DEFAULT, porque o autogenerate e o
# metadata renderizam `server_default` de formas equivalentes mas nao identicas.
_LIMPAR_DEFAULT = re.compile(r"DEFAULT \S+")
_ESPACOS = re.compile(r"\s+")
_INICIO_DE_CONSTRAINT = ("CONSTRAINT", "PRIMARY KEY", "UNIQUE", "FOREIGN KEY")


def _ddl_dos_models() -> str:
    instrucoes: list[str] = []

    def coletar(sql, *_args, **_kwargs):
        instrucoes.append(str(sql.compile(dialect=motor.dialect)))

    motor = create_mock_engine("postgresql+psycopg://", coletar)
    Base.metadata.create_all(motor)
    return "\n".join(instrucoes)


def _ddl_da_migracao() -> str:
    """Renderiza a migracao em modo offline - nao precisa de banco."""
    processo = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        check=False,
    )
    if processo.returncode != 0:
        pytest.fail(f"alembic upgrade head --sql falhou:\n{processo.stderr}")
    return processo.stdout


def _tabelas(ddl: str) -> dict[str, dict[str, str]]:
    """{tabela: {coluna: 'TIPO NULLABILITY'}} a partir dos CREATE TABLE do DDL."""
    tabelas: dict[str, dict[str, str]] = {}
    for nome, corpo in re.findall(r"CREATE TABLE (\w+) \((.*?)\n\)", ddl, re.S):
        if nome == "alembic_version":
            continue
        colunas: dict[str, str] = {}
        for linha in corpo.split("\n"):
            linha = linha.strip().rstrip(",")
            if not linha or linha.startswith(_INICIO_DE_CONSTRAINT):
                continue
            partes = linha.split(None, 1)
            if len(partes) == 2:
                colunas[partes[0]] = _ESPACOS.sub(" ", _LIMPAR_DEFAULT.sub("", partes[1])).strip()
        tabelas[nome] = colunas
    return tabelas


@pytest.fixture(scope="module")
def ddl_migracao() -> str:
    return _ddl_da_migracao()


@pytest.mark.integration
def test_existe_ao_menos_uma_migracao():
    """Pasta versions/ vazia faz `alembic upgrade head` passar sem criar nada."""
    revisoes = [f for f in VERSIONS.glob("*.py") if not f.name.startswith("__")]
    assert revisoes, (
        "Nenhuma migracao em alembic/versions/. "
        'Rode: make migration m="descricao" e revise o arquivo gerado.'
    )


@pytest.mark.integration
def test_migracao_cria_todas_as_tabelas_dos_models(ddl_migracao):
    """Model novo sem migracao correspondente falha aqui, nao no seed."""
    esperadas = set(Base.metadata.tables)
    criadas = set(_tabelas(ddl_migracao))

    faltando = esperadas - criadas
    assert not faltando, (
        f"Tabelas declaradas nos models mas ausentes na migracao: {sorted(faltando)}"
    )

    sobrando = criadas - esperadas
    assert not sobrando, (
        f"Tabelas criadas pela migracao sem model correspondente: {sorted(sobrando)}"
    )


@pytest.mark.integration
def test_colunas_e_tipos_batem_com_os_models(ddl_migracao):
    models_ddl = _tabelas(_ddl_dos_models())
    migracao_ddl = _tabelas(ddl_migracao)

    divergencias: list[str] = []
    for tabela, colunas in models_ddl.items():
        colunas_migracao = migracao_ddl.get(tabela, {})
        if set(colunas) != set(colunas_migracao):
            divergencias.append(
                f"{tabela}: colunas diferentes -> {sorted(set(colunas) ^ set(colunas_migracao))}"
            )
            continue
        for coluna, tipo in colunas.items():
            if tipo != colunas_migracao[coluna]:
                divergencias.append(
                    f"{tabela}.{coluna}: model='{tipo}' migracao='{colunas_migracao[coluna]}'"
                )

    assert not divergencias, "Migracao divergente dos models:\n  " + "\n  ".join(divergencias)


@pytest.mark.integration
@pytest.mark.parametrize(
    ("regra", "trecho_esperado"),
    [
        ("RN01 - CPF unico", "uq_paciente_cpf UNIQUE (cpf)"),
        ("RN02 - e-mail unico do paciente", "uq_paciente_email UNIQUE (email)"),
        ("RN02 - e-mail unico do medico", "uq_medico_email UNIQUE (email)"),
        ("RN02 - login unico", "uq_usuario_login UNIQUE (login)"),
        ("RN05 - sem alocacao dupla", "UNIQUE (medico_id, data, horario)"),
        ("RN06 - enum de status", "CREATE TYPE status_consulta"),
        ("RN15 - data com fuso", "TIMESTAMP WITH TIME ZONE"),
        ("perfis de acesso", "CREATE TYPE tipo_usuario"),
    ],
)
def test_constraints_das_regras_de_negocio_existem(ddl_migracao, regra, trecho_esperado):
    assert trecho_esperado in ddl_migracao, f"{regra}: falta '{trecho_esperado}' na migracao"


@pytest.mark.integration
def test_indice_do_slot_e_parcial_para_permitir_reagendamento(ddl_migracao):
    """RN03 / ADR-006.

    Um UNIQUE comum em consulta.horario_disponivel_id travaria o slot para sempre
    depois do primeiro cancelamento, quebrando a US-11. O indice tem de ser PARCIAL.
    """
    assert "CREATE UNIQUE INDEX uq_slot_ativo" in ddl_migracao, (
        "Indice uq_slot_ativo ausente - a RN03 fica sem garantia no banco"
    )
    assert "WHERE status IN ('SOLICITADA', 'CONFIRMADA')" in ddl_migracao, (
        "uq_slot_ativo nao e parcial. Sem o WHERE, consultas CANCELADAS continuam "
        "ocupando o indice e o horario nunca pode ser reagendado (US-11)."
    )
    assert "UNIQUE (horario_disponivel_id)" not in ddl_migracao, (
        "Existe UNIQUE simples em horario_disponivel_id. Use apenas o indice parcial."
    )
