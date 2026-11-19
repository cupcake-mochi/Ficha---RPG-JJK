# Carregar, Armado e duração de Guarda · 06/11/2026

Base PR74 em `758c571`. A referência é a R66 em
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, nas
entradas Carregar, Armado, Guarda e Concentrada/Duradoura.
Diagnóstico em `AUDITORIA-TEMPO-FEITICOS-2026-11-06.md`.

Nos 36 cartões comuns, Carregar identifica a Ação Padrão e o PE no
preparo e mostra a ação de disparo no turno seguinte. Armado mostra
o custo ao armar e indica que o gatilho resolve sem Reação. Os
resumos de montagens inválidas conservam seus avisos. Se a
Integridade bloquear a conjuração, aparece o motivo da restrição.

O texto interno e o aviso visível de Guarda usam o mesmo prazo.
Concentrada mostra até 10 minutos com concentração e lembra o menor
prazo da montagem. Com um estado curto reconhecido, como Firmeza,
mostra 1 minuto com concentração. Duradoura mostra 1 minuto.
O texto normal de Guarda permanece para montagens sem prolongamento.
Os textos informam as ações e prazos. A execução na mesa continua
a cargo de quem joga.

## Ensaio nativo

Passaram 14 cenários por descartável, Era e Ciclo. Controles
incluíram ação padrão, Rápido, Reação, Atrasar, combinações inválidas
e impedimento por Integridade. Resultados focais:

- Carregar com Rápido mostrou Padrão + 9 PE no preparo e Bônus no
  próximo turno.
- Armado no estágio 2 mostrou Padrão + 12 PE ao armar e gatilho
  sem Reação. O custo base continuou em 9 PE.
- Guarda sozinha com Concentrada mostrou até 10 minutos, com
  Duradoura mostrou 1 minuto, e com Firmeza e Concentrada mostrou
  1 minuto com concentração. O texto interno deixou de apresentar
  o prazo normal nas três montagens válidas.
- Armado com Carregar e Concentrada com Duradoura mantiveram os
  avisos de incompatibilidade.

Código e Editor foram salvos, reabertos e relidos nas duas cópias.
A fórmula de execução `FICHA AMALDIÇOADA!D81` e a fórmula interna
`DADOS_R53!FD2` voltaram após edição real na Era. O aviso visível
`FICHA AMALDIÇOADA!E82` voltou após edição real no Ciclo.

As 13 entradas temporárias foram repostas e a aba interna voltou a
ficar oculta. A releitura conferiu 426 células por cópia, incluindo
259 posições de MONTAGENS. Somente as 108 fórmulas previstas
diferiram, com notas e validações preservadas e sem erros nos
intervalos. Evidência privada em
`nuvem-b47/saidas/correcao-tempo-feiticos/`.

## Preparação incremental

Geração `8b5cc6b4e78f44af`. São 108 fórmulas, com 72 resumos e
avisos visíveis e 36 descrições internas. A comparação do pacote
integral conferiu 280.001 posições e os metadados de 26 abas.
Apenas as 108 fórmulas previstas mudaram. Passaram os 99 checks do
smoke local.

`preparar_tempo_feiticos.js` exige o Código e o Editor ensaiados
na PR74 e um snapshot atualizado das 108 fórmulas. Produz somente
gravações de `userEnteredValue` e plano reverso. O Editor conserva
os 251 contextos. As fórmulas internas entram na rota de recuperação
que restaura somente as células calculadas atingidas pela edição.

Hashes SHA-256 relidos nas duas descartáveis:

- Código `21a59ce691bdd38162688485b9a1222476b469a500d09d055c99e97d07c26923`.
- Editor `676337f165f7056db20364e5327f2793e957d2db405199a75009f5f44a163c49`.
