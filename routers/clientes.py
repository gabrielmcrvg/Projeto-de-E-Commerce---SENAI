from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from database import SessionLocal
from models.cliente import Cliente
from models.pedido import Pedido
from schemas.cliente import ClienteEntrada, ClientePatch, ClienteResposta, PagamentoEntrada
from schemas.pedido import PedidoResposta

router = APIRouter(prefix='/clientes', tags=['Clientes'])

# =-= GET =-=

@router.get('/listar_clientes', response_model=list[ClienteResposta])
def listar_clientes():
    with SessionLocal() as session:
        return session.query(Cliente).options(selectinload(Cliente.pedidos)).all()

@router.get('/{cliente_id}', response_model=ClienteResposta)
def buscar_cliente(cliente_id: int):
    with SessionLocal() as session:
        cliente = session.query(Cliente).options(selectinload(Cliente.pedidos)).filter(Cliente.id == cliente_id).first()
        if cliente is None:
            raise HTTPException(status_code=404, detail='Cliente não encontrado!')
        return cliente

# =-= POST =-=

@router.post('/criar_cliente', status_code=201, response_model=ClienteResposta)
def criar_cliente(dados: ClienteEntrada):
    with SessionLocal() as session:
        novo_cliente = Cliente(login=dados.login, _senha=dados.senha, nome=dados.nome, email=dados.email, telefone_celular=dados.telefone_celular, cpf=dados.cpf, endereco=dados.endereco)
        novo_cliente.validar_cadastro()
        session.add(novo_cliente)
        session.commit()
        cliente_criado = session.query(Cliente).options(selectinload(Cliente.pedidos)).filter(Cliente.id == novo_cliente.id).first()
        return cliente_criado

# =-= PUT =-=

@router.put('/{cliente_id}', response_model=ClienteResposta)
def atualizar_cliente(cliente_id: int, dados: ClienteEntrada):
    with SessionLocal() as session:
        cliente = session.query(Cliente).options(selectinload(Cliente.pedidos)).filter(Cliente.id == cliente_id).first()
        if cliente is None:
            raise HTTPException(status_code=404, detail='Cliente não encontrado!')
        cliente.login = dados.login
        cliente._senha = dados.senha
        cliente.nome = dados.nome
        cliente.email = dados.email
        cliente.telefone_celular = dados.telefone_celular
        cliente.cpf = dados.cpf
        cliente.endereco = dados.endereco
        cliente.validar_cadastro()
        session.commit()
        session.refresh(cliente)
        return cliente

# =-= PATCH =-=

@router.patch('/{cliente_id}', response_model=ClienteResposta)
def alterar_cliente(cliente_id: int, dados: ClientePatch):
    with SessionLocal() as session:
        cliente = session.query(Cliente).options(selectinload(Cliente.pedidos)).filter(Cliente.id == cliente_id).first()
        if cliente is None:
            raise HTTPException(status_code=404, detail='Cliente não encontrado!')
        mudancas = dados.model_dump(exclude_unset=True)
        for campo, valor in mudancas.items():
            setattr(cliente, campo, valor)
        cliente.validar_cadastro()
        session.commit()
        session.refresh(cliente)
        return cliente

# =-= DELETE =-=

@router.delete('/{cliente_id}')
def remover_cliente(cliente_id: int):
    with SessionLocal() as session:
        cliente = session.get(Cliente, cliente_id)
        if cliente is None:
            raise HTTPException(status_code=404, detail='Cliente não encontrado!')
        session.delete(cliente)
        session.commit()
        return {'mensagem': 'Cliente removido'}
    
@router.post('/{cliente_id}/pedidos/{pedido_id}/pagar', response_model=PedidoResposta)
def pagar_pedido(cliente_id: int, pedido_id: int, dados: PagamentoEntrada):
    with SessionLocal() as session:
        cliente = session.get(Cliente, cliente_id)
        if cliente is None:
            raise HTTPException(status_code=404, detail='Cliente não encontrado!')
        pedido = session.query(Pedido).options(selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)).filter(Pedido.id == pedido_id).first()
        if pedido is None:
            raise HTTPException(status_code=404, detail='Pedido não encontrado!')
        cliente.realizar_pagamento(pedido, dados.valor_pago)
        session.commit()
        session.refresh(pedido)
        return pedido