from sqlalchemy.orm import selectinload

from database import SessionLocal
from models.cliente import Cliente
from models.pedido import Pedido
from models.produto import Categoria, Produto
from models.usuario import Administrador, Separador

session = SessionLocal()

categorias = session.query(Categoria).all()
for c in categorias:
    print(c.id, c.nome)

produtos = session.query(Produto).options(selectinload(Produto.categoria)).all()
for p in produtos:
    print(p.id, p.nome, p.preco, p.categoria_id)

clientes = session.query(Cliente).all()
for c in clientes:
    print(c.id, c.nome, c.email)

pedidos = session.query(Pedido).all()
for p in pedidos:
    print(p.id, p.cliente_id)

admins = session.query(Administrador).all()
for a in admins:
    print(a.id, a.nome, a.login)

separadores = session.query(Separador).all()
for s in separadores:
    print(s.id, s.nome, s.login)

session.close()