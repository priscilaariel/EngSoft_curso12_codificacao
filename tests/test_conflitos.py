"""Testes de reservas.conflitos, escritos antes da implementação."""
import re
from datetime import date

import pytest

from fabrica import reserva
from reservas.conflitos import buscar_conflitos, exigir_sem_conflito, reservas_conflitam
from reservas.erros import ConflitoDeReserva, ErroDeValidacao

# (inicio_a, fim_a, inicio_b, fim_b, conflitam), escritos à mão a partir do contrato, seção 6.
TABELA_DE_HORARIOS = [
    ("10:00", "11:00", "10:30", "11:30", True),     # exemplo do enunciado
    ("10:00", "11:00", "09:30", "10:30", True),     # sobreposição no começo
    ("10:00", "11:00", "14:00", "15:00", False),    # distantes
    ("10:00", "11:00", "11:00", "12:00", False),    # começa quando a outra termina (enunciado)
    ("10:00", "11:00", "09:00", "10:00", False),    # termina quando a outra começa
    ("10:00", "11:00", "10:59", "12:00", True),     # 1 minuto de sobreposição
    ("10:00", "11:00", "11:01", "12:00", False),    # 1 minuto de folga
    ("10:00", "12:00", "10:30", "11:00", True),     # B contida em A
    ("10:30", "11:00", "10:00", "12:00", True),     # A contida em B
    ("10:00", "11:00", "10:00", "11:00", True),     # idênticas
    ("10:00", "11:00", "10:00", "10:30", True),     # mesmo início
    ("10:00", "11:00", "10:30", "11:00", True),     # mesmo fim
    ("10:00", "10:01", "10:01", "10:02", False),    # duração mínima, encostadas
    ("10:00", "10:01", "10:00", "10:01", True),     # duração mínima, idênticas
    ("00:00", "00:01", "00:01", "00:02", False),    # início do dia, encostadas
    ("23:30", "23:59", "23:00", "23:30", False),    # fim do dia, encostadas
    ("23:00", "23:59", "23:30", "23:59", True),     # fim do dia, sobrepostas
]
IDS_DA_TABELA = [f"{ia}-{fa}_x_{ib}-{fb}" for ia, fa, ib, fb, _ in TABELA_DE_HORARIOS]


def mensagem_exata(texto: str) -> str:
    return "^" + re.escape(texto) + "$"


# ---------- reservas_conflitam: horários ----------

@pytest.mark.parametrize("inicio_a, fim_a, inicio_b, fim_b, esperado", TABELA_DE_HORARIOS, ids=IDS_DA_TABELA)
def test_conflito_conforme_a_tabela_do_contrato(inicio_a, fim_a, inicio_b, fim_b, esperado):
    assert reservas_conflitam(reserva(inicio_a, fim_a), reserva(inicio_b, fim_b)) is esperado


@pytest.mark.parametrize("inicio_a, fim_a, inicio_b, fim_b, esperado", TABELA_DE_HORARIOS, ids=IDS_DA_TABELA)
def test_conflito_e_simetrico(inicio_a, fim_a, inicio_b, fim_b, esperado):
    assert reservas_conflitam(reserva(inicio_b, fim_b), reserva(inicio_a, fim_a)) is esperado


# ---------- reservas_conflitam: sala e dia ----------

def test_salas_diferentes_no_mesmo_horario_nao_conflitam():
    assert reservas_conflitam(reserva(sala="Sala 1"), reserva(sala="Sala 2")) is False


def test_dias_diferentes_no_mesmo_horario_nao_conflitam():
    assert reservas_conflitam(reserva(dia=date(2026, 11, 3)), reserva(dia=date(2026, 11, 4))) is False


def test_sala_e_comparada_sem_distinguir_maiusculas_nem_espacos_nas_pontas():
    assert reservas_conflitam(reserva(sala="Sala 1"), reserva(sala=" sala 1 ")) is True


def test_sala_com_acento_tambem_ignora_maiusculas():
    assert reservas_conflitam(reserva(sala="Sala Ação"), reserva(sala="SALA AÇÃO")) is True


@pytest.mark.parametrize(
    "outra_sala",
    ["Sala 10", "Sala  1", "Sala1", "Sala"],
    ids=["prefixo_de_outra", "espaco_interno_duplo", "sem_espaco", "so_o_prefixo"],
)
def test_nome_de_sala_so_vale_inteiro_e_com_espacos_internos(outra_sala):
    assert reservas_conflitam(reserva(sala="Sala 1"), reserva(sala=outra_sala)) is False


# ---------- reservas_conflitam: erros ----------

def test_reserva_a_que_nao_e_reserva_levanta_erro_com_o_tipo():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("reserva_a deve ser Reserva, recebeu dict")):
        reservas_conflitam({"sala": "Sala 1"}, reserva())


def test_reserva_b_que_nao_e_reserva_levanta_erro_com_o_tipo():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("reserva_b deve ser Reserva, recebeu NoneType")):
        reservas_conflitam(reserva(), None)


# ---------- buscar_conflitos ----------

