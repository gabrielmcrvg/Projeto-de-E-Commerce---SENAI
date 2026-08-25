from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from routers import auth, categorias, clientes, produtos, pedidos
from exceptions.excecoes import RecursoNaoEncontrado
from exceptions.erros import LojaError
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title='API - TFU')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

Path("uploads").mkdir(exist_ok=True)
app.mount('/uploads', StaticFiles(directory='uploads'), name='uploads')

app.include_router(produtos.router)
app.include_router(pedidos.router)
app.include_router(clientes.router)
app.include_router(categorias.router)
app.include_router(auth.router)

@app.exception_handler(RecursoNaoEncontrado)
def recurso_nao_encontrado_handler(request: Request, exc: RecursoNaoEncontrado):
    return JSONResponse(status_code=404, content={"detail": f"{exc.recurso} não encontrado(a)"})

@app.exception_handler(LojaError)
def loja_error_handler(request: Request, exc: LojaError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.get('/')
def raiz():
    return RedirectResponse(url='/app')

@app.get('/app')
def frontend():
    return FileResponse('frontend/app.html')

@app.get('/status')
def status():
    return {'status': 'OK', 'Versão': '1.0'}