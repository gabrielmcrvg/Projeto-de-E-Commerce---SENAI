from fastapi import HTTPException, status
from sqlalchemy import select

from exceptions.excecoes import RecursoNaoEncontrado


def obter_ou_404(session, model, id, nome: str, options: list = None):
    consulta = select(model).where(model.id == id)
    if options:
        consulta = consulta.options(*options) # traz os dados relacionados (tipo pedidos de um cliente) junto, sem precisar buscar depois
    obj = session.execute(consulta).scalars().first()
    if obj is None:
        raise RecursoNaoEncontrado(nome)
    return obj

def bad_request(session, model, id, nome:str):
    obj = session.get(model, id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{nome} inexistente")