def agenda_do_exemplo() -> list:
    return [
        reserva("09:00", "10:00"),
        reserva("10:00", "11:00"),
        reserva("11:15", "12:00"),
        reserva("10:00", "11:00", sala="Sala 2"),
        reserva("14:00", "15:00"),
    ]


def test_devolve_so_as_existentes_que_conflitam_na_ordem_recebida():
    nova = reserva("10:30", "11:30")
    assert buscar_conflitos(nova, agenda_do_exemplo()) == [reserva("10:00", "11:00"), reserva("11:15", "12:00")]


def test_ordem_do_resultado_segue_a_ordem_de_existentes_e_nao_a_do_horario():
    nova = reserva("10:00", "12:00")
    existentes = [reserva("11:00", "11:30"), reserva("10:00", "10:30")]
    assert buscar_conflitos(nova, existentes) == [reserva("11:00", "11:30"), reserva("10:00", "10:30")]


def test_sem_conflito_devolve_lista_vazia():
    assert buscar_conflitos(reserva("11:00", "12:00"), [reserva("10:00", "11:00"), reserva("12:00", "13:00")]) == []


def test_sem_reservas_existentes_devolve_lista_vazia():
    assert buscar_conflitos(reserva(), []) == []


def test_resultado_e_uma_lista_nova_e_a_entrada_nao_e_alterada():
    existentes = [reserva("10:00", "11:00"), reserva("14:00", "15:00")]
    copia = list(existentes)
    resultado = buscar_conflitos(reserva("10:30", "11:30"), existentes)
    assert isinstance(resultado, list)
    assert resultado is not existentes
    assert existentes == copia


def test_aceita_tupla_e_gerador_como_existentes():
    existentes = [reserva("10:00", "11:00"), reserva("14:00", "15:00")]
    nova = reserva("10:30", "11:30")
    assert buscar_conflitos(nova, tuple(existentes)) == [reserva("10:00", "11:00")]
    assert buscar_conflitos(nova, (r for r in existentes)) == [reserva("10:00", "11:00")]


def test_reserva_igual_a_nova_ja_existente_conflita_consigo_mesma():
    nova = reserva("10:00", "11:00")
    assert buscar_conflitos(nova, [nova]) == [nova]


def test_reservas_repetidas_em_existentes_aparecem_uma_vez_por_ocorrencia():
    repetida = reserva("10:00", "11:00")
    assert buscar_conflitos(reserva("10:30", "11:30"), [repetida, repetida]) == [repetida, repetida]


# ---------- buscar_conflitos: erros ----------

def test_nova_que_nao_e_reserva_levanta_erro_com_o_tipo():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("nova deve ser Reserva, recebeu str")):
        buscar_conflitos("10:00-11:00", [])


@pytest.mark.parametrize("existentes, tipo", [(None, "NoneType"), (42, "int")], ids=["none", "inteiro"])
def test_existentes_nao_iteravel_levanta_erro_com_o_tipo(existentes, tipo):
    esperada = f"existentes deve ser uma coleção de Reserva, recebeu {tipo}"
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(esperada)):
        buscar_conflitos(reserva(), existentes)


def test_item_invalido_de_existentes_levanta_erro_com_o_indice():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("existentes[1] deve ser Reserva, recebeu str")):
        buscar_conflitos(reserva(), [reserva("14:00", "15:00"), "10:00-11:00"])


def test_item_invalido_depois_de_um_conflito_ainda_levanta_erro_sem_resultado_parcial():
    existentes = [reserva("10:00", "11:00"), None]
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("existentes[1] deve ser Reserva, recebeu NoneType")):
        buscar_conflitos(reserva("10:30", "11:30"), existentes)


# ---------- exigir_sem_conflito ----------

def test_sem_conflito_nao_levanta_nada_e_devolve_none():
    assert exigir_sem_conflito(reserva("11:00", "12:00"), [reserva("10:00", "11:00")]) is None


def test_com_conflito_levanta_conflito_de_reserva_com_a_lista_de_conflitos():
    nova = reserva("10:30", "11:30")
    existentes = [reserva("10:00", "11:00"), reserva("11:15", "12:00"), reserva("14:00", "15:00")]
    with pytest.raises(ConflitoDeReserva) as excecao:
        exigir_sem_conflito(nova, existentes)
    assert excecao.value.conflitos == [reserva("10:00", "11:00"), reserva("11:15", "12:00")]


def test_mensagem_do_conflito_traz_a_nova_e_cada_conflitante():
    nova = reserva("10:30", "11:30")
    existentes = [reserva("10:00", "11:00"), reserva("11:15", "12:00")]
    esperada = (
        "reserva Sala 1, 2026-11-03, 10:30-11:30 conflita com: "
        "Sala 1, 2026-11-03, 10:00-11:00; Sala 1, 2026-11-03, 11:15-12:00"
    )
    with pytest.raises(ConflitoDeReserva, match=mensagem_exata(esperada)):
        exigir_sem_conflito(nova, existentes)


def test_conflito_de_reserva_e_um_erro_de_validacao():
    assert issubclass(ConflitoDeReserva, ErroDeValidacao)


def test_exigir_sem_conflito_tambem_valida_as_entradas():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("nova deve ser Reserva, recebeu NoneType")):
        exigir_sem_conflito(None, [])
