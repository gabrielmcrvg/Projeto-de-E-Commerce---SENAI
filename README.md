# Projeto de E-Commerce — SENAI (em desenvolvimento)

API REST para um sistema de e-commerce, desenvolvida em Python com **FastAPI** como projeto final de conclusão do curso técnico de desenvolvimento de sistemas no SENAI.

> ✅ **Autenticação e permissões implementadas.** Todas as rotas exigem um token JWT válido (obtido em `/usuarios/token`), com exceção do registro de usuário/cliente e do próprio login. Rotas administrativas exigem que o usuário logado tenha o papel `Admin`; um cliente autenticado também consegue ver os próprios dados (`/clientes/eu`) e os próprios pedidos (`/pedidos/meus_pedidos`) — veja a coluna **Acesso** nas tabelas de endpoints abaixo.
>
> **Limitação conhecida:** o cliente já consegue ver e editar (`nome`, `email`, `telefone_celular`, `endereco`) os próprios dados, mas trocar `username`, `password` ou `cpf` ainda exige um Admin — não há rota de autoatendimento pra isso.

## 📋 Sobre o projeto

A aplicação expõe endpoints para gerenciar produtos, categorias, clientes e pedidos de uma loja virtual, com autenticação de usuários via JWT. Os dados são persistidos em um banco SQLite, usando SQLAlchemy como ORM.

## 🛠️ Tecnologias utilizadas

