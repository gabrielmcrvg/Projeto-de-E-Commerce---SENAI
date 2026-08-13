from pydantic import BaseModel, ConfigDict, Field


class ProdutoEntrada(BaseModel):
    nome: str = Field(min_length=4)
    preco: float = Field(gt=0)
    estoque: int = Field(ge=0)
    descricao: str = Field(max_length=200)
    categoria_id: int


class CategoriaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class ProdutoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    preco: float
    estoque: int
    descricao: str
    categoria: CategoriaResposta


class ProdutoPatch(BaseModel):
    nome: str | None = Field(default=None, min_length=4)
    preco: float | None = Field(default=None, gt=0)
    estoque: int | None = Field(default=None, ge=0)
    descricao: str | None = Field(default=None, max_length=200)
    categoria_id: int | None = Field(default=None)