from database import SessionLocal
from models.cliente import Cliente
from models.produto import Categoria, Produto
from models.usuario import Administrador

session = SessionLocal()

nova_categoria = Categoria(nome="Eletrônicos")
session.add(nova_categoria)
session.commit()
session.refresh(nova_categoria)
print(f"Categoria criada! ID: {nova_categoria.id}")

novo_produto = Produto(nome="Notebook Gamer", preco=5000.0, estoque=10, categoria_id=nova_categoria.id)
session.add(novo_produto)
session.commit()
session.refresh(novo_produto)
print(f"Produto criado! ID: {novo_produto.id}")

novo_cliente = Cliente(login="joao_compras", _senha="senha123", nome="João Silva", email="joao@email.com", cpf="12345678901", telefone_celular="11999998888")
session.add(novo_cliente)
session.commit()
session.refresh(novo_cliente)
print(f"Cliente criado! ID: {novo_cliente.id}")

admin = Administrador(login="admin_chefe", _senha="admin123", nome="Gerente Geral")
session.add(admin)
session.commit()
session.refresh(admin)
print(f"Admin criado! ID: {admin.id}")

session.close()
print("Dados inseridos com sucesso!")