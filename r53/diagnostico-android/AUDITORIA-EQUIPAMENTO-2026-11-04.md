# Auditoria de equipamento e Defesa sem Armadura

Base da ficha: PR63, commit `4a2fb40`. Livro: R66, commit
`e3058ad29180fdec2efec75b512446c49bf87b3d` de
`cupcake-mochi/JJK---Project`, seções Propriedades, Mãos disponíveis,
Proteção, Carga e Defesa sem Armadura.

A fila consolidada A00–A09 tem correções preparadas nas PRs 60–63.
Esta rodada usou as duas descartáveis de Integridade e Vigília, Era e
Ciclo. Rodaram 17 cenários de recálculo nativo em cada cópia, usando as
fórmulas das próprias fichas. Duas reproduções também passaram pela
interface de edição na Era, além do teste da caixa de treino. O
diagnóstico abaixo permanece aberto para correção.

## Achados confirmados nas duas descartáveis

| ID | Reprodução e resultado | Causa observada |
|---|---|---|
| E01 | Katana na mão principal, escolha Nas duas mãos na secundária. DADOS!CZ12 marca 1, mas CZ13 e FICHA PESSOAL!D66 continuam em `1d8`. A R66 prevê `1d10` nesse caso. | A fórmula de dado em uso compara com `d8` e recebe `1d8` do catálogo. Controle com uma mão mantém `1d8`. A seleção também foi feita por edição real na Era. |
| E02 | A quantidade −10 da Katana é aceita, gera volume −10 na linha e reduz a carga total de 5 para −6. Com quantidade zero, o escudo Médio perde seu 1 de Volume, mas continua em uso com proteção +2, teto de Destreza 3 e indicação de Selo de gesto travado. | A quantidade na tabela multiplica o Volume sem uma guarda de domínio. Os menus e a conta da mão também deixam um item com quantidade zero disponível. A quantidade negativa foi digitada pela interface na Era. A nota do cabeçalho diz que quantidade em branco vale 1. |
| E03 | Com uma única Katana registrada em quantidade 1, a ficha aceita Katana nos dois seletores e mostra uma arma em cada mão, com o volume de uma só. `Nas duas mãos` é outra opção do menu. Com quantidade 2 e as duas seleções, o volume sobe corretamente em 1. | As listas e a verificação de uso não descontam uma unidade já empunhada na outra mão. A falta de controle também aparece com uma quantidade positiva válida. |

Ao trocar a linha do Tanto por um Espadão ou apagar a linha do Tanto
já selecionado na secundária, a seleção antiga fica visível e a ficha
avisa que o Tanto não está guardado. O indicador interno da mão
secundária continua em 1, mas o Tanto some do detalhe e não fornece
proteção ou penalidade de Força nesses casos. Essa inconsistência de
estado é um caso de regressão para o tratamento de estoque. Não foi
contada como um quarto erro mecânico confirmado.

## Controles conformes

- Com Destreza 4, Traje 2 e escudo Médio, a Defesa foi 17
  (10 + 3 de Destreza + 4 de proteção). Força 0 manteve a proteção,
  avisou do requisito 3 e deixou movimento em 4,5 m. O limite de carga
  também estava excedido nesse cenário e a metade foi aplicada só uma vez.
  Ao subir a Força para 3, a Defesa continuou 17 e o movimento voltou a 9 m.
- Espadão na mão principal bloqueou a contribuição do escudo na secundária
  e retirou sua proteção e a indicação de Selo de gesto travado.
- Com limite de carga 8, volume 16 ainda permitiu 4,5 m. Volume 17 zerou
  o movimento.
- Na rota Sem Energia, nível 22 produziu Lapidação 6 nas duas fichas.
  Defesa sem Armadura resultou em proteção 3 e Defesa 17. Com o escudo
  Médio, proteção 5 e Defesa 18. Ao vestir Traje 2, a proteção passiva
  foi substituída pela do Traje: proteção 4 e Defesa 17 com o mesmo escudo.
- Na Era, marcar e desmarcar Lâmina Longa por edição real preencheu e
  limpou as oito caixas do grupo. Esse teste cobre um grupo nessa cópia.

## Testes e restauração

O teste histórico B01 (`menu_origem.js`) passou com as 26 abas do
commit `b7f323c` contra sua base `93a109c`, com somente CP3/CQ3 alteradas.
Ele continua histórico. O verificador focal da versão atual também
passou nas 19 verificações. Os testes históricos `cartas_custom.js` e
`marcas_custom.js` seguem fora da cobertura deste ensaio.

Foram restauradas e relidas 23 entradas na Era e 15 no Ciclo, incluindo
a seleção de Origem, nível, inventário, atributos e caixas de treino.
Os valores inseridos e as regras de validação coincidiram com os
snapshots. A nota dinâmica da arma principal da Era foi restaurada e
relida. Defesa e movimento voltaram aos valores e fórmulas iniciais.
As leituras de recálculo por API não disparam onEdit. As edições reais
citadas foram feitas separadamente na interface do Google Sheets.

Sem alterações de produção, merge, oficiais, jogador, PR31 ou acionadores.
A cobertura em aberto ainda inclui outras Bênçãos e imunidades
condicionais, usos por cena/descanso e a aplicação em combate de
penalidades de custo e Classe que a ficha atualmente informa.
