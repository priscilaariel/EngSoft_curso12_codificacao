"""Testes de reservas.leitura, escritos antes da implementação."""
import json
import re
from pathlib import Path

import pytest

from fabrica import reserva
from reservas.erros import ErroDeValidacao
from reservas.leitura import ler_arquivo, ler_reserva

VALIDA = {"sala": "Sala 1", "dia": "2026-11-03", "inicio": "10:00", "fim": "11:00"}
NOVA = {"sala": "Sala 1", "dia": "2026-11-03", "inicio": "10:30", "fim": "11:30"}


def com(**alteracoes) -> dict:
    return {**VALIDA, **alteracoes}


def sem(*chaves: str) -> dict:
    return {chave: valor for chave, valor in VALIDA.items() if chave not in chaves}


def mensagem_exata(texto: str) -> str:
    return "^" + re.escape(texto) + "$"


def escrever(tmp_path, conteudo) -> str:
    arquivo = tmp_path / "agenda.json"
    if isinstance(conteudo, bytes):
        arquivo.write_bytes(conteudo)
    elif isinstance(conteudo, str):
        arquivo.write_text(conteudo, encoding="utf-8")
    else:
        arquivo.write_text(json.dumps(conteudo), encoding="utf-8")
    return str(arquivo)


# ---------- ler_reserva: funcionamento normal e limites ----------

def test_objeto_valido_vira_reserva():
    assert ler_reserva(VALIDA) == reserva("10:00", "11:00")


def test_primeiro_e_ultimo_minuto_do_dia_sao_aceitos():
    assert ler_reserva(com(inicio="00:00", fim="23:59")) == reserva("00:00", "23:59")


def test_29_de_fevereiro_de_ano_bissexto_e_aceito():
    assert ler_reserva(com(dia="2028-02-29")).descricao() == "Sala 1, 2028-02-29, 10:00-11:00"


# ---------- ler_reserva: erros de estrutura ----------

@pytest.mark.parametrize(
    "dados, tipo",
    [([], "list"), (None, "NoneType"), ("Sala 1", "str")],
    ids=["lista", "none", "texto"],
)
def test_reserva_que_nao_e_objeto_levanta_erro_com_o_tipo(dados, tipo):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(f"reserva deve ser um objeto JSON, recebeu {tipo}")):
        ler_reserva(dados)


@pytest.mark.parametrize("campo", ["sala", "dia", "inicio", "fim"])
def test_campo_ausente_levanta_erro_com_o_nome_do_campo(campo):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(f"campo obrigatório ausente: '{campo}'")):
        ler_reserva(sem(campo))


def test_com_varios_campos_ausentes_o_primeiro_da_ordem_sala_dia_inicio_fim_e_citado():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("campo obrigatório ausente: 'dia'")):
        ler_reserva(sem("fim", "dia"))


def test_campo_desconhecido_levanta_erro_com_o_nome_do_campo():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("campo desconhecido: 'andar'")):
        ler_reserva(com(andar="2"))


def test_campo_ausente_e_citado_antes_do_campo_desconhecido():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("campo obrigatório ausente: 'fim'")):
        ler_reserva({**sem("fim"), "andar": "2"})


# ---------- ler_reserva: erros de formato ----------

@pytest.mark.parametrize(
    "dia",
    [
        "03/11/2026", "2026-11-3", "2026-02-30", "2026-02-29", "2026-13-01", "2026-11-03T10:00",
        "", " 2026-11-03", "٢٠٢٦-١١-٠٣", 20261103, None,
    ],
    ids=[
        "barras", "um_digito", "30_de_fevereiro", "29_fev_nao_bissexto", "mes_13", "com_hora",
        "vazio", "espaco", "digitos_arabes", "inteiro", "none",
    ],
)
def test_dia_fora_do_formato_ou_inexistente_levanta_erro_com_o_valor(dia):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(f"dia inválido: {dia!r}; esperado AAAA-MM-DD")):
        ler_reserva(com(dia=dia))


@pytest.mark.parametrize("campo", ["inicio", "fim"])
@pytest.mark.parametrize(
    "horario",
    ["10h", "9:00", "10:00:00", "25:00", "10:60", "24:00", "", " 10:00", "١٠:٠٠", 1000, None],
    ids=[
        "com_h", "um_digito", "com_segundos", "hora_25", "minuto_60", "hora_24",
        "vazio", "espaco", "digitos_arabes", "inteiro", "none",
    ],
)
def test_horario_fora_do_formato_ou_inexistente_levanta_erro_com_o_valor(campo, horario):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(f"{campo} inválido: {horario!r}; esperado HH:MM")):
        ler_reserva(com(**{campo: horario}))


def test_primeiro_erro_de_formato_da_ordem_dia_inicio_fim_e_o_citado():
    with pytest.raises(ErroDeValidacao, match="^dia inválido"):
        ler_reserva(com(dia="03/11/2026", inicio="25:00"))


# ---------- ler_reserva: erros que vêm da Reserva ----------

def test_sala_que_nao_e_texto_levanta_o_erro_da_reserva():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("sala deve ser um texto não vazio, recebeu None")):
        ler_reserva(com(sala=None))


