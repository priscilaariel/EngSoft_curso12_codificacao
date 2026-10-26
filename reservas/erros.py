"""Exceções do sistema de reservas."""


class ErroDeValidacao(ValueError):
    """Entrada inválida: dado fora das regras do contrato."""


class ConflitoDeReserva(ErroDeValidacao):
    """A reserva nova conflita com reservas existentes; `conflitos` lista quais."""

    def __init__(self, mensagem: str, conflitos: list):
        super().__init__(mensagem)
        self.conflitos = conflitos
