"""Testes da linha de comando: python -m reservas arquivo.json."""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EXEMPLOS = RAIZ / "exemplos"
USO = "uso: python -m reservas caminho_do_arquivo.json\n"


def executar(*argumentos: str) -> subprocess.CompletedProcess:
    ambiente = {**os.environ, "PYTHONUTF8": "1"}
    return subprocess.run(
        [sys.executable, "-m", "reservas", *argumentos],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", env=ambiente,
    )


# ---------- exemplos do contrato (seção 7) ----------

def test_agenda_livre_imprime_sem_conflito_e_sai_com_zero():
    resultado = executar(str(EXEMPLOS / "agenda_livre.json"))
    assert resultado.returncode == 0
    assert resultado.stdout == "Sem conflito: Sala 1, 2026-11-03, 11:00-12:00\n"
    assert resultado.stderr == ""


def test_agenda_com_conflito_lista_as_reservas_em_conflito_e_sai_com_um():
    resultado = executar(str(EXEMPLOS / "agenda_com_conflito.json"))
    assert resultado.returncode == 1
    assert resultado.stdout == (
        "Conflito: Sala 1, 2026-11-03, 10:30-11:30\n"
        "- Sala 1, 2026-11-03, 10:00-11:00\n"
        "- Sala 1, 2026-11-03, 11:15-12:00\n"
    )
    assert resultado.stderr == ""


def test_agenda_invalida_imprime_o_erro_em_stderr_e_nada_em_stdout():
    resultado = executar(str(EXEMPLOS / "agenda_invalida.json"))
    assert resultado.returncode == 2
    assert resultado.stdout == ""
    assert resultado.stderr == "erro: nova_reserva: fim (10:00) deve ser posterior ao inicio (11:00)\n"


# ---------- outros erros de entrada ----------

def test_arquivo_inexistente_sai_com_dois_e_erro_em_stderr(tmp_path):
    resultado = executar(str(tmp_path / "nao_existe.json"))
    assert resultado.returncode == 2
    assert resultado.stdout == ""
    assert resultado.stderr.startswith("erro: ")


def test_caminho_de_pasta_em_vez_de_arquivo_sai_com_dois(tmp_path):
    resultado = executar(str(tmp_path))
    assert resultado.returncode == 2
    assert resultado.stdout == ""
    assert resultado.stderr.startswith("erro: ")


def test_json_invalido_sai_com_dois_e_cita_o_json(tmp_path):
    arquivo = tmp_path / "ruim.json"
    arquivo.write_text("{", encoding="utf-8")
    resultado = executar(str(arquivo))
    assert resultado.returncode == 2
    assert resultado.stdout == ""
    assert resultado.stderr.startswith("erro: JSON inválido: ")


def test_arquivo_fora_de_utf8_sai_com_dois(tmp_path):
    arquivo = tmp_path / "latin1.json"
    arquivo.write_bytes(b"\xff\xfe{}")
    resultado = executar(str(arquivo))
    assert resultado.returncode == 2
    assert resultado.stdout == ""
    assert resultado.stderr == "erro: arquivo não está em UTF-8\n"


# ---------- uso ----------

def test_sem_argumentos_imprime_o_uso_em_stderr_e_sai_com_dois():
    resultado = executar()
    assert resultado.returncode == 2
    assert resultado.stdout == ""
    assert resultado.stderr == USO


def test_com_argumentos_demais_imprime_o_uso_em_stderr_e_sai_com_dois():
    resultado = executar(str(EXEMPLOS / "agenda_livre.json"), "extra")
    assert resultado.returncode == 2
    assert resultado.stdout == ""
    assert resultado.stderr == USO
