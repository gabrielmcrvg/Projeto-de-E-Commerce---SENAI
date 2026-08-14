from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

URL_BANCO = 'sqlite:///ecommerce.db'
engine = create_engine(URL_BANCO, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

SessionDep = Annotated[Session, Depends(get_db)]
