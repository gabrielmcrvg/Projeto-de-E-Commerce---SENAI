from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import selectinload
from database import SessionDep, SessionLocal
from dependencias import Paginacao
from exceptions.excecoes import RecursoNaoEncontrado
from models.produto import Produto, Categoria
from schemas.produto import ProdutoEntrada, ProdutoPatch, ProdutoResposta
from utils.utils import obter_ou_404

router = APIRouter(prefix='/produtos', tags=['Produtos'])

def validar_categoria(categoria_id: int, session):
    categoria = session.get(Categoria, categoria_id)
    if categoria is None:
        raise RecursoNaoEncontrado("Categoria")

# =-= GET =-=

@router.get('/listar_produtos', response_model=list[ProdutoResposta])
def listar_produtos(session: SessionDep, pag: Paginacao = Depends()):
        return session.query(Produto).options(selectinload(Produto.categoria)).offset(pag.skip).limit(pag.limit).all()

@router.get('/{produto_id}', response_model=ProdutoResposta)
def buscar_produto(session: SessionDep, produto_id: int):
        produto = obter_ou_404(session, Produto, produto_id, "Produto")
        return produto

# =-= POST =-=

@router.post('/criar_produto', status_code=status.HTTP_201_CREATED, response_model=ProdutoResposta)
def criar_produto(session: SessionDep, produto: ProdutoEntrada):
        validar_categoria(produto.categoria_id, session)
        novo = Produto(**produto.model_dump())
        session.add(novo)
        session.commit()
        produto_criado = session.query(Produto).options(selectinload(Produto.categoria)).filter(Produto.id == novo.id).first()
        return produto_criado

# =-= PUT =-=

@router.put('/{produto_id}', response_model=ProdutoResposta)
def atualizar_produto(session: SessionDep, produto_id: int, dados: ProdutoEntrada):
        produto = obter_ou_404(session, Produto, produto_id, "Produto")      
        validar_categoria(dados.categoria_id, session)
        for campo, valor in dados.model_dump().items():
            setattr(produto, campo, valor)            
        session.commit()
        session.refresh(produto)
        return produto
    
# =-= PATCH =-=

@router.patch('/{produto_id}', response_model=ProdutoResposta)
def alterar_produto(session: SessionDep, produto_id: int, dados: ProdutoPatch):
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

@router.delete('/{produto_id}')
def remover_produto(session: SessionDep, produto_id: int):
        produto = obter_ou_404(session, Produto, produto_id, "Produto")
        session.delete(produto)
        session.commit()
        return {'Mensagem': 'Produto removido'}