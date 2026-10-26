"""Leitura de reservas a partir de dados JSON."""
from pathlib import Path

from reservas.reserva import Reserva


def ler_reserva(dados: dict) -> Reserva:
    """Converte um objeto JSON com sala, dia, inicio e fim em uma Reserva válida."""
    raise NotImplementedError("ler_reserva ainda não implementada")


def ler_arquivo(caminho: str | Path) -> tuple[Reserva, list[Reserva]]:
    """Lê o arquivo JSON e devolve (reserva nova, reservas existentes)."""
    raise NotImplementedError("ler_arquivo ainda não implementada")
