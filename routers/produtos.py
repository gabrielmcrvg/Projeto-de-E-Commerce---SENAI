from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import selectinload

from database import SessionDep
from dependencias import Paginacao
from exceptions.excecoes import RecursoNaoEncontrado
from models.produto import Categoria, Produto
from schemas.produto import ProdutoEntrada, ProdutoEstoque, ProdutoPatch, ProdutoResposta
from seguranca import AdminAtual, UsuarioAtual
from utils.utils import obter_ou_404

router = APIRouter(prefix='/produtos', tags=['Produtos'])

def validar_categoria(categoria_id: int, session):
    obter_ou_404(session, Categoria, categoria_id, "Categoria")

# =-= GET =-=

@router.get('/listar_produtos', response_model=list[ProdutoResposta])
def listar_produtos(session: SessionDep, usuario: UsuarioAtual, pag: Paginacao = Depends()):
    return session.query(Produto).options(selectinload(Produto.categoria)).offset(pag.skip).limit(pag.limit).all()

@router.get("/estoque", response_model=list[ProdutoEstoque])
def listar_estoque_produtos(session: SessionDep, usuario: AdminAtual, pag: Paginacao = Depends()):
    return session.query(Produto).offset(pag.skip).limit(pag.limit).all()

@router.get('/{produto_id}', response_model=ProdutoResposta)
def buscar_produto(session: SessionDep, produto_id: int, usuario: UsuarioAtual):
    produto = obter_ou_404(session, Produto, produto_id, "Produto")
    return produto

# =-= POST =-=

@router.post('/criar_produto', status_code=status.HTTP_201_CREATED, response_model=ProdutoResposta)
def criar_produto(session: SessionDep, produto: ProdutoEntrada, usuario: AdminAtual):
    validar_categoria(produto.categoria_id, session)
    novo = Produto(**produto.model_dump())
    session.add(novo)
    session.commit()
    session.refresh(novo)
    return novo

# =-= PUT =-=

@router.put('/{produto_id}', response_model=ProdutoResposta)
def atualizar_produto(session: SessionDep, produto_id: int, dados: ProdutoEntrada, usuario: AdminAtual):
    produto = obter_ou_404(session, Produto, produto_id, "Produto")
    validar_categoria(dados.categoria_id, session)
    for campo, valor in dados.model_dump().items():
        setattr(produto, campo, valor)
    session.commit()
    session.refresh(produto)
    return produto

# =-= PATCH =-=

@router.patch('/{produto_id}', response_model=ProdutoResposta)
def alterar_produto(session: SessionDep, produto_id: int, dados: ProdutoPatch, usuario: AdminAtual):
    produto = obter_ou_404(session, Produto, produto_id, "Produto")
    mudancas = dados.model_dump(exclude_unset=True)
    if 'categoria_id' in mudancas:
        validar_categoria(mudancas['categoria_id'], session)
    for campo, valor in mudancas.items():
        setattr(produto, campo, valor)
    session.commit()
    session.refresh(produto)
    return produto

# =-= DELETE =-=

@router.delete('/{produto_id}', status_code=status.HTTP_200_OK)
def remover_produto(session: SessionDep, produto_id: int, usuario: AdminAtual):
    produto = obter_ou_404(session, Produto, produto_id, "Produto")
    session.delete(produto)
    session.commit()
    return {'Mensagem': 'Produto removido'}