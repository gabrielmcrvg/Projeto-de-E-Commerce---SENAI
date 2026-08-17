from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from database import Base
from seguranca import verificar_senha

class Usuario(MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    nome: Mapped[str]
    email: Mapped[str] = mapped_column(default='sem@email.com')

    def autenticar(self, sua_senha: str) -> bool:
        return verificar_senha(sua_senha, self.hashed_password)

class Administrador(Usuario):
    __tablename__ = "administrador"

    id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), primary_key=True, init=False)
    permissao: Mapped[int] = mapped_column(default=1)

class Separador(Usuario):
    __tablename__ = "separador"

    id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), primary_key=True, init=False)
    permissao: Mapped[int] = mapped_column(default=2)