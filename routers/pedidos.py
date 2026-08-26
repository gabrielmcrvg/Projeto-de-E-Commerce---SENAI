from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload

from database import SessionDep
from dependencias import Paginacao
from models.cliente import Cliente
from models.pedido import ItemPedido, Pedido
from models.produto import Produto
from schemas.pedido import PagamentoEntrada, PedidoEntrada, PedidoPatch, PedidoResposta
from seguranca import AdminAtual, UsuarioAtual
from utils.utils import obter_ou_404


router = APIRouter(prefix='/pedidos', tags=['Pedidos'])


def validar_cliente(cliente_id: int, session):
    obter_ou_404(session, Cliente, cliente_id, "Cliente")


def agregar_itens(itens):
    quantidades_por_produto = defaultdict(int)
    for item in itens:
        quantidades_por_produto[item.produto_id] += item.quantidade
    return quantidades_por_produto


def montar_itens_pedido(session: SessionDep, pedido: Pedido, itens):
    if not itens:
        raise HTTPException(status_code=422, detail="Pedido precisa ter ao menos um item")
    quantidades_por_produto = agregar_itens(itens)
    novos_itens = []
    for produto_id, quantidade in quantidades_por_produto.items():
        produto = obter_ou_404(session, Produto, produto_id, "Produto")
        pedido.validar_novo_item(produto, quantidade)
        novos_itens.append(ItemPedido(produto_id=produto.id, quantidade=quantidade, preco_unitario=produto.preco))
    return novos_itens


@router.get('/listar_pedidos', response_model=list[PedidoResposta])
def listar_pedidos(session: SessionDep, usuario: AdminAtual, pag: Paginacao = Depends()):
    return session.query(Pedido).options(selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)).offset(pag.skip).limit(pag.limit).all()


@router.get('/meus_pedidos', response_model=list[PedidoResposta])
def listar_meus_pedidos(session: SessionDep, usuario: UsuarioAtual, pag: Paginacao = Depends()):
    return session.query(Pedido).filter(Pedido.cliente_id == usuario.id).options(selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)).offset(pag.skip).limit(pag.limit).all()


@router.get('/{pedido_id}', response_model=PedidoResposta)
def buscar_pedido(session: SessionDep, pedido_id: int, usuario: UsuarioAtual):
    pedido = obter_ou_404(session, Pedido, pedido_id, "Pedido", options=[selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)])
    if usuario.papel != "Admin" and pedido.cliente_id != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para ver este pedido.")
    return pedido


@router.post('/criar_pedido', status_code=201, response_model=PedidoResposta)
def criar_pedido(session: SessionDep, dados: PedidoEntrada, usuario: UsuarioAtual):
    validar_cliente(dados.cliente_id, session)
    novo_pedido = Pedido(cliente_id = dados.cliente_id)
    novo_pedido.itens_pedido.extend(montar_itens_pedido(session, novo_pedido, dados.itens))
    session.add(novo_pedido)
    session.commit()
    pedido_criado = obter_ou_404(session, Pedido, novo_pedido.id, "Pedido", options=[selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)])
    return pedido_criado


@router.put('/{pedido_id}', response_model=PedidoResposta)
def atualizar_pedido(session: SessionDep, pedido_id: int, dados: PedidoEntrada, usuario: UsuarioAtual):
    pedido = obter_ou_404(session, Pedido, pedido_id, "Pedido", options=[selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)])
    validar_cliente(dados.cliente_id, session)
    novos_itens = montar_itens_pedido(session, pedido, dados.itens)
    pedido.cliente_id = dados.cliente_id
    pedido.itens_pedido.clear()
    pedido.itens_pedido.extend(novos_itens)
    session.commit()
    session.refresh(pedido)
    return pedido


@router.patch('/{pedido_id}', response_model=PedidoResposta)
def alterar_pedido(session: SessionDep, pedido_id: int, dados: PedidoPatch, usuario: UsuarioAtual):
    pedido = obter_ou_404(session, Pedido, pedido_id, "Pedido", options=[selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)])
    mudancas = dados.model_dump(exclude_unset=True)
    if 'cliente_id' in mudancas:
        validar_cliente(mudancas['cliente_id'], session)
    if mudancas.get('status') == 'Cancelado':
        pedido.cancelar_pedido()
        mudancas.pop('status')
    for campo, valor in mudancas.items():
        setattr(pedido, campo, valor)
    session.commit()
    session.refresh(pedido)
    return pedido


@router.post('/{pedido_id}/pagar', response_model=PedidoResposta)
def pagar_pedido(session: SessionDep, pedido_id: int, dados: PagamentoEntrada, usuario: UsuarioAtual):
    pedido = obter_ou_404(
        session, Pedido, pedido_id, "Pedido",
        options=[selectinload(Pedido.itens_pedido).selectinload(ItemPedido.produto)],
    )
    cliente = session.get(Cliente, usuario.id)
    if cliente is None:
        raise HTTPException(status_code=403, detail="Apenas clientes podem pagar pedidos.")
    try:
        cliente.realizar_pagamento(pedido, dados.valor_pago)
    finally:
        session.commit()
    session.refresh(pedido)
    return pedido


@router.delete('/{pedido_id}')
def remover_pedido(session: SessionDep, pedido_id: int, usuario: AdminAtual):
    pedido = obter_ou_404(session, Pedido, pedido_id, "Pedido")
    session.delete(pedido)
    session.commit()
    return {'mensagem': 'Pedido removido'}