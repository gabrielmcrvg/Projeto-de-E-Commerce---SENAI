from database import Base, SessionLocal, engine
import models.usuario
import models.cliente
import models.produto
import models.pedido
from models.usuario import Usuario
from seguranca import gerar_hash

# Garante que as tabelas existem antes de tentar inserir
Base.metadata.create_all(bind=engine)


def main():
    session = SessionLocal()
    try:
        username = input("Username do admin: ").strip()
        if not username:
            print("Username não pode ser vazio.")
            return

        if session.query(Usuario).filter(Usuario.username == username).first():
            print(f"Já existe um usuário com o username '{username}'.")
            return

        nome = input("Nome completo: ").strip()
        if len(nome) < 3:
            print("O nome precisa ter pelo menos 3 caracteres.")
            return

        email = input("Email (opcional, Enter para pular): ").strip()

        senha = input("Senha (min. 6 caracteres): ")
        if len(senha) < 6:
            print("A senha precisa ter pelo menos 6 caracteres.")
            return

        confirmar = input("Confirme a senha: ")
        if senha != confirmar:
            print("As senhas não coincidem.")
            return

        dados_admin = dict(
            username=username,
            hashed_password=gerar_hash(senha),
            nome=nome,
            papel="Admin",
        )
        if email:
            dados_admin["email"] = email

        admin = Usuario(**dados_admin)
        session.add(admin)
        session.commit()
        print(f"Admin '{username}' criado com sucesso!")
    finally:
        session.close()


if __name__ == "__main__":
    main()
