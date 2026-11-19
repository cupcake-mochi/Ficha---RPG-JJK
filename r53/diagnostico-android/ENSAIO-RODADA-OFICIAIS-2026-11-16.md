# Ensaio da rodada nas oficiais · 16/11/2026

**Ensaio concluído primeiro na cópia Era e depois na cópia Ciclo. Nenhuma gravação nas oficiais.** Ambas passaram nas conferências de código, aplicação, reversão, reaplicação e testes reais no Sheets. Os dados temporários foram restaurados e a varredura final das 30 abas de cada cópia encontrou zero erros de fórmula.

Este documento substitui o relatório anterior de parada em J26. Não autoriza nem executa promoção nas oficiais. A PR permanece em rascunho, sem merge, com as diferenças de método e representação explicitadas abaixo.

Base após fetch: `codex/corrige-colagem-atributos-20261108`, commit `7357c36ae407221f93d06281f8351a55c11e5187`. Ramo `codex/ensaio-rodada-oficiais-20261116`. Nenhuma ação em main ou na PR31, force push ou auto-merge.

## Escopo e método realmente executado

- Lidos integralmente o roteiro anexado, o plano e o registro das oficiais. D1 exclui R67/#117; D2+D3 usam o trecho original do molde; D4 aplica as duas notas; D5 instala o pacote pronto, forma B.
- Cópias criadas pelo files.copy nativo do Drive na conta dona das fichas, em vez do menu Arquivo › Fazer uma cópia. Os projetos vinculados vieram junto. A interface mostrou “Apenas eu posso acessar”. Nenhuma permissão ou compartilhamento foi modificado.
- Era: origem `1MQqhHbI…`, cópia `18Yj-2ya…`, projeto `1bikx37d…`. Ciclo: origem `1pgLDZOY…`, cópia `1RdiiQjy…`, projeto `1fsx5EgI…`. Links completos somente em privado.
- Mudanças de células e estrutura exclusivamente por spreadsheets.batchUpdate. Nenhum Localizar e substituir pela interface. Edições de personagem somente no passo 7.
- Não executados construir(), continuar(), funções manuais do Apps Script ou acionadores instaláveis. Nenhum novo consentimento do Google observado ou aceito. As execuções medidas são acionadores simples de edições reais.
- Não repetida a cadeia de 42 alterações de código no Google. Foram relidos os artefatos da Fase 0 e conferidos seus 42 hashes. Os preparadores de planilha #57–#90 rodaram localmente nos commits dos próprios PRs, com a correção autorizada das aspas no helper. Os deltas restantes foram usados como fornecidos.
- **Diferença de método:** o trecho original do molde, sem regeneração, e o trecho gerado pelo achatador foram executados localmente, sem alteração interna, sobre os dez fontes capturados integralmente do editor real. Adaptadores de modelos forneceram getValue/setValue. Os resultados foram instalados, salvos e relidos pela interface. Esses dois trechos não rodaram no console DevTools do navegador lateral. Este ensaio comprova o resultado salvo e o comportamento real no Sheets, mas não comprova o caminho de execução dentro do console/CSP do editor.
- A leitura e instalação finais usaram o navegador lateral, com clipboard e controles restritos à guia. A Era começou no Brave e teve as interrupções registradas adiante. Nenhuma cópia foi apagada.

## Correção autorizada das aspas

A primeira guarda do #57 recusou FICHA!J26 porque a API devolve referências simples como DADOS_PROGRESSAO! sem as aspas opcionais esperadas pelo preparador. Não havia diferença de cálculo. Após autorização expressa do Mizuki, formulaComparavel passou a retirar somente essas aspas opcionais fora dos literais de texto. Aspas dentro de texto, aspas duplas escapadas, nomes de abas com espaços e notas continuam preservados. A comparação não reescreve snapshots ou pedidos.

Validação repetida ao final: `node r53/testes/pilha_5156.js` aprovou 53 verificações; `node r53/testes/pilha_5156_aspas.js` aprovou 13. Total 66. Nenhuma mecânica foi alterada para contornar uma guarda.

Os verificadores privados de releitura consideram também a representação equivalente A1:A1 versus A1 que o Sheets devolve, sem alterar o pedido. Mesclas são comparadas como conjunto, enquanto a posição das regras condicionais continua significativa.

## Dez arquivos: antes e depois salvos

Os dez hashes foram relidos nos dois projetos antes da instalação e novamente após salvar e recarregar a forma B, o molde e o achatamento. A partida e o resultado abaixo são iguais nas duas cópias. O CRLF do transporte do clipboard foi normalizado para LF antes do SHA-256.

