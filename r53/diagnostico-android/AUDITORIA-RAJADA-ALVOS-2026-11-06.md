# Revisão da PR75 e auditoria de alvos · 06/11/2026

A PR75 `af22de9` está aberta para revisão, sem conflitos com a PR74,
com dois checks aprovados. Passaram a conferência de diff, o teste
de tempo dos feitiços com replay do transporte (108 células em 36
cartões) e Prática Cotidiana (1.003 verificações).

A auditoria nativa nas descartáveis Era e Ciclo usou o primeiro cartão
de feitiço comum com a PR75, Classe 3 e a R66 de
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

## Achados

| Montagem | Resultado nas duas cópias | Regra da R66 |
| --- | --- | --- |
| Explosão, 2d8 de dano e Rajada | VÁLIDO, sem aviso; 2 tiros calculados | Rajada exige Forma de alvo individual com ataque. |
| Projétil, 4d8 de cura e Rajada, sem dano | VÁLIDO, sem aviso; 0 tiros calculados | Rajada exige ao menos um dado de dano por tiro. |
| Projétil, 2d8 de cura, Guarda e Tudo ou Nada, sem dano | VÁLIDO, sem aviso; a Restrição devolve 2 pontos e o saldo chega a 5 | A Restrição só cabe quando o sucesso em TR reduziria o dano à metade. |

O cartão usa `registro_livre=True` em `ficha-v01/cartoes_diretos.py`.
Em `r53/modelo.py`, o filtro pelos prefixos “Rajada exige” e
“Tudo ou Nada exige” suprime avisos inteiros. Cada aviso combina
uma condição que depende da descrição (ataque ou TR) com condições
já conhecidas pela ficha (área e presença de dano). A devolução é
independente do aviso e a rota direta fixa as duas flags de validade
das Restrições em verdadeiro.

A correção deverá separar as condições que a ficha consegue verificar
da adjudicação escrita em COMO É. Para Tudo ou Nada sem dano, é preciso
conferir o aviso e a devolução nas duas posições de Restrição.

## Controles e preservação

- Rajada em Projétil calculou 4 tiros com 6 dados e 1 tiro com 1 dado.
  Em Toque, calculou 3 tiros com 3 dados.
- Duas compras de Mais Um em Projétil contabilizaram três destinatários.
  A ficha rejeitou a terceira compra e a combinação com Explosão.
- Foram nove cenários por cópia, com entradas temporárias e marcador
  de preparação no Google Sheets. O teste conferiu cálculo e validade
  do cartão, sem rolar ataques, dividir dados em mesa ou executar
  eventos de edição. A primeira leitura de Tudo ou Nada foi
  descartada porque o rótulo do ensaio foi escrito na Classe. O
  resultado documentado vem da repetição com Classe 3 numérica.
- Foram restauradas 12 entradas por cópia. A releitura de 319
  células em cada cópia, incluindo 259 posições de MONTAGENS,
  confirmou os valores, as fórmulas, as notas e as validações, sem
  diferenças ou erros nos intervalos.
- Evidência privada em `nuvem-b47/saidas/auditoria-rajada-alvos/`.
  Nenhuma alteração de fórmula ou Apps Script nesta auditoria.
