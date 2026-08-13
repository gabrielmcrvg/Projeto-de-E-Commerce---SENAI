from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from database import Base, engine
from routers import categorias, clientes, produtos, pedidos
from excecoes import RecursoNaoEncontrado
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title='API - TFU')

app.include_router(produtos.router)
app.include_router(pedidos.router)
app.include_router(clientes.router)
app.include_router(categorias.router)

@app.exception_handler(RecursoNaoEncontrado)
def recurso_nao_encontrado_handler(request: Request, exc: RecursoNaoEncontrado):
    return JSONResponse(status_code=404, content={"detail": f"{exc.recurso} não encontrado(a)"})

@app.get('')
def raiz():
    return {'Mensagem': 'API do TFU'}

@app.get('/status')
def status():
    return {'status': 'OK', 'Versão': '1.0'}