| Arquivo | SHA-256 inicial — ambas | SHA-256 final salvo — ambas |
|---|---|---|
| Analise | `2ea7e9d453917956fd7f9707c72bd1225961e186ab21fda9202dd53556d295b4` | `98f8f056cd4f86cc874f320813fbb3f309babcd0412a2a9c94487f45b824acde` |
| Codigo | `52302778db247518b39eb9ebd741cb6a24fc58063a992a24bda69789dac1c775` | `a7f6f33050c3bdf9f03def4546f02ecbf20f6b02b239bba08c3dfa32af65237a` |
| Configuracao | `bb784c6d0e5fcd08f37650802e10e87413c094570af71393809c4cf8edd1b69f` | `b5dfcd181c3ccb431bd69f48b9d0198f970d0ada322c2810df08ac1e6a8c2699` |
| EditorR53 | `08badae12322539ff013e728bbf6ad270d9f68455bd4eac548648c2a4ae1b910` | `676337f165f7056db20364e5327f2793e957d2db405199a75009f5f44a163c49` |
| Ficha | `6012dcb3dbcd1050f91101c14c68d68ce30c9640c82a56d3ceb4104724003e34` | `6c0391edac631146b8f1479d47cdf75693aea80235a6efdc1f81e7fb3efec63b` |
| Invocacoes | `ebf20bb167b57cc73a1b7cf71c635303805e43aa7e21f89109f02cb4ba520ee9` | `e73584ddf3b14a6665107ab733fe281cc1b2beb1e4f43ed9a695673ac209f48f` |
| LotePaleta | `848e878b4a2aa4c44a8bffcbf294281d9e77919474babb6ef60732e03fc081c7` | `848e878b4a2aa4c44a8bffcbf294281d9e77919474babb6ef60732e03fc081c7` |
| Origens | `9009522887026e3c402345862566834186fd166f336cc8e5c745077351e43792` | `b5dfcd181c3ccb431bd69f48b9d0198f970d0ada322c2810df08ac1e6a8c2699` |
| PaletaSegundoPlano | `a5a0e83def3c0363fbc75f634e051b21c601d3b87636f4bb3caa16b97357eeee` | `a5a0e83def3c0363fbc75f634e051b21c601d3b87636f4bb3caa16b97357eeee` |
| SalarioLote | `aaaa74f32b0c7294422272baa541fd94f69ffc4a00e447605d4a461b6aed259e` | `aaaa74f32b0c7294422272baa541fd94f69ffc4a00e447605d4a461b6aed259e` |

Módulo inicial descompactado: `9dc3480af82287b153bf6e18c76f2bc111baaca63bd3cbf4f85ecd628ac09ffc`, cinco partes declaradas.

Forma B: Codigo `4f6600227cd1aeaf6ce090260bd81dce64a3b3c3acd6643247f283230dbc8a77`; EditorR53 `676337f165f7056db20364e5327f2793e957d2db405199a75009f5f44a163c49`; Analise `8a54a5162c48d9f340a0aa7178b6f0449dede1a170b32da263eddaeb9ecbf4f6`; módulo `bd42b5351ec1d299e9e54ecd8281de5d75ee129f01fd3c8e4475b5c6fc9e066e`. Os outros sete arquivos foram conferidos sem instalação desnecessária.

O molde original gerou Codigo `b3ed2f7e7b804e7db4c724822034c0839c688fb1733ea38cf338170a475e52f8`. São 593 fórmulas do molde: FICHA 54, FICHA PESSOAL 292, DADOS_CONFIG 22 e DADOS_CUSTOM 225.

Achatamento: três partes declaradas; texto integral recebido pelo new Function com SHA-256 `35d00ae28bfa9836566db4cec46cc14bf4c55da1e6ebb342b30aec2d7d263b10` nas duas cópias. O trecho retornou 8.730.984 caracteres, 51.663 caracteres de remendos incorporados, partes 5 → 3 e Codigo 1.840.559 → 1.788.789 caracteres. O Codigo salvo também coincidiu com a referência Node a7f6f330…; o critério decisivo é o texto descompactado.

## Hashes de cada passo da Fase 0

Releitura local dos 42 artefatos já reproduzidos na Fase 0, comparada ao manifesto. Todos os hashes “depois” foram relidos e bateram. Esta tabela não representa 42 instalações no Google nem uma nova execução da cadeia de código durante este ensaio. O commit é o próprio PR registrado no manifesto.

