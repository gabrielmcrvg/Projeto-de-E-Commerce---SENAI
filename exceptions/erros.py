class LojaError(Exception):
    pass


class ValorInvalidoError(LojaError, ValueError):
    pass


class EstoqueInsuficienteError(LojaError):
    pass


class ProdutoIndisponivelError(LojaError):
    pass


class ProdutoNaoEncontradoError(LojaError):
    pass


class ItemNaoEncontradoError(LojaError):
    pass


class PedidoInvalidoError(LojaError):
    pass


class PagamentoInvalidoError(LojaError):
    pass


class PedidoNaoEncontradoError(LojaError):
    pass


class ClienteInvalidoError(ValorInvalidoError):
    pass


class CPFDuplicadoError(ValorInvalidoError):
    pass


class EmailDuplicadoError(ValorInvalidoError):
    pass


class EnderecoInvalidoError(ValorInvalidoError):
    pass