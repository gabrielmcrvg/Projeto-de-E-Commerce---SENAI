from fastapi import APIRouter, Depends
from sqlalchemy.orm import selectinload

from database import SessionDep
from dependencias import Paginacao
from models.cliente import Cliente
from models.pedido import ItemPedido, Pedido
from models.produto import Produto
from schemas.pedido import PedidoEntrada, PedidoPatch, PedidoResposta
from utils.utils import obter_ou_404

router = APIRouter(prefix='/pedidos', tags=['Pedidos'])

def validar_cliente(cliente_id: int, session):
    obter_ou_404(session, Cliente, cliente_id, "Cliente")

# =-= GET =-=

@router.get('/listar_pedidos', response_model=list[PedidoResposta])
def listar_pedidos(session: SessionDep, pag: Paginacao = Depends()):
        return session.query(Pedido).options(selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)).offset(pag.skip).limit(pag.limit).all()

@router.get('/{pedido_id}', response_model=PedidoResposta)
def buscar_pedido(session: SessionDep, pedido_id: int):
        pedido = obter_ou_404(session, Pedido, pedido_id, "Pedido", options=[selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)])
        return pedido

# =-= POST =-=

@router.post('/criar_pedido', status_code=201, response_model=PedidoResposta)
def criar_pedido(session: SessionDep, dados: PedidoEntrada):
        validar_cliente(dados.cliente_id, session)
        itens_recebidos = dados.itens
        novo_pedido = Pedido(cliente_id=dados.cliente_id)
        for item in itens_recebidos:
            produto = obter_ou_404(session, Produto, item.produto_id, "Produto")
            novo_pedido.validar_novo_item(produto, item.quantidade)
            novo_pedido.itens_pedido.append(ItemPedido(produto_id=produto.id, quantidade=item.quantidade, preco_unitario=produto.preco))
        session.add(novo_pedido)
        session.commit()
        pedido_criado = obter_ou_404(session, Pedido, novo_pedido.id, "Pedido", options=[selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)])
        return pedido_criado

# =-= PUT =-=

@router.put('/{pedido_id}', response_model=PedidoResposta)
def atualizar_pedido(session: SessionDep, pedido_id: int, dados: PedidoEntrada):
        pedido = obter_ou_404(session, Pedido, pedido_id, "Pedido", options=[selectinload(Pedido.cliente), selectinload(Pedido.itens_pedido)])
        validar_cliente(dados.cliente_id, session)
        novos_itens = []
        for item in dados.itens:
            produto = obter_ou_404(session, Produto, item.produto_id, "Produto")
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
def alterar_pedido(session: SessionDep, pedido_id: int, dados: PedidoPatch):
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

# =-= DELETE =-=

@router.delete('/{pedido_id}')
def remover_pedido(session: SessionDep, pedido_id: int):
        pedido = obter_ou_404(session, Pedido, pedido_id, "Pedido")
        session.delete(pedido)
        session.commit()
        return {'mensagem': 'Pedido removido'}