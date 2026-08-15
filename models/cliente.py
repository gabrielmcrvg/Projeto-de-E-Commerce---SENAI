from decimal import Decimal
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.usuario import Usuario
from exceptions.erros import (
    ClienteInvalidoError,
    EnderecoInvalidoError,
    PagamentoInvalidoError,
    EstoqueInsuficienteError,
)

class Cliente(Usuario):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), primary_key=True, init=False)
    cpf: Mapped[str] = mapped_column(unique=True)
    telefone_celular: Mapped[str] = mapped_column(default="")
    endereco: Mapped[str] = mapped_column(default="")

    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="cliente", default_factory=list, init=False)

    def validar_cadastro(self):
        if not self.email or self.email == 'sem@email.com':
            raise ClienteInvalidoError('Clientes são obrigados a cadastrar um email válido.')

        if "brasil" not in self.endereco.lower():
            raise EnderecoInvalidoError('A entrega é realizada apenas para endereços no Brasil.')

    def __lt__(self, outro_cliente):
        return self.nome < outro_cliente.nome

    def realizar_pagamento(self, pedido, valor_pago):
        if pedido.cliente_id != self.id:
            raise PagamentoInvalidoError('Este pedido não pertence a este cliente.')

        if pedido.status != 'Pendente':
            raise PagamentoInvalidoError(
                f'Só é possível pagar pedidos pendentes (status atual: {pedido.status}).'
            )

        if len(pedido.itens_pedido) == 0:
            raise PagamentoInvalidoError('Pedido sem nenhum item, não é possível pagar.')

        if valor_pago < pedido.valor_total:
            raise PagamentoInvalidoError('Valor pago insuficiente.')

        itens_sem_estoque = [
            item for item in pedido.itens_pedido
            if not item.produto.verificar_disponibilidade(item.quantidade)
        ]

        if itens_sem_estoque:
            pedido.status = 'Cancelado'
            nomes = ', '.join(item.produto.nome for item in itens_sem_estoque)
            raise EstoqueInsuficienteError(
                f'Pedido cancelado: estoque insuficiente para {nomes}.'
            )

        pedido.status = 'Pago'

        for item in pedido.itens_pedido:
            item.produto.dar_baixa_estoque(item.quantidade)

        return pedido