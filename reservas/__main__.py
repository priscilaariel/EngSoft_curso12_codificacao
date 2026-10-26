"""Linha de comando: verifica se a reserva nova de um arquivo JSON conflita com as existentes."""
import sys


def principal(argumentos: list[str]) -> int:
    """Executa a verificação e devolve o código de saída (0 livre, 1 conflito, 2 erro)."""
    raise NotImplementedError("linha de comando ainda não implementada")


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
