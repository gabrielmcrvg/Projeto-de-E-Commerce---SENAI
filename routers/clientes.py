from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload

from database import SessionDep
from models.cliente import Cliente
from models.usuario import Usuario
from schemas.cliente import ClienteComPedido, ClienteEntrada, ClientePatch, ClienteResposta
from seguranca import AdminAtual, UsuarioAtual, gerar_hash
from utils.utils import commitar_ou_lancar, obter_ou_404, verificar_unico

router = APIRouter(prefix='/clientes', tags=['Clientes'])


@router.get('/listar_clientes', response_model=list[ClienteResposta])
def listar_clientes(session: SessionDep, usuario: AdminAtual):
    return session.query(Cliente).options(selectinload(Cliente.pedidos)).all()

@router.get('/eu', response_model=ClienteComPedido)
def eu(session: SessionDep, usuario: UsuarioAtual):
    cliente = session.get(Cliente, usuario.id, options=[selectinload(Cliente.pedidos)])
    if cliente is None:
        raise HTTPException(status_code=403, detail="Apenas clientes possuem perfil de cliente.")
    return cliente

@router.get('/{cliente_id}', response_model=ClienteComPedido)
def buscar_cliente(session: SessionDep, cliente_id: int, usuario: AdminAtual):
    cliente = obter_ou_404(session, Cliente, cliente_id, "Cliente", options=[selectinload(Cliente.pedidos)])
    return cliente


@router.post('/criar_cliente', status_code=201, response_model=ClienteResposta)
def criar_cliente(session: SessionDep, dados: ClienteEntrada):
    verificar_unico(session, Usuario, "username", dados.username, f"O username '{dados.username}' já está em uso.")
    verificar_unico(session, Cliente, "cpf", dados.cpf, f"O CPF {dados.cpf} já está cadastrado.")

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
    commitar_ou_lancar(session, f"CPF {dados.cpf} ou username já cadastrado.")
    cliente_criado = obter_ou_404(session, Cliente, novo_cliente.id, "Cliente", options=[selectinload(Cliente.pedidos)])
    return cliente_criado


@router.put('/{cliente_id}', response_model=ClienteResposta)
def atualizar_cliente(session: SessionDep, cliente_id: int, dados: ClienteEntrada, usuario: AdminAtual):
    cliente = obter_ou_404(session, Cliente, cliente_id, "Cliente", options=[selectinload(Cliente.pedidos)])
    for campo, valor in dados.model_dump().items():
        if campo == "password":
            cliente.hashed_password = gerar_hash(valor)
        else:
            setattr(cliente, campo, valor)
    cliente.validar_cadastro()
    commitar_ou_lancar(session, f"CPF {dados.cpf} ou username já cadastrado.")
    session.refresh(cliente)
    return cliente


@router.patch('/eu', response_model=ClienteResposta)
def alterar_meus_dados(session: SessionDep, dados: ClientePatch, usuario: UsuarioAtual):
    cliente = session.get(Cliente, usuario.id)
    if cliente is None:
        raise HTTPException(status_code=403, detail="Apenas clientes possuem perfil de cliente.")
    mudancas = dados.model_dump(exclude_unset=True)
    for campo, valor in mudancas.items():
        setattr(cliente, campo, valor)
    cliente.validar_cadastro()
    session.commit()
    session.refresh(cliente)
    return cliente


@router.patch('/{cliente_id}', response_model=ClienteResposta)
def alterar_cliente(session: SessionDep, cliente_id: int, dados: ClientePatch, usuario: AdminAtual):
    cliente = obter_ou_404(session, Cliente, cliente_id, "Cliente", options=[selectinload(Cliente.pedidos)])
    mudancas = dados.model_dump(exclude_unset=True)
    for campo, valor in mudancas.items():
        setattr(cliente, campo, valor)
    cliente.validar_cadastro()
    commitar_ou_lancar(session, "CPF ou username já cadastrado.")
    session.refresh(cliente)
    return cliente


@router.delete('/{cliente_id}')
def remover_cliente(session: SessionDep, cliente_id: int, usuario: AdminAtual):
    cliente = obter_ou_404(session, Cliente, cliente_id, "Cliente")
    session.delete(cliente)
    session.commit()
    return {'mensagem': 'Cliente removido'}