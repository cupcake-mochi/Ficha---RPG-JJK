# Ensaio da rodada nas oficiais · 16/11/2026

**Ensaio pendente: instalação e testes nativos não iniciados.** Este relatório registra um checkpoint, não aprova a rodada nas oficiais.

Pedido do Mizuki: “leia o promtp acima e siga as instruções”, com o roteiro “Ensaio da rodada nas oficiais, numa cópia fria de cada uma”.
Base após `git fetch`: `codex/corrige-colagem-atributos-20261108`, commit `7357c36`.
Ramo deste relatório: `codex/ensaio-rodada-oficiais-20261116`. Nenhum merge.

## O que foi feito

- Lidos o roteiro anexado, o plano completo de 16/11 e o registro atualizado das oficiais, incluindo o aviso âmbar já aplicado.
- Usado um checkout independente. O clone antigo tinha um `alternates` apontando para um caminho Linux inexistente no Windows; esse arquivo não foi alterado.
- Localizado o pacote privado em `02-RPG/_trabalho/rodada-oficiais-20261116/` no HD.
- Relidos os 42 artefatos da Fase 0 e comparados com os respectivos hashes de `fase0/manifesto.json`: 42 iguais. Não houve nova execução dos 42 preparadores.
- Descompactadas as cinco partes locais do módulo e conferido seu SHA-256 integral: `bd42b5351ec1d299e9e54ecd8281de5d75ee129f01fd3c8e4475b5c6fc9e066e`.
- Conferido o arquivo local `referencia/Codigo-molde.gs`: `b3ed2f7e7b804e7db4c724822034c0839c688fb1733ea38cf338170a475e52f8`.
- Criada a cópia nativa completa “ENSAIO rodada 16-11 · Era (descartável)” pelo `files.copy` do Drive, na conta Gustavo Henrique. Foi usado o conector em lugar do menu Arquivo > Fazer uma cópia. A cópia levou o projeto vinculado, aberto a partir de Extensões > Apps Script.
- A interface da cópia mostrou “Apenas eu posso acessar”. Nenhuma permissão foi alterada.
- Lidos os metadados da cópia: 30 abas, `pt_BR`, INVOCAÇÕES com quatro regras e aviso ± no índice 0. Os dez arquivos esperados estão visíveis no editor.

Origem Era `1MQqhHbI…`; cópia Era `18Yj-2ya…`; projeto da cópia `1bikx37d…`. Links completos somente nos arquivos privados.

## Impedimento observado

O Brave bloqueou a colagem da expressão de leitura dos hashes no console de desenvolvedor com o aviso Self-XSS, solicitando que o usuário digite `allow pasting`.
A expressão só leria os modelos Monaco e calcularia SHA-256, sem alterar o projeto. Sua execução não foi confirmada e nenhum resultado de hash do Google foi obtido.

Foi solicitada a liberação manual ao Mizuki. O aviso não foi contornado, e não foi observado pedido de autorização do Google.
O console e a cópia foram mantidos disponíveis para a retomada.

## Hashes relidos localmente, por passo

Esta tabela prova somente a integridade dos arquivos privados recebidos. “Igual” compara o SHA-256 relido com o manifesto; não representa instalação nem releitura no Apps Script.

