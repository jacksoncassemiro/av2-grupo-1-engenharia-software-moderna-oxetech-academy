"""DTOs de paciente. A validacao de formato (RN07/RN08) vive aqui, no Pydantic."""

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def apenas_digitos(valor: str) -> str:
    return "".join(c for c in valor if c.isdigit())


DIGITOS_TELEFONE_VALIDOS = (10, 11)  # fixo com DDD ou celular com DDD


def telefone_e_valido(telefone: str) -> bool:
    """Conta digitos, nao caracteres: '(82) 9999-' tem 10 caracteres e so 6 digitos."""
    return len(apenas_digitos(telefone)) in DIGITOS_TELEFONE_VALIDOS


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

    @field_validator("telefone")
    @classmethod
    def _validar_telefone(cls, valor: str) -> str:
        if not telefone_e_valido(valor):
            raise ValueError("Telefone deve ter DDD e 10 ou 11 digitos")
        return valor


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
    """US-04. `cpf` de proposito nao esta aqui: o CA5 diz que o paciente nao o edita."""

    nome: str | None = Field(default=None, min_length=3, max_length=120)
    telefone: str | None = Field(default=None, min_length=10, max_length=20)
    email: EmailStr | None = None
    data_nascimento: date | None = None

    @field_validator("telefone")
    @classmethod
    def _validar_telefone(cls, valor: str | None) -> str | None:
        if valor is not None and not telefone_e_valido(valor):
            raise ValueError("Telefone deve ter DDD e 10 ou 11 digitos")
        return valor


class PacienteResposta(PacienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cpf: str
    ativo: bool
