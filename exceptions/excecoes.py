class RecursoNaoEncontrado(Exception):
    def __init__(self, recurso: str):
        self.recurso = recurso
        super().__init__(f"{recurso} não encontrado(a)")