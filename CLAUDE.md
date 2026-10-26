# Reserva de Salas

Este projeto é desenvolvido com o agente descrito em @AGENTE.md, seguindo as convenções de @REGRAS-DO-PROJETO.md.

- Contrato da tarefa: `contrato/tarefa_reservas.md` (entradas, saídas, regras, exemplos de funcionamento normal, limite e erro, decisões D1 a D7)
- Exemplos de arquivo para a linha de comando: `exemplos/`
- Skills do projeto: `/rodar-reservas` (roda o programa sobre um arquivo JSON) e `/rodar-testes` (roda a suíte pytest)

Os módulos em `reservas/` começam como esqueletos (`NotImplementedError`) e os testes já existem. A tarefa do agente é implementar os módulos até a suíte passar, seguindo a checklist de revisão do `AGENTE.md`.

Os testes são a especificação executável: não os altere para fazê-los passar sem uma decisão humana registrada.