| PR | Commit | Lado / preparador | SHA-256 antes | SHA-256 depois, relido = esperado |
|---|---|---|---|---|
| #57 | `8db0bae93a` | C / `preparar_pilha_5156.preparar` | `52302778db247518b39eb9ebd741cb6a24fc58063a992a24bda69789dac1c775` | `8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0` |
| #60 | `eaab143c8d` | C / `preparar_recursos_fila.preparar` | `8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0` | `6aec0d0a1e88f777475bc7578fc231c982f0d9b08783c6e8fbe90becdf920455` |
| #61 | `cb043171a2` | C / `preparar_recursos_fila.preparar` | `8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0` | `5b81e86d0d5f06d648d9ae91af23dfee435aa6b3aec57c677b15309a3f750cb8` |
| #62 | `528e20e39b` | C / `preparar_recursos_fila.preparar` | `8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0` | `3767fb0f19079bc1fbb1bb04d62be97d26cc4a92f00b04431dd4129551b33aa7` |
| #63 | `4a2fb4018e` | C / `preparar_integridade_movimento.prepararCodigo` | `3767fb0f19079bc1fbb1bb04d62be97d26cc4a92f00b04431dd4129551b33aa7` | `9f64aa8c47ee6ecd0b0093a08c1434e55ba6eb711f887117ba821611be431631` |
| #64 | `ffdee604b6` | C / `preparar_equipamento.prepararCodigo` | `9f64aa8c47ee6ecd0b0093a08c1434e55ba6eb711f887117ba821611be431631` | `a09bf672a520e0750d239386f23f14e300eda84094668b7771cee605e028ebac` |
| #65 | `5f6abeae75` | C / `preparar_bencaos_imunidades.prepararCodigo` | `a09bf672a520e0750d239386f23f14e300eda84094668b7771cee605e028ebac` | `19ae4c19660ce322f6cf3df8041469f8a65a7cfa18a9260c7c32f2c760ec77ac` |
| #66 | `f2bc70fd27` | C / `preparar_descanso_origens.prepararCodigo` | `19ae4c19660ce322f6cf3df8041469f8a65a7cfa18a9260c7c32f2c760ec77ac` | `d5845c0367be94e63f12b799053d5432d0ec4af5beea3a3d05bf32b607a2a084` |
| #67 | `971228d2b8` | C / `preparar_origens_recursos.prepararCodigo` | `d5845c0367be94e63f12b799053d5432d0ec4af5beea3a3d05bf32b607a2a084` | `bae62817a2ae03281dff1247c7e2f97d6ac0518a6f90271bf6de96da98a09130` |
| #69 | `6928962804` | C / `preparar_reserva_bolsa.prepararCodigo` | `bae62817a2ae03281dff1247c7e2f97d6ac0518a6f90271bf6de96da98a09130` | `4b0d2cc1952ac3726a47a1969c66c04e30658f7397a927f7af0930615ee9daa9` |
| #70 | `4324ad3b8f` | C / `preparar_pratica_cotidiana.prepararCodigo` | `4b0d2cc1952ac3726a47a1969c66c04e30658f7397a927f7af0930615ee9daa9` | `50f3aa55662adc7251a9be91cae4aace316c84ec3df3f53af471c841094b633b` |
| #70 | `4324ad3b8f` | E / `preparar_pratica_cotidiana.prepararEditor` | `08badae12322539ff013e728bbf6ad270d9f68455bd4eac548648c2a4ae1b910` | `98413975988095b99da8f260c7295b09d00f7f40ae85b4f14ec86f9e88ed6844` |
| #71 | `c54f74a093` | C / `preparar_conjuracao_integridade.prepararCodigo` | `50f3aa55662adc7251a9be91cae4aace316c84ec3df3f53af471c841094b633b` | `6b22b689b1940dd22c8a5a0ba1143becf74c01446afb502dc5633da1d62dd6e8` |
| #71 | `c54f74a093` | E / `preparar_conjuracao_integridade.prepararEditor` | `98413975988095b99da8f260c7295b09d00f7f40ae85b4f14ec86f9e88ed6844` | `165fc80d4f3f32c344195541b888662bda86e503e0b3ab615362ffd610403466` |
| #72 | `b7c06b06a5` | C / `preparar_classe_zero.prepararCodigo` | `6b22b689b1940dd22c8a5a0ba1143becf74c01446afb502dc5633da1d62dd6e8` | `e45999e3cbea477b5357434ffeda418038c8228a7c316bc0dcdab8bf8c4f7c5e` |
| #72 | `b7c06b06a5` | E / `preparar_classe_zero.prepararEditor` | `165fc80d4f3f32c344195541b888662bda86e503e0b3ab615362ffd610403466` | `13cf7ddf5601ef1056e9f5717cb1dcff0dfd1046263dcd384bd69684d791cd55` |
| #73 | `868ebb8ca1` | C / `preparar_alcance_cura.prepararCodigo` | `e45999e3cbea477b5357434ffeda418038c8228a7c316bc0dcdab8bf8c4f7c5e` | `5c8c7493600367d4c004c3c85a4cc0f5e82459ec4cb4a54ccdb1c769741e3a2c` |
| #73 | `868ebb8ca1` | E / `preparar_alcance_cura.prepararEditor` | `13cf7ddf5601ef1056e9f5717cb1dcff0dfd1046263dcd384bd69684d791cd55` | `aa77309cb42e08f49dbe1f427c72b0c68ec6168fbf6b2294d4d3555a7a7b5c09` |
| #74 | `758c571aad` | C / `preparar_alcance_beneficios.prepararCodigo` | `5c8c7493600367d4c004c3c85a4cc0f5e82459ec4cb4a54ccdb1c769741e3a2c` | `2005362b35c236dc17f241ace10d5bb075f61ec7662a1fe234fa1b5216a83e9b` |
| #74 | `758c571aad` | E / `preparar_alcance_beneficios.prepararEditor` | `aa77309cb42e08f49dbe1f427c72b0c68ec6168fbf6b2294d4d3555a7a7b5c09` | `2ed5d1e18726708fcf4d08daa9a674d9996ccf7477bcedcbcfad0c54887fe928` |
| #75 | `af22de97e3` | C / `preparar_tempo_feiticos.prepararCodigo` | `2005362b35c236dc17f241ace10d5bb075f61ec7662a1fe234fa1b5216a83e9b` | `21a59ce691bdd38162688485b9a1222476b469a500d09d055c99e97d07c26923` |
| #75 | `af22de97e3` | E / `preparar_tempo_feiticos.prepararEditor` | `2ed5d1e18726708fcf4d08daa9a674d9996ccf7477bcedcbcfad0c54887fe928` | `676337f165f7056db20364e5327f2793e957d2db405199a75009f5f44a163c49` |
| #76 | `4911da8f8d` | C / `preparar_rajada_alvos.prepararCodigo` | `21a59ce691bdd38162688485b9a1222476b469a500d09d055c99e97d07c26923` | `6062ac46cffe8386d03a3c6fa6d991f1445e948211953783a21febecc1e6f769` |
| #77 | `fa2acaa7ef` | C / `preparar_fragil_fica.prepararCodigo` | `6062ac46cffe8386d03a3c6fa6d991f1445e948211953783a21febecc1e6f769` | `cc5b05bf9de303804a1726d583934526162b1eece43e255ddc126fd6f3ba28cd` |
| #78 | `262e264f28` | C / `preparar_sem_volta.prepararCodigo` | `cc5b05bf9de303804a1726d583934526162b1eece43e255ddc126fd6f3ba28cd` | `01e6422424022d301f994c2dbae84ee630849d81e36ec80c41df04bee6db134e` |
| #79 | `4118bb9b30` | C / `preparar_devolucoes_incompativeis.prepararCodigo` | `01e6422424022d301f994c2dbae84ee630849d81e36ec80c41df04bee6db134e` | `30306ed099e1ae5d88bf42e7a6e48af093f4f84aa719f36fc3fd0231c26b5658` |
| #80 | `97d1b00ee3` | C / `preparar_restricoes_agrupadas.prepararCodigo` | `30306ed099e1ae5d88bf42e7a6e48af093f4f84aa719f36fc3fd0231c26b5658` | `9fc4f2eb1e265f34f8a261001a503eb21c6b8737ced6c399129f32bc4e2c0c05` |
| #81 | `bfe00a528e` | C / `preparar_fragil_instantaneo.prepararCodigo` | `9fc4f2eb1e265f34f8a261001a503eb21c6b8737ced6c399129f32bc4e2c0c05` | `e44e7f0c929fec0fca6ef65a6670937dd7d4278e47dbaedde9d18278dc4eb45f` |
| #82 | `b11c46a2fc` | C / `preparar_fragil_catalogo.prepararCodigo` | `e44e7f0c929fec0fca6ef65a6670937dd7d4278e47dbaedde9d18278dc4eb45f` | `ec0bbd157b7b3bf10b8aee6252896971d0332ae1788f4d7a3b2f13d6928acc75` |
| #83 | `b6c1ac1b33` | C / `preparar_forma_funcao.prepararCodigo` | `ec0bbd157b7b3bf10b8aee6252896971d0332ae1788f4d7a3b2f13d6928acc75` | `cf8dc5960121fcc4677f4b19288932ee738be39e2d6d2a61a10d1a3f3ef59672` |
| #84 | `74d83b7f3c` | C / `preparar_corroi.prepararCodigo` | `cf8dc5960121fcc4677f4b19288932ee738be39e2d6d2a61a10d1a3f3ef59672` | `da89202e8a7af2029855196dc464ef4091d2174393a954860cb5381d8ee5709e` |
| #85 | `735d499684` | C / `preparar_liberacoes.prepararCodigo` | `da89202e8a7af2029855196dc464ef4091d2174393a954860cb5381d8ee5709e` | `7512bf622897eb1145f3849a55ccd80419a147e8cd540a3c2b6113d84c8cdfb7` |
| #86 | `6568838bad` | C / `preparar_expansao_domada.prepararCodigo` | `7512bf622897eb1145f3849a55ccd80419a147e8cd540a3c2b6113d84c8cdfb7` | `5b7bb420739efeeb28e036b8da79f38bcc0e19b20d4d14f229f0effaac74e7ef` |
| #87 | `0554071051` | C / `preparar_repertorio_trilha.prepararCodigo` | `5b7bb420739efeeb28e036b8da79f38bcc0e19b20d4d14f229f0effaac74e7ef` | `26b78470c8eda2443ee74f650b5a925cde1fdbeea7a79c8387c3304e9767968c` |
| #88 | `ab05bcf9cc` | C / `preparar_contagem_especiais.prepararCodigo` | `26b78470c8eda2443ee74f650b5a925cde1fdbeea7a79c8387c3304e9767968c` | `36ca73efd1eca6809fd8ddfa1be324eebaad2f5aef0830d4c25c6aaeaaaff3bc` |
| #89 | `e2b03307eb` | C / `preparar_criacao_nivel_fixo.prepararCodigo` | `36ca73efd1eca6809fd8ddfa1be324eebaad2f5aef0830d4c25c6aaeaaaff3bc` | `ffd349c9299342d735917697355d3f278f526ff74b9e009706ce61a8b0784352` |
| #90 | `4eeb276b39` | C / `preparar_nivel_obtido.prepararCodigo` | `ffd349c9299342d735917697355d3f278f526ff74b9e009706ce61a8b0784352` | `b709ad14b6340c132279f5a44030cb9a737c3f1251322c9929c6ffd341d9f38e` |
| #105 | `88e516c480` | C / `instalar_frequencia_cena.trocas` | `b709ad14b6340c132279f5a44030cb9a737c3f1251322c9929c6ffd341d9f38e` | `0292582a1fffaa7a328980e14bac39830e67cd58e6d48a0563bc665854193463` |
| #107 | `f11ca2216d` | C / `preparar_trava_nivel_missao.preparar` | `0292582a1fffaa7a328980e14bac39830e67cd58e6d48a0563bc665854193463` | `b5861c145394db8ce803304699776986300c121ca0a9ce2f9264edeed3ae4ed5` |
| #108 | `b4b65c36a1` | C / `preparar_corte_xp_missao.preparar` | `b5861c145394db8ce803304699776986300c121ca0a9ce2f9264edeed3ae4ed5` | `c175d8389dce879910ea91e719f6e734ed2f104052e35a4e19e1137cb6a72d48` |
| #109 | `1d0e00c2db` | C / `preparar_xp_congelado_nome.preparar` | `c175d8389dce879910ea91e719f6e734ed2f104052e35a4e19e1137cb6a72d48` | `6ecbe59316825ba0548960ea589a6731dd88a4ef975e71fe36b163fda5609bb3` |
| #110 | `2e0ba52032` | C / `preparar_xp_linha_congelada.preparar` | `6ecbe59316825ba0548960ea589a6731dd88a4ef975e71fe36b163fda5609bb3` | `4f6600227cd1aeaf6ce090260bd81dce64a3b3c3acd6643247f283230dbc8a77` |

