# Contrato: conflito de reservas de sala

## 1. O problema

Um sistema fictício de reserva de salas precisa impedir que duas reservas ocupem a mesma sala no mesmo dia em horários que se sobrepõem. Antes de aceitar uma reserva nova, o sistema verifica quais reservas já existentes entram em conflito com ela.

Regras que definem o problema:

- Duas reservas só conflitam se forem da mesma sala e do mesmo dia.
- Uma reserva das 10h às 11h impede outra das 10h30 às 11h30.
- Uma reserva das 10h às 11h permite outra que comece às 11h (e outra que termine às 10h). O horário de término de uma reserva já está livre para a próxima.
- O término de uma reserva deve ser posterior ao início.

Na prática, cada reserva ocupa o intervalo meio aberto [início, fim): inclui o início e não inclui o fim. Duas reservas conflitam quando `inicio_a < fim_b` e `inicio_b < fim_a`.

## 2. Entradas

### Reserva (dataclass imutável, módulo `reservas/reserva.py`)

| Campo | Tipo | Regra |
|-------|------|-------|
| sala | str | Texto não vazio depois de remover espaços das pontas. Guardado como veio. |
| dia | datetime.date | Apenas data. `datetime` é recusado, mesmo sendo subclasse de `date`. |
| inicio | datetime.time | Sem fuso horário, em minutos inteiros (segundos e microssegundos iguais a zero). |
| fim | datetime.time | Mesmas regras de `inicio`, e obrigatoriamente posterior a `inicio`. |

A validação acontece ao criar a `Reserva`. Quem recebe uma `Reserva` pode confiar que ela é válida. A ordem de validação é: sala, dia, inicio, fim, e por último `fim > inicio`. Vale o primeiro erro encontrado.

### Funções (módulo `reservas/conflitos.py`)

```
reservas_conflitam(reserva_a: Reserva, reserva_b: Reserva) -> bool
buscar_conflitos(nova: Reserva, existentes: Iterable[Reserva]) -> list[Reserva]
exigir_sem_conflito(nova: Reserva, existentes: Iterable[Reserva]) -> None
```

### Arquivo de entrada da linha de comando (JSON, UTF-8)

```json
{
  "reservas_existentes": [
    {"sala": "Sala 1", "dia": "2026-11-03", "inicio": "10:00", "fim": "11:00"}
  ],
  "nova_reserva": {"sala": "Sala 1", "dia": "2026-11-03", "inicio": "10:30", "fim": "11:30"}
}
```

Dia no formato `AAAA-MM-DD`; horários no formato `HH:MM` com dois dígitos. As duas chaves do topo são obrigatórias; `reservas_existentes` pode ser uma lista vazia. Funções de leitura (módulo `reservas/leitura.py`):

```
ler_reserva(dados: dict) -> Reserva
ler_arquivo(caminho: str | Path) -> tuple[Reserva, list[Reserva]]     # (nova, existentes)
```

## 3. Saídas

| Função | Saída |
|--------|-------|
| `Reserva.descricao()` | Texto `"{sala}, {AAAA-MM-DD}, {HH:MM}-{HH:MM}"`, ex.: `"Sala 1, 2026-11-03, 10:00-11:00"` |
| `reservas_conflitam` | `True` se conflitam, `False` se não. Simétrica: `f(a, b) == f(b, a)`. |
| `buscar_conflitos` | Lista nova com as reservas existentes que conflitam com a nova, na ordem em que vieram. Lista vazia se nenhuma conflita. Não altera a entrada. |
| `exigir_sem_conflito` | `None` se não há conflito. Levanta `ConflitoDeReserva` se há. |
| `ler_reserva`, `ler_arquivo` | Objetos `Reserva` prontos e válidos. |

`ConflitoDeReserva` (subclasse de `ErroDeValidacao`) traz o atributo `conflitos` (lista) e a mensagem
`"reserva {nova.descricao()} conflita com: {descricao_1}; {descricao_2}"`.

### Linha de comando: `python -m reservas caminho_do_arquivo.json`

| Situação | stdout | stderr | Código de saída |
|----------|--------|--------|-----------------|
| Sem conflito | `Sem conflito: {descricao da nova}` | vazio | 0 |
| Com conflito | `Conflito: {descricao da nova}` e, em seguida, uma linha `- {descricao}` por reserva em conflito | vazio | 1 |
| Entrada inválida, arquivo ausente ou uso errado | vazio | `erro: {mensagem}` (ou a linha de uso) | 2 |

Linha de uso: `uso: python -m reservas caminho_do_arquivo.json`. Conflito é um resultado esperado do programa, e por isso vai para stdout; só erro de entrada vai para stderr.

## 4. Regras detalhadas