def test_fim_antes_do_inicio_levanta_o_erro_da_reserva():
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("fim (10:00) deve ser posterior ao inicio (11:00)")):
        ler_reserva(com(inicio="11:00", fim="10:00"))


# ---------- ler_arquivo: funcionamento normal ----------

def test_arquivo_valido_devolve_a_nova_e_as_existentes_na_ordem_do_arquivo(tmp_path):
    existentes = [VALIDA, com(inicio="12:00", fim="13:00")]
    nova, lidas = ler_arquivo(escrever(tmp_path, {"nova_reserva": NOVA, "reservas_existentes": existentes}))
    assert nova == reserva("10:30", "11:30")
    assert lidas == [reserva("10:00", "11:00"), reserva("12:00", "13:00")]


def test_arquivo_sem_reservas_existentes_devolve_lista_vazia(tmp_path):
    _, lidas = ler_arquivo(escrever(tmp_path, {"nova_reserva": NOVA, "reservas_existentes": []}))
    assert lidas == []


def test_aceita_caminho_como_path(tmp_path):
    caminho = escrever(tmp_path, {"nova_reserva": NOVA, "reservas_existentes": []})
    nova, _ = ler_arquivo(Path(caminho))
    assert nova == reserva("10:30", "11:30")


# ---------- ler_arquivo: erros ----------

def test_arquivo_inexistente_deixa_a_oserror_subir(tmp_path):
    with pytest.raises(OSError):
        ler_arquivo(str(tmp_path / "nao_existe.json"))


def test_conteudo_que_nao_e_json_levanta_erro_com_linha_e_coluna(tmp_path):
    with pytest.raises(ErroDeValidacao, match=r"^JSON inválido: .+ \(linha 1, coluna 2\)$"):
        ler_arquivo(escrever(tmp_path, "{"))


def test_arquivo_que_nao_esta_em_utf8_levanta_erro(tmp_path):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("arquivo não está em UTF-8")):
        ler_arquivo(escrever(tmp_path, b"\xff\xfe{}"))


def test_topo_que_nao_e_objeto_levanta_erro_com_o_tipo(tmp_path):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("o conteúdo deve ser um objeto JSON, recebeu list")):
        ler_arquivo(escrever(tmp_path, "[]"))


@pytest.mark.parametrize(
    "conteudo, ausente",
    [
        ({}, "nova_reserva"),
        ({"nova_reserva": NOVA}, "reservas_existentes"),
        ({"reservas_existentes": []}, "nova_reserva"),
    ],
    ids=["vazio", "sem_existentes", "sem_nova"],
)
def test_chave_do_topo_ausente_levanta_erro_com_o_nome(tmp_path, conteudo, ausente):
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(f"campo obrigatório ausente: '{ausente}'")):
        ler_arquivo(escrever(tmp_path, conteudo))


def test_chave_do_topo_desconhecida_levanta_erro_com_o_nome(tmp_path):
    conteudo = {"nova_reserva": NOVA, "reservas_existentes": [], "observacao": "x"}
    with pytest.raises(ErroDeValidacao, match=mensagem_exata("campo desconhecido: 'observacao'")):
        ler_arquivo(escrever(tmp_path, conteudo))


@pytest.mark.parametrize(
    "existentes, tipo",
    [("Sala 1", "str"), ({}, "dict"), (None, "NoneType")],
    ids=["texto", "objeto", "none"],
)
def test_reservas_existentes_que_nao_e_lista_levanta_erro_com_o_tipo(tmp_path, existentes, tipo):
    esperada = f"reservas_existentes deve ser uma lista, recebeu {tipo}"
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(esperada)):
        ler_arquivo(escrever(tmp_path, {"nova_reserva": NOVA, "reservas_existentes": existentes}))


def test_erro_na_nova_reserva_leva_o_prefixo_nova_reserva(tmp_path):
    nova = com(inicio="11:00", fim="10:00")
    esperada = "nova_reserva: fim (10:00) deve ser posterior ao inicio (11:00)"
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(esperada)):
        ler_arquivo(escrever(tmp_path, {"nova_reserva": nova, "reservas_existentes": []}))


def test_erro_numa_existente_leva_o_prefixo_com_o_indice(tmp_path):
    existentes = [VALIDA, VALIDA, sem("fim")]
    esperada = "reservas_existentes[2]: campo obrigatório ausente: 'fim'"
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(esperada)):
        ler_arquivo(escrever(tmp_path, {"nova_reserva": NOVA, "reservas_existentes": existentes}))


def test_reserva_existente_que_nao_e_objeto_leva_o_prefixo_com_o_indice(tmp_path):
    esperada = "reservas_existentes[0]: reserva deve ser um objeto JSON, recebeu str"
    with pytest.raises(ErroDeValidacao, match=mensagem_exata(esperada)):
        ler_arquivo(escrever(tmp_path, {"nova_reserva": NOVA, "reservas_existentes": ["Sala 1"]}))


def test_erro_na_nova_vem_antes_do_erro_nas_existentes(tmp_path):
    conteudo = {"nova_reserva": sem("sala"), "reservas_existentes": [sem("fim")]}
    with pytest.raises(ErroDeValidacao, match="^nova_reserva: "):
        ler_arquivo(escrever(tmp_path, conteudo))
