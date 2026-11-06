# Instalação da PR76 e auditoria de Frágil e Fica · 06/11/2026

## PR76 nas descartáveis

A PR76 `4911da8` está sem conflitos e com os dois checks aprovados.
A Era e o Ciclo estavam no Código e nas fórmulas da PR75. O Código
anterior foi guardado em arquivo privado e comparado por hash com
cada projeto. A leitura prévia das 1.004 fórmulas por cópia passou
pela guarda de versão do preparador. O EditorR53 foi relido e
permaneceu com o hash da PR75.

As 1.004 fórmulas da PR76 foram instaladas em 21 lotes por cópia,
nas colunas CK, CP, EH e FX de DADOS_R53. Cada lote foi relido antes
e depois da gravação. Não houve divergência, erro de fórmula ou
mudança de nota/validação nos alvos. A planilha ficou com a PR76
instalada após os ensaios.

O Código.gs foi salvo e relido integralmente nas duas cópias.
SHA-256 do Código após aplicação
`6062ac46cffe8386d03a3c6fa6d991f1445e948211953783a21febecc1e6f769`.

As fórmulas apagadas pela interface voltaram sem intervenção:

| Cópia | Cartões comuns | Classe 0 |
| --- | --- | --- |
| Era | CK2 e FX2 | CK252 |
| Ciclo | CP2 e EH2 | FX253 |

As seis execuções do acionador simples `onEdit` concluíram no Apps
Script e as fórmulas relidas coincidiram com a proposta. DADOS_R53
voltou ao estado oculto e a célula temporária de transporte voltou
ao vazio. As 594 células de controle relidas por cópia, incluindo
532 posições de MONTAGENS, coincidiram com a leitura anterior.

## Pente-fino

O ensaio usou a R66 do livro em
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d` e o
primeiro cartão comum de cada descartável já com a PR76.

- **Frágil com Precisão como única Melhoria.** Em Projétil de dano
  Classe 3, declarar 2 pontos interrompíveis deixou o cartão em
  VÁLIDO, sem aviso, e devolveu 2 pontos. O saldo subiu de 7 para 9.
  A R66 cita Precisão como exemplo de Melhoria que não financia
  Frágil. O cálculo limita o valor manual ao preço Leve e alerta
  quando ultrapassa o total pago, sem verificar se alguma Melhoria
  escolhida deixa efeito interrompível. Os controles com Guarda,
  com zero declarado e com declaração superior ao custo tiveram
  o comportamento previsto.
- **Fica quando a área termina com zero dados.** Em Explosão
  Classe 4, Fica com Toca a Alma e 1 ponto em dano deixou o cartão
  em VÁLIDO, sem aviso, mesmo com 0d8 após o arredondamento.
  O aviso atual de Fica testa a Forma e a função de dano escolhida,
  sem conferir a saída efetiva. Com 2 pontos e 1d8 restante, o
  cartão continuou válido. Fica em Projétil de dano e em Linha só
  de cura foi rejeitado. Explosão com dano comum passou.

Foram nove cenários por cópia. As 15 entradas temporárias foram
repostas. A releitura de 599 células por cópia, incluindo 532
posições de MONTAGENS, encontrou zero diferenças e zero erros.
As divergências acima são diagnósticos. As fórmulas de Frágil
e Fica seguem as da PR76.

Evidência privada em `nuvem-b47/saidas/instalacao-rajada-alvos/`.
