from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from database import SessionDep
from models.cliente import Cliente
from models.usuario import Usuario
from schemas.usuario import Token, UsuarioEntrada, UsuarioResposta
from services.email import enviar_confirmacao_cadastro
from seguranca import AdminAtual, criar_token, gerar_hash, verificar_senha
from utils.utils import obter_ou_404

router = APIRouter(prefix="/usuarios", tags=['Autenticacao'])


@router.get("/listar_usuarios", response_model=list[UsuarioResposta])
def listar_usuarios(session: SessionDep, usuario: AdminAtual):
    return session.query(Usuario).all()


@router.post("/registrar", response_model=UsuarioResposta, status_code=201)
def registrar(dados: UsuarioEntrada, session: SessionDep, tarefas: BackgroundTasks):
    usuario = Usuario(username=dados.username, hashed_password=gerar_hash(dados.password), nome=dados.nome, email=dados.email)
    session.add(usuario)
    session.commit()
    tarefas.add_task(enviar_confirmacao_cadastro, usuario.email, usuario.nome)
    return usuario


@router.post("/token", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    usuario = session.query(Usuario).filter(Usuario.username == form_data.username).first()
    if usuario is None or not verificar_senha(form_data.password, usuario.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario ou senha invalidos", headers={"WWW-Authenticate": "Bearer"})
    token = criar_token({"sub": usuario.username})
    return Token(access_token=token, token_type="bearer")


@router.delete("/{usuario_id}", status_code=204)
def deletar_usuario(usuario_id: int, session: SessionDep, usuario_logado: AdminAtual):
    cliente = session.get(Cliente, usuario_id)
    if cliente is not None:
        session.delete(cliente)
    else:
        usuario = obter_ou_404(session, Usuario, usuario_id, "Usuario")
        session.delete(usuario)
    session.commit()


