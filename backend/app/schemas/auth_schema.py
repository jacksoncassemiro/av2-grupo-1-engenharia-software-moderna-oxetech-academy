from pydantic import BaseModel, EmailStr, Field


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
    """Ativa o login de um paciente existente OU faz o auto-cadastro (ADR-005)."""

    cpf: str
    senha: str = Field(min_length=6)
    # Obrigatorios apenas quando o CPF ainda nao existe (auto-cadastro):
    nome: str | None = Field(default=None, min_length=3)
    telefone: str | None = None
    email: EmailStr | None = None
