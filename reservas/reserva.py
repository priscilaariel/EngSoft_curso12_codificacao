"""Reserva de uma sala: sala, dia e intervalo de horário já validados."""
from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class Reserva:
    """Ocupação de uma sala em um dia, do inicio (inclusive) ao fim (exclusive)."""

    sala: str
    dia: date
    inicio: time
    fim: time

    def __post_init__(self) -> None:
        # Esqueleto: validar sala, dia, inicio e fim conforme contrato/tarefa_reservas.md.
        raise NotImplementedError("validação da Reserva ainda não implementada")

    def descricao(self) -> str:
        """Texto 'sala, AAAA-MM-DD, HH:MM-HH:MM' usado em mensagens e na saída do programa."""
        raise NotImplementedError("descricao ainda não implementada")