## Respostas da API e releitura da planilha

Todas as etapas efetivamente aplicadas, em ordem. “Respostas/lotes” soma replies e chamadas da etapa. Cada chamada foi comparada à quantidade exata de pedidos antes de seguir. “Controles” é a releitura dos campos-alvo; todos passaram. As contagens são iguais nas duas cópias.

| Etapa | Era: respostas / lotes | Ciclo: respostas / lotes | Controles por cópia | FindReplace: fórmulas / valores / ocorrências |
|---|---|---|---|---|
| #57 | 14 / 1 | 14 / 1 | 14 | — |
| #63 | 41 / 1 | 41 / 1 | 41 | — |
| #64 | 63 / 1 | 63 / 1 | 63 | — |
| #65a | 6 / 1 | 6 / 1 | 6 | — |
| #67 | 8 / 1 | 8 / 1 | 8 | — |
| #69 | 6 / 1 | 6 / 1 | 6 | — |
| #70 | 247 / 1 | 247 / 1 | 938 | — |
| #71 | 41 / 1 | 41 / 1 | 41 | — |
| #72 | 23 / 1 | 23 / 1 | 23 | — |
| #73 | 36 / 1 | 36 / 1 | 36 | — |
| #74 | 36 / 1 | 36 / 1 | 36 | — |
| #75 | 108 / 2 | 108 / 2 | 108 | — |
| #76 | 1004 / 9 | 1004 / 9 | 1004 | — |
| #77 | 753 / 10 | 753 / 10 | 753 | — |
| #78 | 753 / 11 | 753 / 11 | 753 | — |
| #79 | 502 / 3 | 502 / 3 | 502 | — |
| #80 | 753 / 3 | 753 / 3 | 753 | — |
| #81 | 753 / 12 | 753 / 12 | 753 | — |
| #82 | 753 / 12 | 753 / 12 | 753 | — |
| #83 | 251 / 10 | 251 / 10 | 251 | — |
| #84 | 251 / 10 | 251 / 10 | 251 | — |
| #85 | 3 / 1 | 3 / 1 | 3 | — |
| #86 | 84 / 1 | 84 / 1 | 84 | — |
| #87 | 123 / 1 | 123 / 1 | 116 | — |
| #88 | 24 / 1 | 24 / 1 | 24 | — |
| #89 | 16 / 1 | 16 / 1 | 16 | — |
| #90 | 50 / 1 | 50 / 1 | 50 | — |
| #91 | 25 / 1 | 25 / 1 | 25 | 24 / 0 / 24 |
| #92 | 60 / 1 | 60 / 1 | 60 | 60 / 0 / 60 |
| #93 | 168 / 1 | 168 / 1 | 168 | 168 / 0 / 168 |
| #94 | 12 / 1 | 12 / 1 | 12 | 12 / 0 / 12 |
| #95 | 12 / 1 | 12 / 1 | 12 | 12 / 0 / 12 |
| #96 | 206 / 1 | 206 / 1 | 206 | 206 / 0 / 206 |
| #98 | 2 / 1 | 2 / 1 | 2 | 2 / 0 / 2 |
| #100 | 4 / 1 | 4 / 1 | 4 | 4 / 0 / 4 |
| #101 | 20 / 1 | 20 / 1 | 20 | 12 / 8 / 20 |
| #102 | 37 / 1 | 37 / 1 | 37 | 37 / 0 / 37 |
| #103 | 38 / 1 | 38 / 1 | 38 | 38 / 0 / 38 |
| #108 | 13 / 1 | 13 / 1 | 304 | 292 / 0 / 292 |
| #113 | 46 / 1 | 46 / 1 | 46 | 0 / 1 / 1 |
| D4 | 2 / 1 | 2 / 1 | 2 | — |
| #114 | 2 / 1 | 2 / 1 | 1 | — |
| #119 | 2 / 1 | 2 / 1 | 225 | 450 / 0 / 5250 |

