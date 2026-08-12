"""Configuracao central da aplicacao (12-factor: tudo via variavel de ambiente)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Aplicacao ---
    APP_NAME: str = "Sistema de Gestao de Clinica Medica (MVP)"
    APP_ENV: str = "development"
    API_PREFIX: str = "/api"

    # --- Banco de dados ---
    DATABASE_URL: str = "postgresql+psycopg://clinica:clinica@localhost:5432/clinica_db"

    # --- Seguranca / JWT ---
    JWT_SECRET_KEY: str = "troque-esta-chave-em-producao"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24h (RN13)

    # --- Regras de negocio parametrizaveis ---
    # RN04 - nome unico da antecedencia minima de cancelamento. E a mesma variavel
    # publicada no .env.example e no docker-compose: baixar para 0 tem de afetar
    # tanto a validacao do ConsultaService quanto o `pode_cancelar` da resposta.
    CANCELAMENTO_ANTECEDENCIA_HORAS: int = 24
    TIMEZONE: str = "America/Maceio"  # RN15 - fuso de referencia das regras temporais

    # --- Bootstrap do primeiro atendente (RN14 / ADR-004) ---
    SEED_ATENDENTE_NOME: str = "Atendente Padrao"
    SEED_ATENDENTE_LOGIN: str = "recepcao@clinica.com"
    SEED_ATENDENTE_SENHA: str = "admin123"

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
