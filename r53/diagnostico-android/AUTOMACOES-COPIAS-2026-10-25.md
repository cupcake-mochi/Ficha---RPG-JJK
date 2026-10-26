# Automações nas cópias · entrega de 25/10/2026

Aplicado incrementalmente nas **duas oficiais de `r53/OFICIAIS.md`**, após snapshots
nativos e ensaio em cópia recém-criada. Não executar construir/continuar nem
reaplicar o preparador. A cópia preenchida apontada pelo usuário foi descartada
por ele e ficou fora da aplicação.

## Problema e comportamento corrigido

Escolher Caminho deixava as perícias desmarcadas e as habilidades vazias. O
acionador simples esgotava seu orçamento antes de concluir. A cópia nova ainda
iniciava uma sincronização de 249 cartões em uma edição da FICHA; o carregador
também podia chamar o editor duas vezes. As caixas grandes de treino em armas
passavam pelo carregador geral.

Caminho, Trilha e treino agora usam as mesmas 29 funções de regras extraídas de
Codigo.gs, com uma área interna de **653 referências**. `R53_EVENTOS` fica oculta,
tem 654 linhas e duas colunas e conserva os tipos e as células vazias das entradas.
O evento lê esse retrato uma vez, calcula em memória e agrupa as gravações. Os
textos manuais das habilidades são preservados e as notas continuam mostrando o
texto do livro quando necessário. A troca de Caminho também mantém a limpeza de
Trilha incompatível e o treinamento em armas correspondente.

O catálogo do EditorR53 é materializado sob demanda a partir do mesmo JSON,
conferido por hash. Os 249 contextos permanecem iguais. Edições da FICHA deixam
de iniciar a sincronização de Famílias; essas escolhas ficam nas outras abas.

## Aplicação e releitura

- `Codigo.gs` instalado: SHA-256 `d92f846e42aa1ad42237ced54da53772d6aa796ae580c90b84fa718a980c5827`.
- `EditorR53.gs` instalado: SHA-256 `bc3004641a1a28c148885638955e6db66ffebaa01cd8acea30415cbbcd30e993`.
- Catálogo JSON do editor: SHA-256 `e4502f595c23edb8807c7241f330fa481599b6ec2ef687e9b2ce440ade3ddce8`.
- Esquema do retrato: `R53_EVENTOS_1`, hash
  `2b6c1de10e696fb99cf4872d9368d5ecfcd768a1725fb4daeef5637078d0348f`.

Os dois projetos foram reabertos. As quatro releituras foram idênticas às
propostas. As duas áreas internas foram relidas integralmente, com 654 linhas
cada e nenhum `errorValue`. Não se preencheram personagens nas oficiais para
testar. As abas antigas, entradas, fotos, salários e ANALISE A:D não foram
reescritos. ANALISE12/esquema2, doze invocações e nove posições de Família
permanecem com os mesmos endereços.

O pacote-base instalado continua `e142593fdc5be157`, com os incrementos já
publicados. **O pacote integral regenerado não foi instalado.** A fonte atual
produz nove arquivos, 26 abas de dados e 249 contextos; a nova aba física soma-se
às extensões já existentes, totalizando 30 abas nas oficiais. A geração-base dos
dados continua `7f85d740f71c4cb6`. Os rótulos públicos continuam em 1.0.

## Validação

Simulação integrada: 52 verificações, cobrindo os seis Caminhos, textos manuais,
Caminho/perícia/habilidade custom e ida/volta dos grupos de armas. O teste também
confere que não há leitura depois de começar a gravação. As 29 funções de regras
são conferidas contra a fonte; as mudanças de leitura e agrupamento ficam em
`r53/caminho_io.gs`. Há testes de células mescladas, recusa de colagens fora da
área, preservação do evento, hash, catálogo completo e inicialização adiada.

As 568 verificações do editor passaram com a fonte normal e com o transporte
comprimido. As 74 verificações de recursos/cartas e os sete testes do contrato
passaram. O pacote foi conferido sem diferença de estado.

Prova Google, todos eventos simples concluídos na cópia de QA:

