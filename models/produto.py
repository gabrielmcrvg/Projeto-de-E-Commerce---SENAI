from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from database import Base
from exceptions.erros import EstoqueInsuficienteError, ValorInvalidoError

class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    preco: Mapped[float]
    estoque: Mapped[int]
    descricao: Mapped[str] = mapped_column(default="")
    foto: Mapped[str | None] = mapped_column(default=None)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    categoria: Mapped["Categoria"] = relationship(back_populates="produtos")

    @validates("preco")
    def validar_preco(self, key, valor):
        if not isinstance(valor, (int, float)) or isinstance(valor, bool) or valor < 0:
            raise ValorInvalidoError('Preço deve ser um número (int ou float) maior ou igual a zero.')
        return valor

    @validates("estoque")
    def validar_estoque(self, key, valor):
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
            raise ValorInvalidoError('Estoque deve ser um número inteiro maior ou igual a zero.')
        return valor

    def verificar_disponibilidade(self, quantidade=1):
        return self.estoque >= quantidade

    def dar_baixa_estoque(self, quantidade=1):
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            raise ValorInvalidoError('A quantidade deve ser um número inteiro maior que 0.')

        if not self.verificar_disponibilidade(quantidade):
            raise EstoqueInsuficienteError(
                f'Estoque insuficiente de {self.nome}. Disponível: {self.estoque}, solicitado: {quantidade}.'
            )

        self.estoque -= quantidade

class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    produtos: Mapped[list["Produto"]] = relationship(back_populates="categoria")