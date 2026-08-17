from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class ItemPedidoEntrada(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)

class PedidoEntrada(BaseModel):
    cliente_id: int
    itens: list[ItemPedidoEntrada]

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