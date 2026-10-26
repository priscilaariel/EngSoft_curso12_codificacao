---
name: rodar-reservas
description: Executa a verificação de conflito de reservas sobre um arquivo JSON e mostra o resultado. Use quando o usuário pedir para rodar o projeto, verificar uma agenda ou testar um arquivo de reservas.
argument-hint: [caminho-do-arquivo-json]
allowed-tools: Bash(python3 -m reservas *) Bash(python -m reservas *) Bash(py -m reservas *)
disable-model-invocation: true
---

# Rodar o Reserva de Salas sobre um arquivo

Arquivo a usar: `$ARGUMENTS`. Se nenhum caminho foi informado, use `exemplos/agenda_com_conflito.json`.

## Passos

1. Trabalhe sempre na raiz do projeto (a pasta que contém `reservas/` e `exemplos/`).
2. Execute o comando abaixo, trocando `<arquivo>` pelo caminho escolhido:
   - macOS ou Linux: `python3 -m reservas <arquivo>`
   - Windows: `py -m reservas <arquivo>` (ou `python -m reservas <arquivo>`)
   - Se existir a pasta `.venv`, use o Python dela: `.venv/bin/python -m reservas <arquivo>` (Windows: `.venv\Scripts\python.exe -m reservas <arquivo>`).
3. Mostre ao usuário a saída exatamente como saiu, sem reescrever ou resumir.
4. Termine com uma linha dizendo o código de saída e o que ele significa.

## Como ler o resultado

- Código 0: sem conflito. A reserva nova pode ser feita.
- Código 1: há conflito. Isso é um resultado esperado do programa, não uma falha. Mostre as reservas em conflito listadas em stdout.
- Código 2: entrada inválida, arquivo ausente ou uso errado. Mostre a mensagem de stderr na íntegra e diga qual reserva do arquivo a causou, quando ela for citada.
- Se aparecer `NotImplementedError` ou um traceback do Python, o módulo ainda é um esqueleto ou há um defeito: relate isso como comportamento inesperado, sem tentar corrigir.

## Regras

- Esta skill só executa e relata. Não edite arquivos do projeto nem os arquivos de exemplo.
- Não invente resultados: se o comando não rodar, diga que não rodou.
