from database import SessionLocal
from models.cliente import Cliente
from models.pedido import ItemPedido, Pedido
from models.produto import Categoria, Produto
from models.usuario import Usuario
from seguranca import gerar_hash

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

novo_cliente = Cliente(
    username="joao_compras",
    hashed_password=gerar_hash("senha123"),
    nome="João Silva",
    email="joao@email.com",
    cpf="12345678901",
    telefone_celular="11999998888",
    endereco="Brasil",
)
session.add(novo_cliente)
session.commit()
session.refresh(novo_cliente)
print(f"Cliente criado! ID: {novo_cliente.id}")

admin = Usuario(username="admin_chefe", hashed_password=gerar_hash("admin123"), nome="Gerente Geral", papel="Admin")
session.add(admin)
session.commit()
session.refresh(admin)
print(f"Admin criado! ID: {admin.id}")

separador = Usuario(username="separador_ana", hashed_password=gerar_hash("sep123"), nome="Ana Separadora", papel="CLT")
session.add(separador)
session.commit()
session.refresh(separador)
print(f"Separador criado! ID: {separador.id}")

novo_pedido = Pedido(cliente_id=novo_cliente.id)
novo_pedido.itens_pedido.append(
    ItemPedido(produto_id=novo_produto.id, quantidade=1, preco_unitario=novo_produto.preco)
)
session.add(novo_pedido)
session.commit()
session.refresh(novo_pedido)
print(f"Pedido criado! ID: {novo_pedido.id}")

session.close()
print("Dados inseridos com sucesso!")