1. Conflito exige mesma sala, mesmo dia e sobreposição de horário (`inicio_a < fim_b` e `inicio_b < fim_a`).
2. Reservas encostadas (fim de uma igual ao início da outra) não conflitam.
3. Reserva contida em outra, que contém outra, ou idêntica a outra conflita.
4. A sala é comparada sem distinguir maiúsculas de minúsculas e sem espaços nas pontas: `"Sala 1"` e `" sala 1 "` são a mesma sala. Espaços internos contam: `"Sala 1"` e `"Sala  1"` (dois espaços) são salas diferentes, e `"Sala 1"` e `"Sala 10"` também.
5. `buscar_conflitos` valida todas as entradas antes de procurar. Se qualquer item de `existentes` for inválido, levanta erro e não devolve resultado parcial.
6. Se `existentes` contiver reservas repetidas que conflitam, cada ocorrência aparece no resultado (não há remoção de duplicatas).
7. Nenhuma função altera seus argumentos nem guarda estado entre chamadas.

## 5. Decisões já tomadas (não reabrir)

| Id | Assunto | Decisão |
|----|---------|---------|
| D1 | Nome da sala | Comparação sem distinguir maiúsculas e sem espaços nas pontas (regra 4). Um conflito não detectado por diferença de caixa seria uma reserva duplicada. |
| D2 | Reserva que passa da meia-noite | Não aceita. O fim é sempre posterior ao início no mesmo dia, então o último horário possível é 23:59. Quem precisa atravessar a meia-noite divide em duas reservas. |
| D3 | Segundos | Horários em minutos inteiros. Segundos ou microssegundos diferentes de zero são recusados. |
| D4 | Fuso horário | `time` com fuso é recusado. Todos os horários são locais da sala. |
| D5 | Edição de reserva | Fora de escopo. A função não sabe qual reserva existente é "a mesma". Para editar, quem chama remove a reserva antiga de `existentes` antes de verificar. |
| D6 | Duração e horário de funcionamento | Sem duração mínima ou máxima e sem horário comercial. Qualquer intervalo de 1 minuto ou mais é válido. |
| D7 | Tipo do intervalo | Meio aberto: [início, fim). |

Qualquer lacuna que não esteja neste contrato é decisão pendente. O agente a registra como `DECISÃO PENDENTE D8, D9...` e não decide sozinho.

## 6. Exemplos

### 6.1 Funcionamento normal

| Reserva A | Reserva B | Resultado | Por quê |
|-----------|-----------|-----------|---------|
| Sala 1, 03/11, 10:00-11:00 | Sala 1, 03/11, 10:30-11:30 | conflito | Sobreposição de 30 min (exemplo do enunciado) |
| Sala 1, 03/11, 10:00-11:00 | Sala 1, 03/11, 14:00-15:00 | sem conflito | Horários distantes |
| Sala 1, 03/11, 10:00-11:00 | Sala 2, 03/11, 10:30-11:30 | sem conflito | Salas diferentes |
| Sala 1, 03/11, 10:00-11:00 | Sala 1, 04/11, 10:30-11:30 | sem conflito | Dias diferentes |

### 6.2 Limites

| Reserva A | Reserva B | Resultado | Por quê |
|-----------|-----------|-----------|---------|
| Sala 1, 10:00-11:00 | Sala 1, 11:00-12:00 | sem conflito | B começa quando A termina (exemplo do enunciado) |
| Sala 1, 10:00-11:00 | Sala 1, 09:00-10:00 | sem conflito | B termina quando A começa |
| Sala 1, 10:00-11:00 | Sala 1, 10:59-12:00 | conflito | 1 minuto de sobreposição |
| Sala 1, 10:00-11:00 | Sala 1, 11:01-12:00 | sem conflito | 1 minuto de folga |
| Sala 1, 10:00-12:00 | Sala 1, 10:30-11:00 | conflito | B está contida em A |
| Sala 1, 10:00-11:00 | Sala 1, 10:00-11:00 | conflito | Idênticas |
| Sala 1, 10:00-10:01 | Sala 1, 10:01-10:02 | sem conflito | Duração mínima de 1 minuto, encostadas |
| Sala 1 | " sala 1 " | mesma sala | Regra 4 |
| Sala 1 | Sala 10 | salas diferentes | Regra 4 |
| 00:00-00:01 e 23:58-23:59 | | válidas | Primeiro e último minutos do dia |

### 6.3 Erros

Todos levantam `ErroDeValidacao`. Mensagens exatas (`{tipo}` é `type(valor).__name__`):

