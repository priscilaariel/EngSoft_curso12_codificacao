"""Fábrica de reservas para os testes: horários escritos como 'HH:MM'."""
from datetime import date, time

from reservas.reserva import Reserva

DIA_PADRAO = date(2026, 11, 3)


def horario(texto: str) -> time:
    horas, minutos = texto.split(":")
    return time(int(horas), int(minutos))


def reserva(inicio: str = "10:00", fim: str = "11:00", sala: str = "Sala 1", dia: date = DIA_PADRAO) -> Reserva:
    return Reserva(sala, dia, horario(inicio), horario(fim))
