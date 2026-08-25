from exceptions.excecoes import RecursoNaoEncontrado


def obter_ou_404(session, model, id, nome: str, options: list = None):
    obj = session.get(model, id, options=options) # options carrega dados relacionados (tipo pedidos de um cliente) junto, sem precisar buscar depois
    if obj is None:
        raise RecursoNaoEncontrado(nome)
    return obj