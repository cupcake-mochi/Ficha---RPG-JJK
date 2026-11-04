# Preparação incremental das PRs 51–56 — recuperação de 04/11/2026

Estado: preparada para revisão, sem merge ou aplicação nas oficiais. Base de
código: PR56 `618370e024102a99f66acb79ba12c450df0b0c2a`. PR31 preservada em
`765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`.

## Recuperação

A pasta de trabalho anterior dependia de um diretório Git em `/tmp` que deixou
de existir. Foi preservada integralmente. Um clone independente, com objetos
Git próprios e sem alternates temporários, foi criado em
`Claude/02-RPG/_trabalho/ficha-integracao-5156-20261104`, ramo
`codex/preparacao-incremental-5156-20261104`.

Os projetos das duas cópias descartáveis do ensaio anterior foram abertos apenas
para leitura. Seus `Codigo.gs` continuam idênticos ao hash registrado no ensaio.
Foram recuperados os cinco fragmentos do pacote da cópia Era. Remover somente
os incrementos identificados da proposta recuperada reproduziu exatamente o
hash anterior registrado. Essa reconstrução é uma evidência histórica; não é
um snapshot atual das oficiais.

| Conteúdo | SHA-256 |
|---|---|
| Codigo anterior reconstituído | `52302778db247518b39eb9ebd741cb6a24fc58063a992a24bda69789dac1c775` |
| Codigo proposto, relido igual nas duas QA | `8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0` |
| Módulo comprimido preservado | `9dc3480af82287b153bf6e18c76f2bc111baaca63bd3cbf4f85ecd628ac09ffc` |

Snapshots privados, código reconstituído, proposta e log local estão em
`nuvem-b47/saidas/integracao-5156/`, ignorado. Não versionar esses arquivos.
Os deltas sanitizados e o preparador estão versionados, permitindo reprodução
sem depender desta conversa ou de arquivos em `/tmp`.

## Escopo da proposta

Somente o `Codigo.gs` instalado recebe o incremento. Conserva os cinco
fragmentos, os helpers anteriores, os caminhos leves de abertura, salário,
editor, paleta e demais arquivos. Não instalar o pacote integral do Git.
O hash fixo recusa um projeto diferente ou que já recebeu o incremento.

O plano `pilha_5156_plano.json` contém 11 valores/fórmulas e três notas:

- FICHA: J26, D37, Z56, D59 e O67.
- DADOS_CUSTOM: CP3, CQ3, BE12, B126 e B127.
- DADOS: DW15.
- FICHA AMALDIÇOADA: notas D73, J73 e P73.

São vida do Corpo Quebradiço, indicador sem barra de Integridade, Bloquear,
Defesa, deslocamento, menus de Origem, auxiliares corporais e textos R60/R61.
O código inclui descanso, cura recebida e SOCORRO das PRs 51–56. A aba SOCORRO
é criada pela operação de registro; este preparador não cria abas.

`pilha_5156_runtime.gs` preserva a sequência de remendos do ensaio. O teste
confere que as três funções finais de descanso são exatamente as fontes da
PR56. `pilha_5156_molde.gs` valida todos os alvos antes de alterar o modelo em
memória e aceita os valores novos numa segunda leitura.

## Reprodução e revisão

Teste portátil, sem conta Google:

```sh
node r53/testes/pilha_5156.js
```

Teste adicional com os arquivos privados recuperados:

```sh
node r53/testes/pilha_5156.js nuvem-b47/saidas/integracao-5156
```

Preparar arquivos locais a partir de snapshots, sem acesso à rede:

```sh
node r53/diagnostico-android/preparar_pilha_5156.js \
  caminho/snapshot-Codigo.gs caminho/snapshot-celulas.json \
  nuvem-b47/saidas/entrega-5156-nova
```

O snapshot normalizado tem `{locale, cells}`. Cada elemento de `cells` usa
`{aba, r, c, sheetId, value}` para valores ou `{aba, addr, sheetId, note}`
para notas. `r`/`c` começam em 1; `sheetId` é o ID real retornado pelo Google,
nunca a posição da aba. Fórmulas vêm de `userEnteredValue.formulaValue`,
não do resultado calculado. Célula vazia é `null` ou `""`. Ler somente os
14 campos necessários, com os metadados de aba e locale.

Saídas: Codigo proposto/reversão, pedidos/reversão e manifesto. Só são escritos
após todas as validações, numa pasta nova. Os pedidos limitam `fields` a
`userEnteredValue` ou `note`; não substituem formatos nem validações. Literais
usam `stringValue`, preservando apóstrofos sem interpretação USER_ENTERED.
Localização pt_BR altera separadores e decimais apenas fora de textos;
matrizes e locales não ensaiados são recusados.

Antes de futura aplicação autorizada: backup nativo novo e snapshot de todos
os arquivos do projeto; comparar o Codigo e os 14 alvos com a proposta. Se
houver qualquer divergência, revisar, sem forçar as guardas. Ensaiar o pacote
resultante em cópia atual. Reler imediatamente antes de gravar, pois o plano
não trava edições concorrentes. Salvar e reler o código, aplicar um único lote
de células e conferir fórmula, nota e comportamento de restauração.

Não executar construir/continuar/acabar. Não usar estado de personagem das QA
como modelo. Se houver falha entre código e células, suspender uso e confrontar
os snapshots; as duas etapas não são uma transação única. Reversão exige que
cada alvo ainda tenha o valor proposto (`planejarCelulas(snapshotAtual,true)`)
e que o Codigo salvo tenha o hash posterior. Não reaplicar pedidos de reversão
cegamente após edições do usuário. Um registro SOCORRO criado no uso posterior
não é apagado por este plano.

## Evidência e limites

Nesta recuperação: 58 verificações incluindo snapshots recuperados; 48 no
modo portátil. Verificados paridade dos 14 alvos, idempotência do molde,
recusa sem alteração parcial, locales, preservação de notas/campos, hashes,
carregamento do módulo real, exportação do descanso e funções finais iguais às
fontes. A proposta reproduz o código nativo anteriormente ensaiado; nesta
rodada não foram executados novamente os menus nem aplicadas células.

O registro de continuação anterior relata aprovação dos cinco comandos de
Recursos e restauração nativa das cinco fórmulas da FICHA nas duas QA.
Os logs/capturas originais em `/tmp` não foram recuperados; não apresentar a
releitura atual de código como repetição desses testes de comportamento.

As PRs 51–56 continuam na ordem 51 → 52 → 53 → 54 → 55 → 56. Ao integrar,
preservar ancestralidade e conferir base/diff/checks após cada passo. Esta
preparação é um ramo separado sobre PR56, sem alteração das PRs existentes.
Revisão recomendada: Sol/Medium. Aplicação incremental futura: Sol/High.
