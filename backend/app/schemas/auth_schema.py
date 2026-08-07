from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.paciente_schema import apenas_digitos, cpf_e_valido


class LoginRequisicao(BaseModel):
    """US-00 - campo unico: CPF ou e-mail."""

    login: str = Field(min_length=3, examples=["12345678909", "recepcao@clinica.com"])
    senha: str = Field(min_length=6)


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tipo_usuario: str


class VerificarCpfResposta(BaseModel):
    cadastro_existe: bool
    login_ativo: bool
    nome: str | None


class PrimeiroAcesso(BaseModel):
    """Ativa o login de um paciente existente OU faz o auto-cadastro (ADR-005).

    Este e o unico caminho publico que cria `paciente`, entao precisa das mesmas
    validacoes de formato de `PacienteCriar`: RN07 no CPF e o mesmo minimo de
    telefone. Sem isso a RN01 aceitaria `00000000000` pela porta dos fundos.
    """

    cpf: str
    senha: str = Field(min_length=6)
    # Obrigatorios apenas quando o CPF ainda nao existe (auto-cadastro):
    nome: str | None = Field(default=None, min_length=3, max_length=120)
    telefone: str | None = Field(default=None, min_length=10, max_length=20)
    email: EmailStr | None = None

    @field_validator("cpf", mode="before")
    @classmethod
    def _validar_cpf(cls, valor: str) -> str:
        """RN07 - digitos verificadores, mesma regra da US-03."""
        cpf = apenas_digitos(str(valor))
        if not cpf_e_valido(cpf):
            raise ValueError("CPF invalido")
        return cpf