| Caso | Duração registrada |
|---|---:|
| Emanador: perícias e texto completo de Desdobramento Técnico | 12,259 s |
| Condutor Armado: habilidades da Trilha | 13,595 s |
| Cartão: ponto gravado em MONTAGENS | 20,303 s |
| Cartão: ponto restaurado e relido como zero | 20,917 s |
| Vanguarda: Acrobacia, Percepção, Trilha incompatível limpa e habilidade de 6.251 caracteres | 11,191 s |
| Grupo Arma de Fogo: desmarcação propagada às armas | 16,756 s |

A marcação manual de Lâmina Curta também foi conferida no Google. A conferência
visual mostra as outras categorias marcadas e Arma de Fogo com suas armas
desmarcadas. As tentativas anteriores que esgotaram o tempo ocorreram somente
na QA, antes da solução final.

## Limites e revisão seguinte

Esses tempos são de execuções no Google nesta sessão, não medidas de RAM ou
garantia de resposta no Android. A latência inicial da troca de cores não foi
medida novamente; seu algoritmo foi preservado. Não afirmar “100% sem erros” nem
resposta instantânea de todas as automações. Sequências rápidas de edições
concorrentes merecem revisão específica.

## Revisão do Claude: Caminho e Trilha em sequência rápida

A execução do Caminho lê o retrato no começo e grava uns 10 s depois. Uma Trilha
escolhida nesse meio-tempo era apagada, com as cartas dela: Emanador +
Ressonante → Bastião, e Muro escolhida durante a execução, terminava em
"Escolha sua Trilha" com as quatro cartas vazias.

Corrigido em `r53/caminho_io.gs` (`r53TrilhaTrocada_`): só quando vai limpar a
Trilha, a execução do Caminho relê aquela célula. Se o jogador já trocou, ela
não grava a Trilha, as nove cartas (nome, texto, nota, altura) nem
`DADOS_PROGRESSAO!CB2:CC10`, porque a execução da Trilha recalcula tudo isso com o
Caminho novo. Perícias, treino e "trocou por arma" seguem gravados. Sem troca
pendente, a única leitura a mais é essa célula; personagem novo e mesmo Caminho
não leem nada a mais.

`r53/testes/caminho_corrida.js` (17 verificações) compara a corrida com as duas
escolhas feitas uma de cada vez, em três trocas, e reprova sem o descarte.
`Eventos.gs` e a `R53_EVENTOS` não mudam. **Ainda não aplicado nas oficiais:** o
`Codigo.gs` delas é o anterior com o `Caminho.gs` no fim; trocar só esse bloco dá
SHA-256 `e9b20182947bb98b39a629d98d8e8dcead07e1b4116146731047d35c3dce404c`
(arquivo pronto em `r53/saidas/caminho-corrida/Codigo.gs`, ignorado pelo Git).
Continua aberto o caso sem limpeza: personagem novo cuja Trilha termina antes do
Caminho gravar. As cartas visíveis ficam certas, menos a do nível 7 em Incursor +
Pugilista (a única versão "Caminho com a Trilha" do livro), que volta ao texto só
do Caminho. O registro oculto `CB2:CC10` perde as quatro linhas da Trilha; para
texto do livro isso não pesa, porque ele é reconhecido pelo livro inteiro, mas
um texto de Trilha custom passaria a ser tratado como texto do jogador. Fechar
isso pede a mesma releitura em toda troca de Caminho.

Novas cópias das oficiais recebem o incremento. Cópias antigas não herdam
automaticamente o código novo. Ao mudar layout ou os campos necessários aos
eventos, regenerar `Caminho.gs` e `Eventos.gs` com `node r53/caminho_leve.js`;
o empacotador também faz essa atualização. O esquema recusa referências
divergentes. Não adicionar ou deslocar posições do contrato ANALISE.

Snapshots, códigos nativos completos, capturas e registros de execução estão em
`nuvem-b47/saidas/pericias-caminho-20261025/`, ignorado pelo Git. Nenhum acionador,
permissão ou acesso foi criado. O usuário autorizou a aplicação; revisão do Claude
pode partir desta entrega, mantendo os limites do repositório.