- #65a foi aplicado; #65b foi omitido porque o head já contém a revisão. #69 não precisou de compensação.
- #70 teve 247 pedidos e crescimento de quatro grades; os 938 controles passaram.
- #108: uma regex alterou exatamente 292 fórmulas/292 ocorrências. Os outros 12 pedidos atualizaram oito notas e quatro campos auxiliares; 304 alvos relidos.
- #113: 45 notas e uma substituição literal, 1 valor/1 ocorrência. D4: notas exatas AH10 e AN10 do arquivo fornecido.
- #114: uma nota e regra nova no índice 4 de INVOCAÇÕES, preservando as quatro regras anteriores. Regra comparada à de bônus da QA, inclusive os 36 intervalos.
- #119 foi a última alteração da planilha antes da prova composta. Os dois pedidos originais rodaram na mesma chamada: 225 fórmulas/4.725 ocorrências no primeiro, 225 fórmulas/525 ocorrências no segundo; 225 fórmulas finais relidas.
- #116/#120 não reaplicados: aviso âmbar já presente nas oficiais e copiado. #117/R67 excluído.

## Plano composto, inversa e tempos

Cada cópia tem plano e inversa próprios em privado, com antes nativo inicial e depois final. Inventário de 6.356 alvos, incluindo todas as células das linhas novas. Mudaram 3.434 células: 3.178 com valor/fórmula, 129 com nota, 29 com validação e 511 com formato; conjuntos se sobrepõem. A estrutura inclui quatro crescimentos, 23 mesclas novas e quatro pedidos de regras (três extensões na FICHA AMALDIÇOADA e a regra nova de INVOCAÇÕES).

