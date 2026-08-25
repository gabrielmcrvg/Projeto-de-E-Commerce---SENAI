from database import SessionLocal
from models.cliente import Cliente
from models.pedido import ItemPedido, Pedido
from models.produto import Categoria, Produto
from models.usuario import Usuario
from seguranca import gerar_hash

session = SessionLocal()

# =-= Categorias =-=

nomes_categorias = ["Eletrônicos", "Livros", "Roupas", "Casa e Cozinha", "Esportes"]
categorias = []
for nome in nomes_categorias:
    categoria = Categoria(nome=nome)
    session.add(categoria)
    session.commit()
    print(f"Categoria criada! ID: {categoria.id} - {categoria.nome}")
    categorias.append(categoria)

# =-= Produtos =-=

dados_produtos = [
    dict(nome="Notebook Gamer", preco=5000.0, estoque=10, descricao="Notebook para jogos com placa de vídeo dedicada."),
    dict(nome="Dom Casmurro", preco=29.90, estoque=50, descricao="Romance de Machado de Assis."),
    dict(nome="Camiseta Básica", preco=49.90, estoque=100, descricao="Camiseta 100% algodão, várias cores."),
    dict(nome="Panela de Pressão 4,5L", preco=189.90, estoque=30, descricao="Panela de pressão em alumínio polido."),
    dict(nome="Bola de Futebol", preco=89.90, estoque=40, descricao="Bola de futebol de campo, tamanho oficial."),
]
produtos = []
for dados, categoria in zip(dados_produtos, categorias):
    produto = Produto(categoria_id=categoria.id, **dados)
    session.add(produto)
    session.commit()
    print(f"Produto criado! ID: {produto.id} - {produto.nome}")
    produtos.append(produto)

# =-= Clientes =-=

dados_clientes = [
    dict(username="joao_compras", nome="João Silva", email="joao@email.com", cpf="11111111111", telefone_celular="11999998888", endereco="Rua A, 100 - São Paulo, Brasil"),
    dict(username="maria_shop", nome="Maria Souza", email="maria@email.com", cpf="22222222222", telefone_celular="11999997777", endereco="Rua B, 200 - Rio de Janeiro, Brasil"),
    dict(username="pedro_c", nome="Pedro Santos", email="pedro@email.com", cpf="33333333333", telefone_celular="11999996666", endereco="Rua C, 300 - Belo Horizonte, Brasil"),
    dict(username="ana_compras", nome="Ana Oliveira", email="ana@email.com", cpf="44444444444", telefone_celular="11999995555", endereco="Rua D, 400 - Curitiba, Brasil"),
    dict(username="carlos_c", nome="Carlos Pereira", email="carlos@email.com", cpf="55555555555", telefone_celular="11999994444", endereco="Rua E, 500 - Porto Alegre, Brasil"),
]
clientes = []
for dados in dados_clientes:
    cliente = Cliente(hashed_password=gerar_hash("senha123"), **dados)
    session.add(cliente)
    session.commit()
    print(f"Cliente criado! ID: {cliente.id} - {cliente.nome}")
    clientes.append(cliente)

# =-= Usuários internos =-=

admin = Usuario(username="admin_chefe", hashed_password=gerar_hash("admin123"), nome="Gerente Geral", papel="Admin")
session.add(admin)
session.commit()
print(f"Admin criado! ID: {admin.id}")

separador = Usuario(username="separador_ana", hashed_password=gerar_hash("sep123"), nome="Ana Separadora", papel="CLT")
session.add(separador)
session.commit()
print(f"Separador criado! ID: {separador.id}")

# =-= Pedidos =-=
# Cada cliente compra um exemplar do produto de mesmo índice

for cliente, produto in zip(clientes, produtos):
    pedido = Pedido(cliente_id=cliente.id)
    pedido.itens_pedido.append(
        ItemPedido(produto_id=produto.id, quantidade=1, preco_unitario=produto.preco)
    )
    session.add(pedido)
    session.commit()
    print(f"Pedido criado! ID: {pedido.id} - Cliente: {cliente.nome}")

session.close()
print("Dados inseridos com sucesso!")
