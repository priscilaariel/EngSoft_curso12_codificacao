# Reserva de Salas (esqueleto para o agente implementar)

Projeto Python para VS Code e Claude Code. Verifica conflitos entre reservas da mesma sala no mesmo dia: uma reserva das 10h às 11h impede outra das 10h30 às 11h30, mas permite uma que comece às 11h. O término deve ser posterior ao início. Todos os dados são fictícios.

O projeto vem com o problema definido (contrato), as instruções do agente, os testes escritos e os módulos como **esqueletos** (`NotImplementedError`). A implementação é a tarefa do agente.

## Estrutura

```
AGENTE.md                      prompt do agente: papel, regras, convenções, critérios de Clean Code, processo, checklist
REGRAS-DO-PROJETO.md           convenções do projeto em uma página
CLAUDE.md                      carrega AGENTE.md e REGRAS-DO-PROJETO.md no Claude Code
contrato/tarefa_reservas.md    problema, entradas, saídas, regras, exemplos normais, de limite e de erro, decisões D1 a D7
exemplos/                      agenda_livre.json, agenda_com_conflito.json, agenda_invalida.json
reservas/                      erros.py (pronto), reserva.py, conflitos.py, leitura.py, __main__.py (esqueletos)
tests/                         test_reserva.py, test_conflitos.py, test_leitura.py, test_main.py, fabrica.py
.claude/skills/                rodar-reservas e rodar-testes
.vscode/                       configuração do VS Code (testes, depuração, tarefas)
```

## 1. Preparar o ambiente (uma vez)

Requisito: Python 3.12 ou mais novo. Abra a pasta raiz no VS Code (File > Open Folder) e, no terminal integrado:

macOS ou Linux:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Windows (PowerShell):
```
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

No VS Code: Ctrl+Shift+P (Cmd+Shift+P no Mac), "Python: Select Interpreter", e escolha o Python de `.venv`.

## 2. Estado inicial: tudo vermelho de propósito

No Claude Code, com a pasta raiz aberta, digite `/rodar-testes`. Esperado: quase todos os testes falham com `NotImplementedError`, porque os módulos são esqueletos. Passa só o teste que confere que `ConflitoDeReserva` é um `ErroDeValidacao`, já que `erros.py` vem pronto.

## 3. Pedir a implementação ao agente (duas etapas)

O `CLAUDE.md` já carrega as instruções do agente. Em duas mensagens:

1. Etapa 1, sem código: "Siga o AGENTE.md, etapa 1. Liste as decisões pendentes, os comportamentos que o contrato não define e confirme se os testes cobrem os exemplos normais, de limite e de erro."
2. Etapa 2, depois que você revisar a resposta: "Etapa 2. Implemente os módulos na ordem reserva, conflitos, leitura e __main__, rode os testes e confira a checklist de revisão."

## 4. Conferir o resultado

| Comando | O que faz |
|---------|-----------|
| `/rodar-testes` | Roda a suíte inteira e resume as falhas por seção do contrato. |
| `/rodar-testes -k encostadas` | Roda só os testes cujo nome contém "encostadas". |
| `/rodar-reservas` | Roda `exemplos/agenda_com_conflito.json` e mostra o resultado. |
| `/rodar-reservas exemplos/agenda_livre.json` | Roda o arquivo que você indicar. |

Sem as skills: `python -m pytest -q` e `python -m reservas exemplos/agenda_com_conflito.json` (use `python3` no macOS ou Linux fora do `.venv`, `py` no Windows). No VS Code: painel Testing, F5 e Terminal > Run Task.

Códigos de saída do programa: 0 sem conflito, 1 com conflito (resultado esperado, não falha), 2 entrada inválida.

## 5. Revisão do código gerado

Além de a suíte passar, confira a checklist do final do `AGENTE.md`: tamanho e responsabilidade das funções, regra de conflito em um único lugar, nomes, comentários que explicam o porquê, erros sem engolir exceção, nenhuma função alterando seus argumentos. Uma pergunta útil para o seu relato: o agente respeitou os critérios de Clean Code que foram pedidos explicitamente, e o que foi preciso corrigir?

## Observações

- O sistema é determinístico e não usa relógio, rede nem banco de dados.
- Os testes foram validados com uma implementação de referência que não está no projeto, para não substituir o trabalho do agente.
- Decisões fechadas (D1 a D7) estão no contrato. Lacunas novas devem virar `DECISÃO PENDENTE D8` em diante.
- Testado em Python 3.13; o projeto fixa 3.12, então confira também nessa versão.