| Medição | Era | Ciclo |
|---|---|---|
| Janela registrada passos 3 a 6 | 1 h 59 min 56,719 s | 1 h 36 min 36,072 s |
| Ida composta: guardas + gravação + releitura | 11 min 46,597 s | 9 min 14,739 s |
| Volta | v1 identificou 7 campos; inversa corrigida conferida | 8 min 0,278 s |
| Pedidos / lotes de ida | 3.471 / 18 | 3.471 / 18 |
| Pedidos / lotes da inversa final | 2.520 / 15 | 2.520 / 15 |
| Verificação final de ida | 25.424 campos + 90 estruturas | 25.424 campos + 90 estruturas |
| Verificação final de volta | 17.632 campos + 90 estruturas | 17.632 campos + 90 estruturas |

As janelas registradas incluem preparação, cadeia por etapas, evidência, recuperações de conexão e prova de volta/ida. A Era inclui a elaboração/correção da inversa; seu registro começou na retomada e não cobre todas as tentativas anteriores no Brave. Não são uma janela oficial limpa. A medição diretamente útil da aplicação composta é 11 min 46,597 s na Era e 9 min 14,739 s no Ciclo, incluindo guardas e releitura final. Não foi medida promoção nas oficiais.

**Divergência da primeira inversa da Era:** desfazer mesclas removeu a borda inferior de P327 e Q327 da FICHA AMALDIÇOADA e propagou a validação de D35 para E35, F35, D36, E36 e F36 de INVOCAÇÕES. Valores e fórmulas não falharam. A inversa v1 e a falha foram preservadas. A inversa final ganhou sete pedidos após a redução das grades para recuperar exatamente esses campos. Na Era rodaram os 14 lotes originais e os sete pedidos na ordem final; a releitura integral passou. Não foi repetido o ciclo inteiro só para obter outro tempo. No Ciclo a inversa final de 15 lotes já incluía a correção e passou integralmente, seguida da ida agrupada.

