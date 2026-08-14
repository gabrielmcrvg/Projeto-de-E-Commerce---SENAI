from fastapi import HTTPException, status
from sqlalchemy import select
from excecoes import RecursoNaoEncontrado


def obter_ou_404(session, model, id, nome: str, options: list = None):
    com_options = select(model).where(model.id == id)
    if options:
        com_options = com_options.options(*options)
    obj = session.exec(com_options).first()
    if obj is None:
        raise RecursoNaoEncontrado(nome)
    return obj

def bad_request(session, model, id, nome:str):
    obj = session.get(model, id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{nome} inexistente")