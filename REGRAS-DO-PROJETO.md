# Regras do projeto Reserva de Salas

- Linguagem: Python 3.12. Dependências permitidas: biblioteca padrão e pytest. Nada além disso sem decisão registrada.
- Fonte das regras: `contrato/tarefa_reservas.md`. Decisões D1 a D7 fechadas. O que não estiver no contrato é decisão pendente.
- Tempo: `datetime.date` e `datetime.time`; nunca texto. Sem relógio do sistema.
- Funções puras: não alteram argumentos, sem estado global mutável. E/S só em `leitura.py` e `__main__.py`.
- Erros: `ErroDeValidacao` e `ConflitoDeReserva` (`reservas/erros.py`). Nunca devolver `None`, `False` ou lista vazia para sinalizar falha. Mensagens exatamente como no contrato.
- Nomes: português do domínio e sem acento nos identificadores (reserva, sala, dia, inicio, fim, conflito). Sem abreviações obscuras, sem nomes genéricos, sem literais soltos.
- Funções: uma responsabilidade, até 15 linhas, 3 parâmetros e 2 níveis de indentação; sem parâmetro flag; docstring de uma linha com a regra de negócio.
- Comentários: explicam o porquê, nunca repetem o código; sem código comentado nem TODO.
- Testes: pytest, um arquivo por módulo, um comportamento por teste, sem lógica dentro do teste, valores esperados escritos à mão a partir do contrato. Limites e erros são obrigatórios.
- Saída da linha de comando: resultado em stdout (código 0 sem conflito, 1 com conflito); erros em stderr com código 2.
- Dados e exemplos sempre fictícios.
