from fastapi import APIRouter, status
from sqlalchemy.orm import selectinload
from database import SessionLocal
from excecoes import RecursoNaoEncontrado
from models.produto import Produto, Categoria
from schemas.produto import ProdutoEntrada, ProdutoPatch, ProdutoResposta

router = APIRouter(prefix='/produtos', tags=['Produtos'])

def validar_categoria(categoria_id: int, session):
    categoria = session.get(Categoria, categoria_id)
    if categoria is None:
        raise RecursoNaoEncontrado("Categoria")

# =-= GET =-=

@router.get('/listar_produtos', response_model=list[ProdutoResposta])
def listar_produtos():
    with SessionLocal() as session:
        return session.query(Produto).options(selectinload(Produto.categoria)).all()

@router.get('/{produto_id}', response_model=ProdutoResposta)
def buscar_produto(produto_id: int):
    with SessionLocal() as session:
        produto = session.query(Produto).options(selectinload(Produto.categoria)).filter(Produto.id == produto_id).first()
        if produto is None:
            raise RecursoNaoEncontrado("Produto")
        return produto

# =-= POST =-=

@router.post('/criar_produto', status_code=status.HTTP_201_CREATED, response_model=ProdutoResposta)
def criar_produto(produto: ProdutoEntrada):
    with SessionLocal() as session:
        validar_categoria(produto.categoria_id, session)
        novo = Produto(**produto.model_dump())
        session.add(novo)
        session.commit()
        produto_criado = session.query(Produto).options(selectinload(Produto.categoria)).filter(Produto.id == novo.id).first()
        return produto_criado

# =-= PUT =-=

@router.put('/{produto_id}', response_model=ProdutoResposta)
def atualizar_produto(produto_id: int, dados: ProdutoEntrada):
    with SessionLocal() as session:
        produto = session.query(Produto).options(selectinload(Produto.categoria)).filter(Produto.id == produto_id).first()
        if produto is None:
            raise RecursoNaoEncontrado("Produto")        
        validar_categoria(dados.categoria_id, session)
        for campo, valor in dados.model_dump().items():
            setattr(produto, campo, valor)            
        session.commit()
        session.refresh(produto)
        return produto
    
# =-= PATCH =-=

@router.patch('/{produto_id}', response_model=ProdutoResposta)
def alterar_produto(produto_id: int, dados: ProdutoPatch):
    with SessionLocal() as session:
        produto = session.query(Produto).options(selectinload(Produto.categoria)).filter(Produto.id == produto_id).first()
        if produto is None:
            raise RecursoNaoEncontrado("Produto")
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
def remover_produto(produto_id: int):
    with SessionLocal() as session:
        produto = session.get(Produto, produto_id)
        if produto is None:
            raise RecursoNaoEncontrado("Produto")
        session.delete(produto)
        session.commit()
        return {'Mensagem': 'Produto removido'}