# Revisão da PR71 e auditoria de Classe 0 · 06/11/2026

A PR71 em `c54f74a` estava aberta, sem conflito com a PR70 em
`4324ad3`, com os dois checks do GitHub aprovados. A revisão conferiu
os limiares e os efeitos cumulativos contra a R66, o delta de 41
fórmulas e a recuperação dos cartões sem alterar as montagens. Passaram
os testes locais de conjuração, Integridade/movimento, Prática Cotidiana
(992 verificações) e Socorro (101). O replay usou o snapshot privado do
código anterior. Nenhum bloqueio encontrado no escopo da PR71.

## Ensaio nativo de Classe 0

Quatro rodadas de cálculo em cada uma das descartáveis Era e Ciclo da
PR71. Os resultados foram iguais nas duas. Foram exercitados dano base,
Empurrão, Queima-Roupa em Projétil e Explosão, Impulso individual à
distância e com Toque, tentativa coletiva, Restrição sem Melhoria e
contagem de repertório com e sem Prática Cotidiana. A regra de
referência é a seção Feitiços de Classe 0 da R66 em
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

| Caso | Esperado | Observado nas duas cópias |
| --- | --- | --- |
| Projétil sem Melhoria | 2d8 no nível 2, 3d8 no nível 5, 6d8 no nível 25 | Conforme, 9 m e 0 PE |
| Projétil com Empurrão | Retira um dado | 1d8 no nível 2 e 2d8 no nível 5 |
| Empurrão e Queima-Roupa em Explosão | Recupera o dado e centra a área no conjurador | 3d8 no nível 5, válido, raio 3 m |
| Queima-Roupa em Projétil e Atrasar sem Melhoria | Recusar Restrição Média | As duas montagens receberam aviso e ficaram inválidas |
| Impulso individual com Toque | 1,5 m, sem dano | Conforme |
| Impulso coletivo em Explosão | Montagem inválida | Inválida, com aviso de que Classe 0 não aceita benefício coletivo |
| Impulso individual com Projétil | 4,5 m, sem dano | **9 m e montagem válida**, nas vagas comum e extra |
| Cinco Classe 0 comuns no nível 2, sem Prática Cotidiana | Máximo de dois | O resumo acusa **5 de 2**, mas os cinco cartões continuam válidos individualmente |
| Três comuns e dois extras no nível 5 com Prática Cotidiana | Cinco válidos, sem excesso | Conforme. Com sete nomes no nível 5, os extras recebem o aviso individual |

## Pontos para corrigir em separado

- O resumo de alcance de Classe 0 reutiliza o alcance ofensivo em
  `ficha-v01/montagens_r53.py`. O erro aparece em
  `FICHA AMALDIÇOADA!R326` e `R566`, com validade verdadeira em
  `DADOS_R53!FY44` e `FY252`. Ao corrigir, distinguir benefício
  individual de dano e de utilidade fora de combate. Conservar o
  alcance de Toque e o aviso de aplicação coletiva inválida.
- `DADOS_CUSTOM!B135:B136` conta os nomes e informa excesso. Na
  condição testada, `DADOS_AM!HM10` indica 2,
  `FICHA AMALDIÇOADA!D328` avisa 5 de 2 e
  `DADOS_R53!FY41:FY45` continua verdadeiro. O gerador da PR70
  aplica a guarda de quantidade individualmente às vagas extras.
  A correção do feedback dos cartões comuns deve preservar as
  montagens e permitir que o jogador escolha quais manter no limite.

## Evidência e limites

As entradas foram aplicadas pelo conector. O cálculo é nativo, com
sete marcadores de preparação usados como dados de teste e restaurados.
O ensaio não exercitou o evento de edição que prepara uma versão nem
o fluxo de execução do feitiço. Foram repostas 44 entradas por cópia.
A releitura comparou 156 células por cópia, incluindo valores, fórmulas,
notas e validações, sem diferenças e sem erros nos intervalos.
Snapshots privados em `nuvem-b47/saidas/auditoria-classe-zero/`.
Nenhuma mudança de implementação ou publicação nesta auditoria.
