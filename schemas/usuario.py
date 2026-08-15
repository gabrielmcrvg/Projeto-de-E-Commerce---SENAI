from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UsuarioEntrada(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
    nome: str = Field(min_length=3)
    email: EmailStr

class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    nome: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str