from database import Base, engine
import models.cliente
import models.pedido
import models.produto
import models.usuario

Base.metadata.create_all(bind=engine)