| Entrada | Mensagem |
|---------|----------|
| `fim` igual ou anterior a `inicio` (ex.: 10:00-10:00, 11:00-10:00, 23:00-00:00) | `fim (10:00) deve ser posterior ao inicio (10:00)` (com os horários recebidos) |
| `sala` vazia, só espaços ou que não é str | `sala deve ser um texto não vazio, recebeu ''` (com o valor recebido, usando `repr`) |
| `dia` que não é `date`, ou é `datetime` | `dia deve ser date (sem hora), recebeu {tipo}` |
| `inicio` ou `fim` que não é `time` (inclui `str` e `datetime`) | `{campo} deve ser time, recebeu {tipo}` |
| `inicio` ou `fim` com fuso horário | `{campo} não pode ter fuso horário` |
| `inicio` ou `fim` com segundos ou microssegundos | `{campo} deve estar em minutos inteiros, recebeu 10:00:30` (valor em `isoformat`) |
| `nova` que não é `Reserva` | `nova deve ser Reserva, recebeu {tipo}` |
| `reserva_a` ou `reserva_b` que não é `Reserva` | `reserva_a deve ser Reserva, recebeu {tipo}` (idem `reserva_b`) |
| `existentes` não iterável (ex.: `None`) | `existentes deve ser uma coleção de Reserva, recebeu {tipo}` |
| Item inválido de `existentes` (índice 0 a partir do primeiro) | `existentes[1] deve ser Reserva, recebeu {tipo}` |
| `exigir_sem_conflito` com conflito | `ConflitoDeReserva` (ver seção 3) |

Leitura do arquivo (todos `ErroDeValidacao`):

| Entrada | Mensagem |
|---------|----------|
| Conteúdo que não é JSON | `JSON inválido: {motivo} (linha {n}, coluna {n})` |
| Arquivo que não está em UTF-8 | `arquivo não está em UTF-8` |
| Topo do JSON que não é objeto | `o conteúdo deve ser um objeto JSON, recebeu {tipo}` |
| Chave do topo ausente (`nova_reserva`, depois `reservas_existentes`) | `campo obrigatório ausente: 'nova_reserva'` |
| Chave do topo desconhecida | `campo desconhecido: 'x'` |
| `reservas_existentes` que não é lista | `reservas_existentes deve ser uma lista, recebeu {tipo}` |
| Erro numa reserva | O erro da reserva com prefixo: `nova_reserva: {mensagem}` ou `reservas_existentes[2]: {mensagem}` |
| Reserva que não é objeto | `reserva deve ser um objeto JSON, recebeu {tipo}` |
| Campo da reserva ausente (ordem: sala, dia, inicio, fim) | `campo obrigatório ausente: 'fim'` |
| Campo da reserva desconhecido | `campo desconhecido: 'x'` |
| `dia` fora de `AAAA-MM-DD` ou inexistente (ex.: `2026-02-30`, `03/11/2026`, `2026-11-3`) | `dia inválido: '2026-02-30'; esperado AAAA-MM-DD` |
| `inicio` ou `fim` fora de `HH:MM` ou inexistente (ex.: `10h`, `9:00`, `10:00:00`, `25:00`, `10:60`) | `inicio inválido: '25:00'; esperado HH:MM` |

Arquivo inexistente ou ilegível: `ler_arquivo` deixa a `OSError` do Python subir; a linha de comando a captura e imprime `erro: {mensagem}` com código 2.

## 7. Exemplos de arquivos (pasta `exemplos/`)

| Arquivo | Resultado esperado |
|---------|--------------------|
| `agenda_livre.json` | `Sem conflito: Sala 1, 2026-11-03, 11:00-12:00`, código 0. A nova reserva encosta nas duas vizinhas, sem sobrepor. |
| `agenda_com_conflito.json` | Código 1, stdout: `Conflito: Sala 1, 2026-11-03, 10:30-11:30`, `- Sala 1, 2026-11-03, 10:00-11:00`, `- Sala 1, 2026-11-03, 11:15-12:00`. Outras 3 reservas existentes (09:00-10:00, outra sala, outro dia) não conflitam. |
| `agenda_invalida.json` | Código 2, stderr: `erro: nova_reserva: fim (10:00) deve ser posterior ao inicio (11:00)`. |

## 8. Módulos e testes

| Módulo | O que contém | Testes |
|--------|--------------|--------|
| `reservas/erros.py` | `ErroDeValidacao`, `ConflitoDeReserva` (já pronto) | coberto em `test_conflitos.py` |
| `reservas/reserva.py` | `Reserva` e sua validação | `tests/test_reserva.py` |
| `reservas/conflitos.py` | As três funções de conflito | `tests/test_conflitos.py` |
| `reservas/leitura.py` | `ler_reserva`, `ler_arquivo` | `tests/test_leitura.py` |
| `reservas/__main__.py` | Linha de comando | `tests/test_main.py` |

Observação do solicitante: o contrato acima é tudo o que foi definido. O que não estiver nele é decisão pendente.
