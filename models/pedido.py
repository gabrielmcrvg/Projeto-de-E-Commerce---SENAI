from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from models.produto import Produto
from exceptions.erros import ValorInvalidoError, ProdutoIndisponivelError, PedidoInvalidoError

class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_pedido: Mapped[datetime] = mapped_column(default=datetime.now)
    status: Mapped[str] = mapped_column(default="Pendente")
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    cliente: Mapped["Cliente"] = relationship(back_populates="pedidos")
    itens_pedido: Mapped[list["ItemPedido"]] = relationship(back_populates="pedido", cascade="all, delete-orphan")

    def validar_novo_item(self, produto: Produto, quantidade: int):
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            raise ValorInvalidoError('A quantidade deve ser um número inteiro maior que 0.')

        if not produto.verificar_disponibilidade(quantidade):
            raise ProdutoIndisponivelError(
                f'Estoque insuficiente de {produto.nome} para atender a quantidade pedida.'
            )

    def cancelar_pedido(self):
        if self.status != 'Pendente':
            raise PedidoInvalidoError(f'Só é possível cancelar pedidos pendentes (status atual: {self.status}).')
        self.status = 'Cancelado'

    @property
    def valor_total(self):
        return sum(item.valor_total for item in self.itens_pedido)

    def __lt__(self, outro_pedido):
        return self.valor_total < outro_pedido.valor_total

    def __repr__(self):
        return f'Pedido #{self.id} - {self.status} - R${self.valor_total:.2f}'

class ItemPedido(Base):
    __tablename__ = "item_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantidade: Mapped[int]
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    pedido: Mapped["Pedido"] = relationship(back_populates="itens_pedido")
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    produto: Mapped["Produto"] = relationship()

    @property
    def valor_total(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f'Você comprou {self.quantidade} itens num valor total de {self.valor_total:.2f}.'

    def __repr__(self):
        return f'{self.quantidade}x {self.produto.nome}'