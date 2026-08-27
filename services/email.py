import os

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType, NameEmail
from pydantic import SecretStr

load_dotenv()

config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=SecretStr(os.getenv("MAIL_PASSWORD", "")),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    TIMEOUT=10,
)

fm = FastMail(config)


async def enviar_confirmacao_cadastro(email: str, nome: str):
    mensagem = MessageSchema(
        subject="Cadastro confirmado",
        recipients=[NameEmail(name=nome, email=email)],
        body=f"<h1>Olá, {nome}!</h1><p>Seu cadastro foi confirmado com sucesso. Já pode entrar na loja e aproveitar!</p>",
        subtype=MessageType.html,
    )
    try:
        await fm.send_message(mensagem)
    except Exception as erro:
        print(f"Falha ao enviar email de confirmacao para {email}: {erro}")
