from pydantic import BaseModel, ConfigDict, Field


class EspecialidadeCriar(BaseModel):
    nome: str = Field(min_length=3, max_length=80)
    descricao: str | None = None


class EspecialidadeResposta(EspecialidadeCriar):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool
