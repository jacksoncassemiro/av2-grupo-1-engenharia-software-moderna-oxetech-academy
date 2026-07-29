from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MedicoCriar(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    email: EmailStr
    crm: str = Field(min_length=4, max_length=20)
    especialidade_id: int


class MedicoResposta(MedicoCriar):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool
