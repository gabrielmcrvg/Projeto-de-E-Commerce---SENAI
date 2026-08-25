from datetime import datetime
from decimal import Decimal

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
    preco_unitario: Decimal

class PedidoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    itens: list[ItemPedidoResposta] = Field(validation_alias='itens_pedido')
    valor_total: Decimal
    data_pedido: datetime
    status: str

class PedidoPatch(BaseModel):
    status: str | None = Field(default=None)

class PagamentoEntrada(BaseModel):
    valor_pago: Decimal = Field(gt=0)