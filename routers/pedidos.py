from fastapi import APIRouter
from sqlalchemy.orm import selectinload
from database import SessionLocal
from excecoes import RecursoNaoEncontrado
from models.pedido import Pedido, ItemPedido
from models.produto import Produto
from models.cliente import Cliente
from schemas.pedido import PedidoEntrada, PedidoPatch, PedidoResposta

router = APIRouter(prefix='/pedidos', tags=['Pedidos'])

def validar_cliente(cliente_id: int, session):
    cliente = session.get(Cliente, cliente_id)
    if cliente is None:
        raise RecursoNaoEncontrado("Cliente")

# =-= GET =-=

@router.get('/listar_pedidos', response_model=list[PedidoResposta])
def listar_pedidos():
    with SessionLocal() as session:
        return session.query(Pedido).options(selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)).all()

@router.get('/{pedido_id}', response_model=PedidoResposta)
def buscar_pedido(pedido_id: int):
    with SessionLocal() as session:
        pedido = session.query(Pedido).options(selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)).filter(Pedido.id == pedido_id).first()
        if pedido is None:
            raise RecursoNaoEncontrado("Pedido")
        return pedido

# =-= POST =-=

@router.post('/criar_pedido', status_code=201, response_model=PedidoResposta)
def criar_pedido(dados: PedidoEntrada):
    with SessionLocal() as session:
        validar_cliente(dados.cliente_id, session)
        itens_recebidos = dados.itens
        novo_pedido = Pedido(cliente_id=dados.cliente_id)
        for item in itens_recebidos:
            produto = session.get(Produto, item.produto_id)
            if produto is None:
                raise RecursoNaoEncontrado("Produto")
            novo_pedido.validar_novo_item(produto, item.quantidade)
            novo_pedido.itens_pedido.append(ItemPedido(produto_id=produto.id, quantidade=item.quantidade, preco_unitario=produto.preco))
        session.add(novo_pedido)
        session.commit()
        pedido_criado = session.query(Pedido).options(selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)).filter(Pedido.id == novo_pedido.id).first()
        return pedido_criado

# =-= PUT =-=

@router.put('/{pedido_id}', response_model=PedidoResposta)
def atualizar_pedido(pedido_id: int, dados: PedidoEntrada):
    with SessionLocal() as session:
        pedido = session.query(Pedido).options(selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)).filter(Pedido.id == pedido_id).first()
        if pedido is None:
            raise RecursoNaoEncontrado("Pedido")
        validar_cliente(dados.cliente_id, session)
        novos_itens = []
        for item in dados.itens:
            produto = session.get(Produto, item.produto_id)
            if produto is None:
                raise RecursoNaoEncontrado("Produto")
            pedido.validar_novo_item(produto, item.quantidade)
            novos_itens.append(ItemPedido(produto_id=produto.id, quantidade=item.quantidade, preco_unitario=produto.preco))
        pedido.cliente_id = dados.cliente_id
        pedido.itens_pedido.clear()
        pedido.itens_pedido.extend(novos_itens)
        session.commit()
        session.refresh(pedido)
        return pedido

# =-= PATCH =-=

@router.patch('/{pedido_id}', response_model=PedidoResposta)
def alterar_pedido(pedido_id: int, dados: PedidoPatch):
    with SessionLocal() as session:
        pedido = session.query(Pedido).options(selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)).filter(Pedido.id == pedido_id).first()
        if pedido is None:
            raise RecursoNaoEncontrado("Pedido")
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

# =-= DELETE =-=

@router.delete('/{pedido_id}')
def remover_pedido(pedido_id: int):
    with SessionLocal() as session:
        pedido = session.get(Pedido, pedido_id)
        if pedido is None:
            raise RecursoNaoEncontrado("Pedido")
        session.delete(pedido)
        session.commit()
        return {'mensagem': 'Pedido removido'}