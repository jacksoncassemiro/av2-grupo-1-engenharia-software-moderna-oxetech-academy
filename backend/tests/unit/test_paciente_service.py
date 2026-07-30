"""CTU01 e CTU02 - RN01 (CPF unico) e RN02 (e-mail unico)."""

import pytest

from app.exceptions.dominio import CpfDuplicado, EmailDuplicado
from app.models.paciente import Paciente
from app.schemas.paciente_schema import PacienteCriar
from app.services.paciente_service import PacienteService
from tests.conftest import FakePacienteRepository

CPF_VALIDO = "52998224725"
OUTRO_CPF_VALIDO = "11144477735"


def _dados(cpf: str = CPF_VALIDO, email: str | None = "novo@email.com") -> PacienteCriar:
    return PacienteCriar(nome="Joao da Silva", cpf=cpf, telefone="82999990000", email=email)


@pytest.mark.unit
def test_ctu01_deve_bloquear_cadastro_com_cpf_duplicado():
    """RN01 - dois pacientes nao podem compartilhar o mesmo CPF."""
    existente = Paciente(id=1, nome="Carlos", cpf=CPF_VALIDO, telefone="8288887777")
    service = PacienteService(FakePacienteRepository([existente]))

    with pytest.raises(CpfDuplicado) as erro:
        service.cadastrar(_dados(cpf=CPF_VALIDO))

    assert erro.value.status_code == 409
    assert "CPF ja cadastrado" in erro.value.mensagem


@pytest.mark.unit
def test_ctu02_deve_bloquear_cadastro_com_email_duplicado():
    """RN02 - e-mail preenchido precisa ser unico."""
    existente = Paciente(
        id=1,
        nome="Carlos",
        cpf=OUTRO_CPF_VALIDO,
        email="carlos@email.com",
        telefone="8288887777",
    )
    service = PacienteService(FakePacienteRepository([existente]))

    with pytest.raises(EmailDuplicado):
        service.cadastrar(_dados(email="carlos@email.com"))


@pytest.mark.unit
def test_email_nulo_nao_colide_com_outro_email_nulo():
    """RN02 - paciente de balcao pode nao ter e-mail; NULL nao conta como duplicidade."""
    sem_email = Paciente(
        id=1, nome="Carlos", cpf=OUTRO_CPF_VALIDO, email=None, telefone="8288887777"
    )
    service = PacienteService(FakePacienteRepository([sem_email]))

    criado = service.cadastrar(_dados(email=None))

    assert criado.email is None
    assert criado.cpf == CPF_VALIDO
