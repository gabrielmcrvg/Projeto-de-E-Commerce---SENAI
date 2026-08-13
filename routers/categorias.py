from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from database import SessionLocal
from models.produto import Categoria
from schemas.categoria import CategoriaEntrada, CategoriaPatch, CategoriaResposta

router = APIRouter(prefix='/categorias', tags=['Categorias'])

# =-= GET =-=

@router.get('/listar_categorias', response_model=list[CategoriaResposta])
def listar_categorias():
    with SessionLocal() as session:
        return session.query(Categoria).options(selectinload(Categoria.produtos)).all()

@router.get('/{categoria_id}', response_model=CategoriaResposta)
def buscar_categoria(categoria_id: int):
    with SessionLocal() as session:
        categoria = session.query(Categoria).options(selectinload(Categoria.produtos)).filter(Categoria.id == categoria_id).first()
        if categoria is None:
            raise HTTPException(status_code=404, detail='Categoria não encontrada!')
        return categoria

# =-= POST =-=

@router.post('/criar_categoria', status_code=201, response_model=CategoriaResposta)
def criar_categoria(categoria: CategoriaEntrada):
    with SessionLocal() as session:
        nova = Categoria(**categoria.model_dump())
        session.add(nova)
        session.commit()
        session.refresh(nova)
        return nova

# =-= PUT =-=

@router.put('/{categoria_id}', response_model=CategoriaResposta)
def atualizar_categoria(categoria_id: int, dados: CategoriaEntrada):
    with SessionLocal() as session:
        categoria = session.query(Categoria).options(selectinload(Categoria.produtos)).filter(Categoria.id == categoria_id).first()
        if categoria is None:
            raise HTTPException(status_code=404, detail='Categoria não encontrada!')
        categoria.nome = dados.nome
        session.commit()
        session.refresh(categoria)
        return categoria

# =-= PATCH =-=

@router.patch('/{categoria_id}', response_model=CategoriaResposta)
def alterar_categoria(categoria_id: int, dados: CategoriaPatch):
    with SessionLocal() as session:
        categoria = session.query(Categoria).options(selectinload(Categoria.produtos)).filter(Categoria.id == categoria_id).first()
        if categoria is None:
            raise HTTPException(status_code=404, detail='Categoria não encontrada!')
        mudancas = dados.model_dump(exclude_unset=True)
        for campo, valor in mudancas.items():
            setattr(categoria, campo, valor)
        session.commit()
        session.refresh(categoria)
        return categoria

# =-= DELETE =-=

@router.delete('/{categoria_id}')
def remover_categoria(categoria_id: int):
    with SessionLocal() as session:
        categoria = session.query(Categoria).options(selectinload(Categoria.produtos)).filter(Categoria.id == categoria_id).first()
        if categoria is None:
            raise HTTPException(status_code=404, detail='Categoria não encontrada!')
        if categoria.produtos:
            raise HTTPException(
                status_code=400,
                detail=f'Não é possível remover: existem {len(categoria.produtos)} produtos vinculados a esta categoria.')
        session.delete(categoria)
        session.commit()
        return {'mensagem': 'Categoria removida'}