"""Testes de reservas.reserva.Reserva, escritos antes da implementação."""
import dataclasses
import re
from datetime import date, datetime, time, timezone

import pytest

from fabrica import DIA_PADRAO, reserva
from reservas.erros import ErroDeValidacao
from reservas.reserva import Reserva


def mensagem_exata(texto: str) -> str:
    return "^" + re.escape(texto) + "$"


# ---------- funcionamento normal ----------

def test_reserva_valida_guarda_os_valores_recebidos():
    criada = Reserva("Sala 1", date(2026, 11, 3), time(10, 0), time(11, 0))
    valores = (criada.sala, criada.dia, criada.inicio, criada.fim)
    assert valores == ("Sala 1", date(2026, 11, 3), time(10, 0), time(11, 0))


def test_nome_da_sala_e_guardado_como_veio_sem_normalizar():
    assert reserva(sala="  Sala 1 ").sala == "  Sala 1 "


def test_descricao_mostra_sala_dia_e_intervalo():
    assert reserva().descricao() == "Sala 1, 2026-11-03, 10:00-11:00"


def test_descricao_usa_dois_digitos_em_hora_e_minuto():
    assert reserva(inicio="08:05", fim="09:00").descricao() == "Sala 1, 2026-11-03, 08:05-09:00"


def test_reserva_e_imutavel():
    with pytest.raises(dataclasses.FrozenInstanceError):
        reserva().sala = "Sala 2"


def test_reservas_com_os_mesmos_dados_sao_iguais_e_tem_o_mesmo_hash():
    assert reserva() == reserva()
    assert hash(reserva()) == hash(reserva())


def test_reservas_com_dados_diferentes_nao_sao_iguais():
    assert reserva() != reserva(fim="11:30")


# ---------- limites ----------

def test_duracao_minima_de_um_minuto_e_valida():
    assert reserva(inicio="10:00", fim="10:01").descricao() == "Sala 1, 2026-11-03, 10:00-10:01"


def test_primeiro_minuto_do_dia_e_valido():
    assert reserva(inicio="00:00", fim="00:01").descricao() == "Sala 1, 2026-11-03, 00:00-00:01"


def test_ultimo_minuto_do_dia_e_valido():
    assert reserva(inicio="23:58", fim="23:59").descricao() == "Sala 1, 2026-11-03, 23:58-23:59"


def test_dia_inteiro_ate_23h59_e_valido():
    assert reserva(inicio="00:00", fim="23:59").descricao() == "Sala 1, 2026-11-03, 00:00-23:59"


# ---------- erros: término posterior ao início ----------

@pytest.mark.parametrize(
    "inicio, fim, esperada",
    [
        ("10:00", "10:00", "fim (10:00) deve ser posterior ao inicio (10:00)"),
        ("11:00", "10:00", "fim (10:00) deve ser posterior ao inicio (11:00)"),
        ("10:01", "10:00", "fim (10:00) deve ser posterior ao inicio (10:01)"),
        ("23:00", "00:00", "fim (00:00) deve ser posterior ao inicio (23:00)"),
    ],
    ids=["fim_igual_ao_inicio", "fim_antes_do_inicio", "fim_um_minuto_antes", "atravessa_a_meia_noite"],
)
def test_fim_nao_posterior_ao_inicio_levanta_erro_com_os_dois_horarios(inicio, fim, esperada):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(esperada)):
        reserva(inicio=inicio, fim=fim)


# ---------- erros: sala ----------

@pytest.mark.parametrize(
    "sala, esperada",
    [
        ("", "sala deve ser um texto não vazio, recebeu ''"),
        ("   ", "sala deve ser um texto não vazio, recebeu '   '"),
        (None, "sala deve ser um texto não vazio, recebeu None"),
        (101, "sala deve ser um texto não vazio, recebeu 101"),
    ],
    ids=["vazia", "so_espacos", "none", "numero"],
)
def test_sala_invalida_levanta_erro_com_o_valor_recebido(sala, esperada):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(esperada)):
        Reserva(sala, DIA_PADRAO, time(10, 0), time(11, 0))


# ---------- erros: dia ----------

@pytest.mark.parametrize(
    "dia, esperada",
    [
        (datetime(2026, 11, 3, 10, 0), "dia deve ser date (sem hora), recebeu datetime"),
        ("2026-11-03", "dia deve ser date (sem hora), recebeu str"),
        (None, "dia deve ser date (sem hora), recebeu NoneType"),
    ],
    ids=["datetime", "texto", "none"],
)
def test_dia_que_nao_e_date_levanta_erro_com_o_tipo_recebido(dia, esperada):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(esperada)):
        Reserva("Sala 1", dia, time(10, 0), time(11, 0))


# ---------- erros: inicio e fim ----------

@pytest.mark.parametrize("campo", ["inicio", "fim"])
@pytest.mark.parametrize(
    "valor, tipo",
    [("10:00", "str"), (None, "NoneType"), (datetime(2026, 11, 3, 10, 0), "datetime"), (10, "int")],
    ids=["texto", "none", "datetime", "inteiro"],
)
def test_horario_que_nao_e_time_levanta_erro_com_o_tipo_recebido(campo, valor, tipo):
    argumentos = {"inicio": time(10, 0), "fim": time(11, 0), campo: valor}
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(f"{campo} deve ser time, recebeu {tipo}")):
        Reserva("Sala 1", DIA_PADRAO, argumentos["inicio"], argumentos["fim"])


@pytest.mark.parametrize("campo", ["inicio", "fim"])
def test_horario_com_fuso_horario_levanta_erro(campo):
    argumentos = {"inicio": time(10, 0), "fim": time(11, 0), campo: time(10, 30, tzinfo=timezone.utc)}
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(f"{campo} não pode ter fuso horário")):
        Reserva("Sala 1", DIA_PADRAO, argumentos["inicio"], argumentos["fim"])


@pytest.mark.parametrize("campo", ["inicio", "fim"])
@pytest.mark.parametrize(
    "valor, texto",
    [(time(10, 30, 30), "10:30:30"), (time(10, 30, 0, 500), "10:30:00.000500")],
    ids=["com_segundos", "com_microssegundos"],
)
def test_horario_fora_de_minutos_inteiros_levanta_erro(campo, valor, texto):
    argumentos = {"inicio": time(9, 0), "fim": time(12, 0), campo: valor}
    esperada = f"{campo} deve estar em minutos inteiros, recebeu {texto}"
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(esperada)):
        Reserva("Sala 1", DIA_PADRAO, argumentos["inicio"], argumentos["fim"])


# ---------- ordem de validação ----------

def test_primeiro_erro_da_ordem_sala_dia_inicio_fim_e_o_que_vale():
    with pytest.raises(ErroDeValidacao, match="^sala deve ser"):
        Reserva("", "2026-11-03", "10:00", "09:00")


def test_erro_de_tipo_do_horario_vem_antes_da_comparacao_entre_inicio_e_fim():
    with pytest.raises(ErroDeValidacao, match="^inicio deve ser time"):
        Reserva("Sala 1", DIA_PADRAO, "10:00", time(9, 0))


def test_inicio_e_validado_antes_do_fim():
    with pytest.raises(ErroDeValidacao, match="^inicio deve ser time, recebeu str"):
        Reserva("Sala 1", DIA_PADRAO, "10:00", "11:00")


def test_dia_e_validado_antes_do_inicio():
    with pytest.raises(ErroDeValidacao, match="^dia deve ser date"):
        Reserva("Sala 1", "2026-11-03", "10:00", time(11, 0))
