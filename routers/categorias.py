from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from database import SessionDep
from dependencias import Paginacao
from models.produto import Categoria
from schemas.categoria import CategoriaEntrada, CategoriaPatch, CategoriaResposta
from utils.utils import obter_ou_404

router = APIRouter(prefix='/categorias', tags=['Categorias'])

# =-= GET =-=

@router.get('/listar_categorias', response_model=list[CategoriaResposta])
def listar_categorias(session: SessionDep, pag: Paginacao = Depends()):
        return session.query(Categoria).options(selectinload(Categoria.produtos)).offset(pag.skip).limit(pag.limit).all()

@router.get('/{categoria_id}', response_model=CategoriaResposta)
def buscar_categoria(session: SessionDep, categoria_id: int):
        categoria = obter_ou_404(session, Categoria, categoria_id, "Categoria", options=[selectinload(Categoria.produtos)])
        return categoria

# =-= POST =-=

@router.post('/criar_categoria', status_code=201, response_model=CategoriaResposta)
def criar_categoria(session: SessionDep, categoria: CategoriaEntrada):
        nova = Categoria(**categoria.model_dump())
        session.add(nova)
        session.commit()
        session.refresh(nova)
        return nova

# =-= PUT =-=

@router.put('/{categoria_id}', response_model=CategoriaResposta)
def atualizar_categoria(session: SessionDep, categoria_id: int, dados: CategoriaEntrada):
        categoria = obter_ou_404(session, Categoria, categoria_id, "Categoria", options=[selectinload(Categoria.produtos)])
        categoria.nome = dados.nome
        session.commit()
        session.refresh(categoria)
        return categoria

# =-= PATCH =-=

@router.patch('/{categoria_id}', response_model=CategoriaResposta)
def alterar_categoria(session: SessionDep, categoria_id: int, dados: CategoriaPatch):
        categoria = obter_ou_404(session, Categoria, categoria_id, "Categoria", options=[selectinload(Categoria.produtos)])
        mudancas = dados.model_dump(exclude_unset=True)
        for campo, valor in mudancas.items():
            setattr(categoria, campo, valor)
        session.commit()
        session.refresh(categoria)
        return categoria

# =-= DELETE =-=

@router.delete('/{categoria_id}')
def remover_categoria(session: SessionDep, categoria_id: int):
        categoria = obter_ou_404(session, Categoria, categoria_id, "Categoria", options=[selectinload(Categoria.produtos)])
        if categoria.produtos:
            raise HTTPException(
                status_code=400,
                detail=f'Não é possível remover: existem {len(categoria.produtos)} produtos vinculados a esta categoria.')
        session.delete(categoria)
        session.commit()
        return {'mensagem': 'Categoria removida'}