from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from database import Base
from seguranca import verificar_senha

class Usuario(MappedAsDataclass, Base, kw_only=True):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    nome: Mapped[str]
    email: Mapped[str] = mapped_column(default='sem@email.com')
    papel: Mapped[str] = mapped_column(default="Comum")

    def autenticar(self, sua_senha: str) -> bool:
        return verificar_senha(sua_senha, self.hashed_password)