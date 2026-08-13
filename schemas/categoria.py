from pydantic import BaseModel, ConfigDict, Field

class CategoriaEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=50)

class CategoriaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str

class CategoriaPatch(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=50)