| PR | Artefato | SHA-256 esperado e relido | Resultado |
|---|---|---|---|
| #57 | `Codigo-57.gs` | `8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0` | igual |
| #60 | `Codigo-60.gs` | `6aec0d0a1e88f777475bc7578fc231c982f0d9b08783c6e8fbe90becdf920455` | igual |
| #61 | `Codigo-61.gs` | `5b81e86d0d5f06d648d9ae91af23dfee435aa6b3aec57c677b15309a3f750cb8` | igual |
| #62 | `Codigo-62.gs` | `3767fb0f19079bc1fbb1bb04d62be97d26cc4a92f00b04431dd4129551b33aa7` | igual |
| #63 | `Codigo-63.gs` | `9f64aa8c47ee6ecd0b0093a08c1434e55ba6eb711f887117ba821611be431631` | igual |
| #64 | `Codigo-64.gs` | `a09bf672a520e0750d239386f23f14e300eda84094668b7771cee605e028ebac` | igual |
| #65 | `Codigo-65.gs` | `19ae4c19660ce322f6cf3df8041469f8a65a7cfa18a9260c7c32f2c760ec77ac` | igual |
| #66 | `Codigo-66.gs` | `d5845c0367be94e63f12b799053d5432d0ec4af5beea3a3d05bf32b607a2a084` | igual |
| #67 | `Codigo-67.gs` | `bae62817a2ae03281dff1247c7e2f97d6ac0518a6f90271bf6de96da98a09130` | igual |
| #69 | `Codigo-69.gs` | `4b0d2cc1952ac3726a47a1969c66c04e30658f7397a927f7af0930615ee9daa9` | igual |
| #70 | `Codigo-70.gs` | `50f3aa55662adc7251a9be91cae4aace316c84ec3df3f53af471c841094b633b` | igual |
| #70 | `EditorR53-70.gs` | `98413975988095b99da8f260c7295b09d00f7f40ae85b4f14ec86f9e88ed6844` | igual |
| #71 | `Codigo-71.gs` | `6b22b689b1940dd22c8a5a0ba1143becf74c01446afb502dc5633da1d62dd6e8` | igual |
| #71 | `EditorR53-71.gs` | `165fc80d4f3f32c344195541b888662bda86e503e0b3ab615362ffd610403466` | igual |
| #72 | `Codigo-72.gs` | `e45999e3cbea477b5357434ffeda418038c8228a7c316bc0dcdab8bf8c4f7c5e` | igual |
| #72 | `EditorR53-72.gs` | `13cf7ddf5601ef1056e9f5717cb1dcff0dfd1046263dcd384bd69684d791cd55` | igual |
| #73 | `Codigo-73.gs` | `5c8c7493600367d4c004c3c85a4cc0f5e82459ec4cb4a54ccdb1c769741e3a2c` | igual |
| #73 | `EditorR53-73.gs` | `aa77309cb42e08f49dbe1f427c72b0c68ec6168fbf6b2294d4d3555a7a7b5c09` | igual |
| #74 | `Codigo-74.gs` | `2005362b35c236dc17f241ace10d5bb075f61ec7662a1fe234fa1b5216a83e9b` | igual |
| #74 | `EditorR53-74.gs` | `2ed5d1e18726708fcf4d08daa9a674d9996ccf7477bcedcbcfad0c54887fe928` | igual |
| #75 | `Codigo-75.gs` | `21a59ce691bdd38162688485b9a1222476b469a500d09d055c99e97d07c26923` | igual |
| #75 | `EditorR53-75.gs` | `676337f165f7056db20364e5327f2793e957d2db405199a75009f5f44a163c49` | igual |
| #76 | `Codigo-76.gs` | `6062ac46cffe8386d03a3c6fa6d991f1445e948211953783a21febecc1e6f769` | igual |
| #77 | `Codigo-77.gs` | `cc5b05bf9de303804a1726d583934526162b1eece43e255ddc126fd6f3ba28cd` | igual |
| #78 | `Codigo-78.gs` | `01e6422424022d301f994c2dbae84ee630849d81e36ec80c41df04bee6db134e` | igual |
| #79 | `Codigo-79.gs` | `30306ed099e1ae5d88bf42e7a6e48af093f4f84aa719f36fc3fd0231c26b5658` | igual |
| #80 | `Codigo-80.gs` | `9fc4f2eb1e265f34f8a261001a503eb21c6b8737ced6c399129f32bc4e2c0c05` | igual |
| #81 | `Codigo-81.gs` | `e44e7f0c929fec0fca6ef65a6670937dd7d4278e47dbaedde9d18278dc4eb45f` | igual |
| #82 | `Codigo-82.gs` | `ec0bbd157b7b3bf10b8aee6252896971d0332ae1788f4d7a3b2f13d6928acc75` | igual |
| #83 | `Codigo-83.gs` | `cf8dc5960121fcc4677f4b19288932ee738be39e2d6d2a61a10d1a3f3ef59672` | igual |
| #84 | `Codigo-84.gs` | `da89202e8a7af2029855196dc464ef4091d2174393a954860cb5381d8ee5709e` | igual |
| #85 | `Codigo-85.gs` | `7512bf622897eb1145f3849a55ccd80419a147e8cd540a3c2b6113d84c8cdfb7` | igual |
| #86 | `Codigo-86.gs` | `5b7bb420739efeeb28e036b8da79f38bcc0e19b20d4d14f229f0effaac74e7ef` | igual |
| #87 | `Codigo-87.gs` | `26b78470c8eda2443ee74f650b5a925cde1fdbeea7a79c8387c3304e9767968c` | igual |
| #88 | `Codigo-88.gs` | `36ca73efd1eca6809fd8ddfa1be324eebaad2f5aef0830d4c25c6aaeaaaff3bc` | igual |
| #89 | `Codigo-89.gs` | `ffd349c9299342d735917697355d3f278f526ff74b9e009706ce61a8b0784352` | igual |
| #90 | `Codigo-90.gs` | `b709ad14b6340c132279f5a44030cb9a737c3f1251322c9929c6ffd341d9f38e` | igual |
| #105 | `Codigo-105.gs` | `0292582a1fffaa7a328980e14bac39830e67cd58e6d48a0563bc665854193463` | igual |
| #107 | `Codigo-107.gs` | `b5861c145394db8ce803304699776986300c121ca0a9ce2f9264edeed3ae4ed5` | igual |
| #108 | `Codigo-108.gs` | `c175d8389dce879910ea91e719f6e734ed2f104052e35a4e19e1137cb6a72d48` | igual |
| #109 | `Codigo-109.gs` | `6ecbe59316825ba0548960ea589a6731dd88a4ef975e71fe36b163fda5609bb3` | igual |
| #110 | `Codigo-110.gs` | `4f6600227cd1aeaf6ce090260bd81dce64a3b3c3acd6643247f283230dbc8a77` | igual |