## Comparação com QA

As QAs foram somente lidas, incluindo seus projetos atuais. Codigo 4f660022…, EditorR53 676337f1… e módulo bd42b535… conferem. Mantêm molde anterior e INDIRECT, sem achatamento e sem R67. Seus restos de teste não foram copiados.

Foram comparados valores/fórmulas, notas e validações dos alvos alterados: 3.336 controles na Era e 3.341 no Ciclo, que inclui cinco guardas de validação acrescentadas após o achado da inversa. Em cada cópia houve 227 diferenças previstas: 225 fórmulas custom sem INDIRECT e duas notas D4.

Mais uma diferença de armazenamento, em ambas: ANALISE!C18410. O #70 grava uma fórmula constante cujo resultado é `'DADOS_R53'!C252`; a QA guarda esse texto literal. O effectiveValue foi relido em ambas as fontes e é idêntico. Mantido o pedido do preparador, sem conserto improvisado para igualar a representação. Essa diferença não é contabilizada como igualdade literal.

A comparação com QA não verificou formatos. Os formatos foram preservados nos snapshots, na aplicação/reversão e na restauração dos testes. Mesclas comparadas por conteúdo, regras também por posição.

## Testes reais no Sheets

| Teste | Era | Ciclo |
|---|---|---|
| Decimal FICHA | P26 = 1,5; J26 = 1 | Mesmo resultado |
| Vida −1 | D26 preparado em 1; AM26 = −1; D26 = 0; comando limpo | Mesmo resultado |
| Decimal entidade | O21 = 1,5; DADOS_INVOC!DO2 = 1; FOR 1 e aviso âmbar | Mesmo resultado |
| Missão longa | 200 XP; total 3.900; nível 10 | 200 XP; total 200; nível 2 |
| XP total digitado | 3.750; fórmula =DADOS!$CZ$47 restaurada; base 3.550; missão congelada em 200 | 250; mesma fórmula; base 50; nível 2 → 3; missão congelada em 200 |
| Classe 0 | Nome temporário; Toque; Utilidade; 1,5 m; armazenamento classe0.1 | Mesmo resultado |
| Custom Arma | 13 categorias visíveis | 13 categorias visíveis |
| Custom Origem | 23 perícias visíveis | 23 perícias visíveis |
| Restaurador Z15 | Sobrescrito; fórmula nova exata restaurada; 11 de 11 | Sobrescrito; fórmula nova exata restaurada; 9 de 9 |

Imagens privadas dos menus, cartão, resultados e Execuções. Inspeção visual da seção de Prática Cotidiana nas linhas 563–567 e do seletor/texto de repertório em INVOCAÇÕES, em ambas.

Tempos de onEdit em segundos; todos os registros abaixo terminaram “Concluído”. Amostras de desktop, não teste de celular ou garantia futura.

