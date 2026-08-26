import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError

from exceptions.erros import CPFDuplicadoError
from exceptions.excecoes import RecursoNaoEncontrado


def obter_ou_404(session, model, id, nome: str, options: list = None):
    obj = session.get(model, id, options=options)
    if obj is None:
        raise RecursoNaoEncontrado(nome)
    return obj


def commitar_ou_lancar(session, mensagem: str, excecao=CPFDuplicadoError):
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise excecao(mensagem)


def verificar_unico(session, model, campo: str, valor, mensagem: str, excecao=CPFDuplicadoError):
    coluna = getattr(model, campo)
    if session.query(model).filter(coluna == valor).first():
        raise excecao(mensagem)


def salvar_arquivo_upload(pasta: Path, prefixo: str, arquivo: UploadFile, tipos_permitidos: set, tamanho_maximo: int) -> str:
    if arquivo.content_type not in tipos_permitidos:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido.")
    if arquivo.size is not None and arquivo.size > tamanho_maximo:
        tamanho_mb = tamanho_maximo // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"Arquivo muito grande (máx. {tamanho_mb} MB).")
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome.")

    nome_seguro = Path(arquivo.filename).name
    nome_arquivo = f"{prefixo}_{nome_seguro}"
    destino = pasta / nome_arquivo
    with open(destino, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    return str(destino)