### Partes locais do módulo após #105

| Arquivo | SHA-256 relido |
|---|---|
| `modulo-Analise.gs` | `8a54a5162c48d9f340a0aa7178b6f0449dede1a170b32da263eddaeb9ecbf4f6` |
| `modulo-Configuracao.gs` | `bb784c6d0e5fcd08f37650802e10e87413c094570af71393809c4cf8edd1b69f` |
| `modulo-Ficha.gs` | `6012dcb3dbcd1050f91101c14c68d68ce30c9640c82a56d3ceb4104724003e34` |
| `modulo-Invocacoes.gs` | `ebf20bb167b57cc73a1b7cf71c635303805e43aa7e21f89109f02cb4ba520ee9` |
| `modulo-Origens.gs` | `9009522887026e3c402345862566834186fd166f336cc8e5c745077351e43792` |

## Aplicação, respostas da API e tempos

| Item | Era | Ciclo |
|---|---|---|
| Cópia fria | criada e preservada | não criada |
| Dez hashes de partida e módulo `9dc3480a` relidos no Google | pendente | não iniciado |
| Snapshot inicial de todos os alvos | pendente; só metadados lidos | não iniciado |
| Código forma B e molde D2+D3 | não instalados | não instalados |
| `spreadsheets.batchUpdate` enviados | 0 | 0 |
| Respostas de `findReplace` | nenhuma | nenhuma |
| Contagem #108 = 292 | não medida | não medida |
| Contagens #119 = 225/4725 e 225/525 | não medidas | não medidas |
| Notas D4 e regra #114 no índice 4 | não aplicadas | não aplicadas |
| Achatador e texto `35d00ae28bfa…` no Google | não executados | não executados |
| Plano composto e reversão | não gerados | não gerados |
| Janela dos passos 3–6 | cronômetro não iniciado | cronômetro não iniciado |
| Tempo para aplicar só o plano composto | não medido | não medido |
| Durações nas Execuções e capturas | não medidas; sem capturas | não medidas; sem capturas |

## O que não rodou no Sheets

Nenhuma célula foi editada. Não rodaram: ± de vida, Buff decimal na FICHA e na entidade, missão no painel, XP total digitado, cartão de Classe 0, menus custom de Arma e Origem, nem restauração da fórmula nova em FICHA!Z15.

Também não rodaram a comparação com as QAs, a varredura de erros de fórmula, os preparadores de planilha nos commits próprios ou a composição do plano e da reversão. Não há evidência de aprovação funcional nativa.

## Preservação e retomada

- Nenhuma oficial, QA ou ficha de jogador recebeu escrita. As oficiais só foram referenciadas para localizar e copiar a Era.
- Nenhuma função de Apps Script foi executada. Nenhum `construir()`, `continuar()`, acionador ou versão foi criado.
- A cópia da Era não foi apagada. O Ciclo aguarda a conclusão integral da Era, como manda o roteiro.
- #117 continua excluído por D1; #116/#120 não foram reaplicados.
- Depois da liberação manual, começar pelos dez hashes e pelo módulo da cópia Era. Havendo divergência, parar e registrar; não substituir o código.
- Antes de instalar, obter o snapshot completo dos alvos. Usar o `referencia/trecho-molde.js` privado já fornecido, sem gerar outro.
- A rodada nas oficiais continua dependendo de Mizuki no PC, backup e autorização posterior ao ensaio.

Evidências privadas: `rodada-oficiais-20261116/ensaio/copia-era.json`, `estado-inicial.json` e `hashes-pacote-local.json`. Não há snapshot completo, plano composto ou reversão ainda.
