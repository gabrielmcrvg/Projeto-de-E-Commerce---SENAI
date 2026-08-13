from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from database import Base

class Usuario(Base, MappedAsDataclass, kw_only=True):
    __abstract__ = True # pra nao criar uma tabela de Usuario

    login: Mapped[str]
    _senha: Mapped[str] = mapped_column(repr=False)  # pra não aparecer a senha se alguem tentar dar print no usuario
    nome: Mapped[str]
    email: Mapped[str] = mapped_column(default='sem@email.com')

    def autenticar(self, sua_senha) -> bool:
        return self._senha == sua_senha

class Administrador(Usuario):
    __tablename__ = "administrador"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    permissao: Mapped[int] = mapped_column(default=1)

class Separador(Usuario):
    __tablename__ = "separador"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    permissao: Mapped[int] = mapped_column(default=2)