- **[FastAPI](https://fastapi.tiangolo.com/)** — framework web para construção da API
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM para modelagem e acesso ao banco de dados
- **SQLite** — banco de dados relacional (`ecommerce.db`)
- **[Pydantic](https://docs.pydantic.dev/)** — validação de dados e schemas
- **PyJWT** — geração e validação de tokens de autenticação
- **argon2-cffi / pwdlib** — hashing seguro de senhas
- **Uvicorn** — servidor ASGI para execução da aplicação
- **python-dotenv** — carregamento de variáveis de ambiente

## 📁 Estrutura do projeto

```
├── exceptions/          # Exceções customizadas
│   ├── erros.py             # Hierarquia de exceções de domínio (LojaError e subclasses)
│   └── excecoes.py          # RecursoNaoEncontrado, usada pelo obter_ou_404
├── models/              # Modelos SQLAlchemy: Usuario (com papel), Cliente, Categoria, Produto, Pedido, ItemPedido
├── routers/              # Rotas da API
│   ├── auth.py               # /usuarios — registro, login/token, listagem
│   ├── categorias.py         # /categorias — CRUD de categorias
│   ├── produtos.py           # /produtos  — CRUD de produtos
│   ├── clientes.py           # /clientes  — CRUD de clientes
│   └── pedidos.py            # /pedidos   — CRUD de pedidos
├── schemas/              # Schemas Pydantic (validação de entrada/saída)
├── services/              # Regras de negócio da aplicação
├── consultar.py            # Script auxiliar para consultas no banco
├── criar_admin.py          # Script para criar o primeiro usuário Admin (obrigatório)
├── database.py              # Configuração da conexão com o banco de dados (SessionDep, engine, Base)
├── dependencias.py           # Dependências reutilizáveis (ex: paginação)
├── inserir.py                  # Script auxiliar para inserção de dados de teste
├── main.py                      # Ponto de entrada da aplicação FastAPI
├── seguranca.py                  # Hash de senha, verificação de senha e geração de token JWT
├── utils/                         # Funções utilitárias (ex: obter_ou_404, validar_produto, validar_categoria)
└── requirements.txt                # Dependências do projeto
```

## 🚀 Como executar o projeto

### Pré-requisitos

- Python 3.10 ou superior

### Passo a passo

1. Clone o repositório:
   ```bash
   git clone https://github.com/gabrielmcrvg/Projeto-de-E-Commerce---SENAI.git
   cd Projeto-de-E-Commerce---SENAI
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` na raiz do projeto com a chave usada para assinar os tokens JWT:
   ```
   SECRET_KEY=uma_chave_secreta_qualquer
   ```

5. Crie o banco e o primeiro usuário Admin (obrigatório — sem ele não há como acessar nenhuma rota administrativa):
   ```bash
   py criar_admin.py
   ```

6. (Opcional) Popule o banco com dados de teste:
   ```bash
   py inserir.py
   ```

7. Execute a aplicação:
   ```bash
   uvicorn main:app --reload
   ```

8. Acesse a documentação interativa da API (gerada automaticamente pelo FastAPI):
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔌 Endpoints da API

A API é organizada em routers, cada um responsável por um recurso. Todos retornam e recebem JSON.

### 🔑 Usuários / Autenticação — `/usuarios`

| Método | Rota                       | Descrição                                                  | Acesso |
|--------|-----------------------------|----------------------------------------------------------------|--------|
| GET    | `/usuarios/listar_usuarios` | Lista todos os usuários cadastrados                          | Admin |
| POST   | `/usuarios/registrar`       | Cria um novo usuário (senha é armazenada com hash)            | Público |
| POST   | `/usuarios/token`           | Autentica (`username` + `password`, formulário OAuth2) e retorna um token JWT (`access_token`, `token_type`) | Público |
| DELETE | `/usuarios/{usuario_id}`    | Remove um usuário                                             | Admin |

**Corpo de `/registrar`** (`UsuarioEntrada`): `username` (mín. 3), `password` (mín. 6), `nome` (mín. 3), `email` (formato válido).
**Resposta** (`UsuarioResposta`): `id`, `username`, `nome`, `email` — a senha nunca é retornada.

### 🏷️ Categorias — `/categorias`

| Método | Rota                          | Descrição                                                                 | Acesso |
|--------|--------------------------------|--------------------------------------------------------------------------------|--------|
| GET    | `/categorias/listar_categorias`| Lista categorias (com seus produtos vinculados), com paginação               | Autenticado |
| GET    | `/categorias/{categoria_id}`  | Busca uma categoria específica                                              | Autenticado |
| POST   | `/categorias/criar_categoria` | Cria uma nova categoria                                                     | Admin |
| PUT    | `/categorias/{categoria_id}`  | Atualiza o nome da categoria (substituição completa)                       | Admin |
| PATCH  | `/categorias/{categoria_id}`  | Atualiza parcialmente os dados da categoria                                | Admin |
| DELETE | `/categorias/{categoria_id}`  | Remove uma categoria — bloqueado (`400`) se houver produtos vinculados a ela | Admin |

### 📦 Produtos — `/produtos`

| Método | Rota                        | Descrição                                             | Acesso |
|--------|------------------------------|--------------------------------------------------------------|--------|
| GET    | `/produtos/listar_produtos` | Lista produtos (com dados da categoria), com paginação   | Autenticado |
| GET    | `/produtos/estoque`         | Lista produtos com foco em `id`, `nome` e `estoque`       | Admin |
| GET    | `/produtos/{produto_id}`    | Busca um produto específico                              | Autenticado |
| POST   | `/produtos/criar_produto`   | Cria um novo produto (valida se `categoria_id` existe)    | Admin |
| PUT    | `/produtos/{produto_id}`    | Atualiza um produto (substituição completa)               | Admin |
| PATCH  | `/produtos/{produto_id}`    | Atualiza parcialmente um produto                          | Admin |
| DELETE | `/produtos/{produto_id}`    | Remove um produto                                          | Admin |

**Corpo de criação/atualização** (`ProdutoEntrada`): `nome` (mín. 4), `preco` (> 0), `estoque` (≥ 0), `descricao` (máx. 200 caracteres), `categoria_id`.
**Resposta** (`ProdutoResposta`): `id`, `nome`, `preco`, `estoque`, `descricao`, `categoria` (objeto com `id` e `nome`).

### 👤 Clientes — `/clientes`

| Método | Rota                                              | Descrição                                                          | Acesso |
|--------|----------------------------------------------------|--------------------------------------------------------------------------|--------|
| GET    | `/clientes/listar_clientes`                        | Lista clientes (com seus pedidos)                                      | Admin |
| GET    | `/clientes/eu`                                     | Retorna os dados do cliente autenticado, incluindo seus pedidos        | Autenticado |
| PATCH  | `/clientes/eu`                                     | Atualiza parcialmente os próprios dados (`nome`, `email`, `telefone_celular`, `endereco`) | Autenticado |
| GET    | `/clientes/{cliente_id}`                           | Busca um cliente específico, incluindo seus pedidos                    | Admin |
| POST   | `/clientes/criar_cliente`                          | Cria um novo cliente                                                    | Público |
| PUT    | `/clientes/{cliente_id}`                           | Atualiza um cliente (substituição completa)                            | Admin |
| PATCH  | `/clientes/{cliente_id}`                           | Atualiza parcialmente os dados do cliente                              | Admin |
| DELETE | `/clientes/{cliente_id}`                           | Remove um cliente                                                       | Admin |

**Corpo de criação/atualização** (`ClienteEntrada`): `username` (mín. 3), `password` (mín. 6), `nome` (mín. 2), `email`, `telefone_celular`, `cpf` (exatamente 11 caracteres), `endereco`.
**Resposta** (`ClienteResposta`): `id`, `username`, `nome`, `email`, `telefone_celular`, `cpf`, `endereco`. Ao buscar um cliente específico, a resposta (`ClienteComPedido`) inclui também a lista de `pedidos`.
**PATCH** (`ClientePatch`): todos os campos são opcionais (`nome`, `email`, `telefone_celular`, `endereco` — `username` e `password` não são alteráveis por aqui).

> Se `cpf` ou `username` já estiverem cadastrados em outro usuário, a API responde `400` com uma mensagem indicando o conflito, em vez de um erro genérico.

### 🧾 Pedidos — `/pedidos`

| Método | Rota                       | Descrição                                                                                    | Acesso |
|--------|-----------------------------|------------------------------------------------------------------------------------------------------|--------|
| GET    | `/pedidos/listar_pedidos`  | Lista pedidos (com cliente e itens), com paginação                                               | Admin |
| GET    | `/pedidos/meus_pedidos`    | Lista os pedidos do cliente autenticado                                                          | Autenticado |
| GET    | `/pedidos/{pedido_id}`     | Busca um pedido específico                                                                       | Autenticado (dono do pedido, ou Admin) |
| POST   | `/pedidos/criar_pedido`    | Cria um novo pedido para um cliente (`cliente_id` + lista de `itens`: `produto_id` e `quantidade`)| Autenticado |
| PUT    | `/pedidos/{pedido_id}`     | Atualiza um pedido (substitui cliente e reconstrói a lista de itens)                             | Autenticado |
| PATCH  | `/pedidos/{pedido_id}`     | Atualiza parcialmente um pedido; se `status` for `"Cancelado"`, aciona a lógica de cancelamento   | Autenticado |
| POST   | `/pedidos/{pedido_id}/pagar` | Paga um pedido pendente (`valor_pago`); debita estoque e marca como `Pago`, ou cancela o pedido se faltar estoque | Autenticado (dono do pedido) |
| DELETE | `/pedidos/{pedido_id}`     | Remove um pedido                                                                                  | Admin |

**Corpo de criação/atualização** (`PedidoEntrada`): `cliente_id`, `itens` (lista de `{ produto_id, quantidade }`, com `quantidade > 0`). Itens repetidos com o mesmo `produto_id` são somados antes da validação de estoque.
**Resposta** (`PedidoResposta`): `id`, `cliente_id`, `itens` (lista de `{ id, produto_id, quantidade }`), `data_pedido`, `status`.
**PATCH** (`PedidoPatch`): apenas `status` é alterável (ex.: `"Cancelado"`, o que aciona a validação de cancelamento do pedido).

### ⚙️ Status — `/status`

| Método | Rota      | Descrição                        | Acesso |
|--------|-----------|-----------------------------------|--------|
| GET    | `/status` | Retorna o status e versão da API | Público |

> Consulte `/docs` (Swagger) após executar a aplicação para ver os schemas completos de cada requisição/resposta.

## 🗂️ Modelo de dados

### Usuario (classe base)

Tabela `usuarios`. Campos: `id`, `username` (único), `hashed_password`, `nome`, `email`, `papel` (texto livre, default `"Comum"`). É essa entidade base que o endpoint `/usuarios/registrar` cria.

O `papel` identifica o tipo de usuário: `"Admin"` (administrador), `"CLT"` (separador/funcionário) ou `"Comum"` (padrão, usado também pelos clientes). Não há tabelas nem classes separadas por papel — é só esse campo na própria tabela `usuarios`.

A partir da classe base deriva um tipo de usuário com tabela própria (*joined table inheritance*):

- **Cliente** — o único tipo exposto via API própria (`/clientes`), com campos adicionais: `cpf` (único), `telefone_celular`, `endereco`, e relação com seus `pedidos`.

**Regras de negócio do Cliente:**
- `validar_cadastro()` exige um e-mail válido (diferente do padrão `sem@email.com`) e um endereço que contenha "Brasil" (a entrega é feita apenas para o Brasil).
- `realizar_pagamento(pedido, valor_pago)` valida que o pedido pertence ao cliente, que está com status `Pendente`, que possui itens, que o valor pago cobre o total e que há estoque disponível para todos os itens — do contrário, cancela o pedido automaticamente por falta de estoque. Exposto pela rota `POST /pedidos/{pedido_id}/pagar`.

### Categoria e Produto

- **Categoria**: `id`, `nome`, relação com seus `produtos`.
- **Produto**: `id`, `nome`, `preco`, `estoque`, `descricao`, vinculado a uma `Categoria`.
  - Validações: `preco` e `estoque` devem ser números não negativos.
  - Métodos: `verificar_disponibilidade(quantidade)` e `dar_baixa_estoque(quantidade)` (usado ao confirmar pagamento de um pedido).

### Pedido e ItemPedido

- **Pedido**: `id`, `data_pedido`, `status` (`Pendente`, `Pago` ou `Cancelado`), vinculado a um `Cliente` e a uma lista de `itens_pedido`.
  - `valor_total` é calculado dinamicamente a partir dos itens.
  - `validar_novo_item(produto, quantidade)` garante quantidade inteira positiva e estoque suficiente.
  - `cancelar_pedido()` só permite cancelamento de pedidos com status `Pendente`.
- **ItemPedido**: `id`, `quantidade`, `preco_unitario` (congelado no momento da compra), vinculado a um `Pedido` e a um `Produto`.

## ⚠️ Tratamento de erros

Toda a árvore de exceções de domínio herda de `LojaError`, capturada por um handler genérico que responde `400` com a mensagem do erro. Além dela, `RecursoNaoEncontrado` tem handler próprio, retornando `404`. Entre as exceções de domínio:

- `ClienteInvalidoError` / `EnderecoInvalidoError` — dados de cadastro do cliente inválidos
- `CPFDuplicadoError` — CPF ou username já cadastrados em outro usuário
- `PagamentoInvalidoError` — pedido não pertence ao cliente, já foi pago/cancelado, ou valor pago é insuficiente
- `EstoqueInsuficienteError` — estoque insuficiente para concluir a operação
- `ProdutoIndisponivelError` — produto descontinuado ou indisponível para venda
- `ValorInvalidoError` — valores numéricos inválidos (preço, estoque, quantidade)
- `PedidoInvalidoError` — operação não permitida para o status atual do pedido

## 👤 Autor

Desenvolvido por [Gabriel Merçon](https://github.com/gabrielmcrvg) como Trabalho Final de Unidade (TFU) no SENAI.