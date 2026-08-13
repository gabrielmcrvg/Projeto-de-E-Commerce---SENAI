from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ItemPedidoEntrada(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)

class PedidoEntrada(BaseModel):
    cliente_id: int
    itens: list[ItemPedidoEntrada]
    data_pedido: datetime = Field(default_factory=datetime.now)
    status: str = Field(default='pendente')

class ItemPedidoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    quantidade: int

class PedidoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    itens: list[ItemPedidoResposta] = Field(validation_alias='itens_pedido')
    data_pedido: datetime
    status: str

class ItemPedidoPatch(BaseModel):
    produto_id: int | None = Field(default=None)
    quantidade: int | None = Field(default=None, gt=0)

class PedidoPatch(BaseModel):
    status: str | None = Field(default=None)