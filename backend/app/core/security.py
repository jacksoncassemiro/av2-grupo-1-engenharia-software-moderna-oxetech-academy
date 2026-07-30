"""Hash de senha (RN11 - bcrypt) e emissao/validacao de JWT (RN13 - expiracao)."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha: str) -> str:
    """RN11 - senha nunca e armazenada em texto claro."""
    return _pwd_context.hash(senha)


def senha_confere(senha_plana: str, senha_hash: str) -> bool:
    return _pwd_context.verify(senha_plana, senha_hash)


def criar_token_acesso(subject: str, tipo_usuario: str, paciente_id: int | None = None) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "tipo_usuario": tipo_usuario,
        "paciente_id": paciente_id,
        "exp": expira_em,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Levanta JWTError se o token for invalido ou expirado."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as erro:
        raise JWTError("Token invalido ou expirado") from erro