| Edição | Era (s) | Ciclo (s) |
|---|---|---|
| Buff FICHA | 11,770 | 10,203 |
| Comando −1 | 19,344 | 15,622 |
| Buff entidade | Sem duração vinculada observada | 14,598 |
| Nome missão | 10,421 | 9,682 |
| Tipo Longa | 22,880 | 23,559 |
| XP digitado | 22,810 | 23,542 |
| Nome Classe 0 | 27,177 | 19,312 |
| Forma Toque | 19,747 | 15,519 |
| Tipo Arma | 16,243 | 22,877 |
| Tipo Origem | 25,259 | 10,186 |
| Z15 | 22,446 | 15,167 |

Preparação de D26 em 1: 5,737 s na Era e 7,994 s no Ciclo, fora das ações principais. Maiores onEdit principais observados: 27,177 s e 23,559 s. A proximidade do limite dos acionadores simples na amostra mais lenta permanece uma limitação operacional.

## Limpeza e estado final

Antes dos testes foram salvas áreas de personagem, cartão custom, montagens, dados do Classe 0, catálogo, missões e registros de salário/extrato, incluindo vazios. Restauração exclusivamente por API: Era, 19 células e um grupo de colunas (20 pedidos); Ciclo, 21 células e um grupo (22 pedidos). A diferença decorre dos dados iniciais e do lançamento de salário.

Cada limpeza passou em 357.185 controles de campos, zero divergências. Propriedades, mesclas, regras e grupos das 30 abas coincidiram com o fim da rodada anterior aos testes. O grupo custom foi recolhido novamente. Varredura completa de effectiveValue.errorValue antes e depois dos testes: zero erros em cada cópia. Cópias preservadas com a rodada final e sem os dados temporários.

## Ocorrências e limites

- A recusa inicial de J26 e a evidência foram preservadas; o usuário autorizou a correção do comparador. Não foi alterada mecânica.
- Brave pediu liberação manual de colagem, fornecida pelo usuário, e caiu ao receber Codigo inteiro. Não se presumiu salvamento após queda: o conteúdo foi relido. A forma B na Era usou blocos menores conferidos; depois o navegador lateral aceitou os arquivos completos.
- Leituras tiveram lentidão, timeouts e erro HTTP 500 recuperável. Só leituras foram repetidas. No Ciclo #81 retomou no lote 7 e #83 no lote 4, após conferir respostas anteriores. Nenhuma escrita com resultado desconhecido foi repetida. O controle lateral reiniciou ao atualizar uma guia; a guia e o editor salvo foram recuperados.
- Um verificador contou partes não vazias e sinalizou três quando ainda havia cinco declarações, duas vazias. O hash do módulo estava correto. A contagem foi corrigida; nenhuma alteração de projeto foi feita por esse alarme.
- Na descoberta do custom na Era houve tentativas em J11 e AI14, esta por redirecionamento de coluna recolhida. J11 foi restaurada por API, AI14 por desfazer a última edição, ambas relidas. O grupo correto foi aberto e as edições seguintes exigiram confirmação do endereço selecionado antes de digitar. As tentativas não integram os tempos válidos. A verificação integral da limpeza passou. O Ciclo já usou essa proteção.
- Alt+Down trocou uma aba na descoberta de dropdown da Era; os menus passaram a ser abertos pela seta com o mouse da guia. Somente a visualização mudou.
- A inversa exigiu sete ajustes, e a diferença de representação C18410 foi registrada. Após a retomada autorizada não houve hash real divergente, contagem de resposta inesperada ou novo pedido de consentimento Google.
- Não rodaram: trechos no DevTools real, cadeia de código no Google, R67, reaplicação do aviso âmbar, ensaio de celular ou promoção nas oficiais. A cópia veio pelo conector em vez do menu. Não tratar esses caminhos como verificados pelo método literal do roteiro.

## Evidência e próximos passos

Na pasta privada `rodada-oficiais-20261116/ensaio/` ficam, por cópia: snapshots iniciais/finais, dez fontes, hashes salvos, respostas dos lotes, guardas e verificações, `composto/plano-composto.json`, `composto/reversao.json`, tempos, inversa v1 e correção, comparação QA, imagens e registros das Execuções, limpeza dos testes e conclusões. Links completos somente nessa pasta, fora do Git.

O clone antigo com alternates Linux inválido foi preservado; usou-se checkout independente. No Git entram somente o comparador, seus testes e este relatório. PR em rascunho para `codex/corrige-colagem-atributos-20261108`, sem merge. Rodada futura nas oficiais exige backup prévio, Mizuki no PC e autorização específica dele, como determina o roteiro.
