"""Regras de conflito entre reservas da mesma sala no mesmo dia."""
from collections.abc import Iterable

from reservas.reserva import Reserva


def reservas_conflitam(reserva_a: Reserva, reserva_b: Reserva) -> bool:
    """Duas reservas conflitam se são da mesma sala e dia e seus intervalos se sobrepõem."""
    raise NotImplementedError("reservas_conflitam ainda não implementada")


def buscar_conflitos(nova: Reserva, existentes: Iterable[Reserva]) -> list[Reserva]:
    """Devolve as reservas existentes que conflitam com a nova, na ordem recebida."""
    raise NotImplementedError("buscar_conflitos ainda não implementada")


def exigir_sem_conflito(nova: Reserva, existentes: Iterable[Reserva]) -> None:
    """Aceita a reserva nova apenas se nenhuma reserva existente conflitar com ela."""
    raise NotImplementedError("exigir_sem_conflito ainda não implementada")
