---
name: rodar-testes
description: Executa a suíte de testes pytest do projeto e resume o resultado, agrupando as falhas por regra do contrato. Use quando o usuário pedir para rodar, conferir ou validar os testes.
argument-hint: [filtro opcional, ex.: -k encostadas ou tests/test_conflitos.py]
allowed-tools: Bash(python3 -m pytest *) Bash(python -m pytest *) Bash(py -m pytest *)
disable-model-invocation: true
---

# Rodar os testes do Reserva de Salas

Filtro opcional: `$ARGUMENTS`. Se vazio, rode a suíte inteira.

## Passos

1. Trabalhe sempre na raiz do projeto (a pasta que contém `pytest.ini`).
2. Execute:
   - macOS ou Linux: `python3 -m pytest -q $ARGUMENTS`
   - Windows: `py -m pytest -q $ARGUMENTS` (ou `python -m pytest -q $ARGUMENTS`)
   - Se existir a pasta `.venv`, use o Python dela: `.venv/bin/python -m pytest -q $ARGUMENTS` (Windows: `.venv\Scripts\python.exe -m pytest -q $ARGUMENTS`).
3. Se o pytest não for encontrado, diga ao usuário para instalar com `pip install -r requirements-dev.txt` dentro do ambiente virtual.

## Como relatar

1. Primeira linha: total de testes aprovados e reprovados, copiando o resumo final do pytest.
2. Se todas as falhas forem `NotImplementedError`, diga que os módulos ainda são esqueletos e quais arquivos faltam implementar. Não liste teste por teste.
3. Nas demais falhas, uma linha por grupo com: nome do teste, o que era esperado, o que foi obtido e a seção do `contrato/tarefa_reservas.md` a que ela se refere (regra de conflito, limite, validação da Reserva, leitura do arquivo ou linha de comando).
4. Agrupe falhas que têm a mesma causa e diga qual é a causa provável no código, com arquivo e função.
5. Termine dizendo se a suíte está aprovada ou não, sem suavizar.

## Regras

- Os testes são a especificação executável. Nunca altere, apague ou desative um teste para fazê-lo passar.
- Não corrija o código a menos que o usuário peça. Esta skill só executa e relata.
- Se um teste parecer contradizer o contrato, relate como pergunta para o usuário decidir, não como erro simples.
