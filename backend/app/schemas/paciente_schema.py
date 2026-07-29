"""DTOs de paciente. A validacao de formato (RN07/RN08) vive aqui, no Pydantic."""

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def apenas_digitos(valor: str) -> str:
    return "".join(c for c in valor if c.isdigit())


def cpf_e_valido(cpf: str) -> bool:
    """RN07 - digitos verificadores do CPF."""
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11 % 10
        if digito != int(cpf[tamanho]):
            return False
    return True


class PacienteBase(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    telefone: str = Field(min_length=10, max_length=20)
    email: EmailStr | None = None
    data_nascimento: date | None = None


class PacienteCriar(PacienteBase):
    cpf: str

    @field_validator("cpf", mode="before")
    @classmethod
    def _validar_cpf(cls, valor: str) -> str:
        cpf = apenas_digitos(str(valor))
        if not cpf_e_valido(cpf):
            raise ValueError("CPF invalido")
        return cpf


class PacienteAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=3, max_length=120)
    telefone: str | None = Field(default=None, min_length=10, max_length=20)
    email: EmailStr | None = None
    data_nascimento: date | None = None


class PacienteResposta(PacienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cpf: str
    ativo: bool
