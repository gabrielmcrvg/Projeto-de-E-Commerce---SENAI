from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from schemas.pedido import PedidoResposta


class ClienteEntrada(BaseModel):
    login: str = Field(min_length=3)
    senha: str = Field(min_length=6)
    nome: str = Field(min_length=2)
    email: EmailStr
    telefone_celular: str
    cpf: str = Field(min_length=11, max_length=11)
    endereco: str

class ClienteResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    nome: str
    email: str
    telefone_celular: str
    cpf: str
    endereco: str

class ClienteComPedido(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    login: str
    nome: str
    email: str
    telefone_celular: str
    cpf: str
    endereco: str
    pedidos: list[PedidoResposta] = []

class ClientePatch(BaseModel):
    nome: str | None = Field(default=None, min_length=2)
    email: EmailStr | None = Field(default=None)
    telefone_celular: str | None = Field(default=None)
    endereco: str | None = Field(default=None)

class PagamentoEntrada(BaseModel):
    valor_pago: Decimal = Field(gt=0)