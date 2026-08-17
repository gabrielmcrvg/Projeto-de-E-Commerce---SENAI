from fastapi import APIRouter
from sqlalchemy.orm import selectinload

from database import SessionDep
from models.cliente import Cliente
from schemas.cliente import ClienteComPedido, ClienteEntrada, ClientePatch, ClienteResposta
from seguranca import gerar_hash
from utils.utils import obter_ou_404

router = APIRouter(prefix='/clientes', tags=['Clientes'])

# =-= GET =-=

@router.get('/listar_clientes', response_model=list[ClienteResposta])
def listar_clientes(session: SessionDep):
    return session.query(Cliente).options(selectinload(Cliente.pedidos)).all()

@router.get('/{cliente_id}', response_model=ClienteComPedido)
def buscar_cliente(session: SessionDep, cliente_id: int):
    cliente = obter_ou_404(session, Cliente, cliente_id, "Cliente", options=[selectinload(Cliente.pedidos)])
    return cliente

# =-= POST =-=

@router.post('/criar_cliente', status_code=201, response_model=ClienteResposta)
def criar_cliente(session: SessionDep, dados: ClienteEntrada):
    novo_cliente = Cliente(
        username=dados.username,
        hashed_password=gerar_hash(dados.password),
        nome=dados.nome,
        email=dados.email,
        telefone_celular=dados.telefone_celular,
        cpf=dados.cpf,
        endereco=dados.endereco,
    )
    novo_cliente.validar_cadastro()
    session.add(novo_cliente)
    session.commit()
    cliente_criado = obter_ou_404(session, Cliente, novo_cliente.id, "Cliente", options=[selectinload(Cliente.pedidos)])
    return cliente_criado

# =-= PUT =-=

@router.put('/{cliente_id}', response_model=ClienteResposta)
def atualizar_cliente(session: SessionDep, cliente_id: int, dados: ClienteEntrada):
    cliente = obter_ou_404(session, Cliente, cliente_id, "Cliente", options=[selectinload(Cliente.pedidos)])
    for campo, valor in dados.model_dump().items():
        if campo == "password":
            cliente.hashed_password = gerar_hash(valor)
        else:
            setattr(cliente, campo, valor)
    cliente.validar_cadastro()
    session.commit()
    session.refresh(cliente)
    return cliente

# =-= PATCH =-=

@router.patch('/{cliente_id}', response_model=ClienteResposta)
def alterar_cliente(session: SessionDep, cliente_id: int, dados: ClientePatch):
    cliente = obter_ou_404(session, Cliente, cliente_id, "Cliente", options=[selectinload(Cliente.pedidos)])
    mudancas = dados.model_dump(exclude_unset=True)
    for campo, valor in mudancas.items():
        setattr(cliente, campo, valor)
    cliente.validar_cadastro()
    session.commit()
    session.refresh(cliente)
    return cliente

# =-= DELETE =-=

@router.delete('/{cliente_id}')
def remover_cliente(session: SessionDep, cliente_id: int):
    cliente = obter_ou_404(session, Cliente, cliente_id, "Cliente")
    session.delete(cliente)
    session.commit()
    return {'mensagem': 'Cliente removido'}