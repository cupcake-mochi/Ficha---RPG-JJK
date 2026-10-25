# Análise do estado atual e fila de correção

Conferência de 23/10/2026, solicitada após a transferência de chat.
Ramo remoto vigente: `codex/otimizacao-android-r53`, commit
`255b98460197561f43e9d7c17c4458b43aae087b`.
`main` continua em `fbd6d156602958dc0f9da467a4a80100ad7b913f`;
há sete commits de continuação que ainda não estão em main.

Esta revisão usou checkout isolado, preservando o diagnóstico/ZIP anteriores.
Não houve escrita Google, alteração de script instalado, acionadores,
permissões, código de produção, commit, push ou merge nesta revisão.

## Conclusão principal

A otimização foi implementada e promovida à oficial pela continuação mais
recente. A falha Android da oficial continua aberta. Os relatos registrados
confirmam que uma cópia nativa feita DEPOIS da promoção abre e permite uso no
mesmo telefone, e também abriu no telefone de um amigo. A candidata C já abria.

Portanto, reduzir ainda mais o peso não é a primeira intervenção justificada
pela evidência atual. Conteúdo e código equivalentes em uma cópia funcional
exigem investigar diferenças de documento e contexto de abertura. Isso não
exclui contribuição do peso, nem identifica uma causa alternativa específica.
Não há evidência que justifique retirar mecânicas ou capacidade.

## Fila vigente localizada no Git

| Ordem | Problema | Situação e próxima ação útil |
|---|---|---|
| 1 | Oficial fica carregando indefinidamente no Android | Não resolvido. Isolar diferenças entre a oficial e a cópia funcional antes de outra migração. |
| 2 | Troca de cores lenta | Adiada pelo usuário até resolver a abertura. Existe correção local de leitura de propriedades após lock ainda não incorporada ao carregador instalado. |
| 3 | Quatro Sementes da rota Sem Técnica | Defeito independente ainda presente; corrigir extração, faixas e dropdown em etapa própria. |
| Manutenção | Smoke espera oito módulos, mas o pacote possui nove | Falha reproduzida nesta revisão; atualizar a conferência para o módulo leve de paleta e executar o smoke completo. |
| Manutenção | Geração integral GS antecede a guarda de zero das barras | Divergência confirmada; sincronizar geração antes de qualquer futura entrega integral. |

O topo de AGENTS.md, PROMOCAO-APLICADA-2026-10-23.json e
ANDROID-OFICIAL-FALHA-POS-PROMOCAO-2026-10-23.json prevalece sobre os estados
históricos de “oficial intacta” e “promoção pendente” abaixo nos documentos.
O teste do link direto à CARTEIRA já falhou e está concluído; não repeti-lo
como se fosse uma hipótese nova. O snapshot R52 é referência secundária.

## O que já foi feito pela continuação

- Promoção autorizada e concluída em 37 etapas, com preflight e releituras.
- 498 fórmulas FD/FX compactadas; 15.869 constantes de ANALISE convertidas.
- Removidas as oito colunas excedentes de ANALISE: menos 147.152 posições.
- Recuperação automática das constantes adaptada, incluindo apóstrofos.
- Três barras substituídas por SPARKLINE com guarda para valores/máximo zero.
- Defesa contra corte de strings no Workbook implementada; geração anterior
  validou 233.091 atribuições e maior texto de 17.729 caracteres.
- Contrato ANALISE A:D conferido na promoção: 73.576 células, 18.393 chaves,
  entradas, salários, nomes e proteção preservados conforme a evidência salva.
- Código incremental instalado relido integralmente na promoção, SHA-256
  `6112c6cf4ff34c88cea6c944b55aaf62a878e2310bb502b2ac5d2131f2d57e80`.
  O registro posterior compara o código da cópia com essa captura; não foi
  realizada nova leitura do Apps Script nesta revisão.

O último inventário completo da candidata C registra 121.311 fórmulas,
710.587 posições e 27.383.046 bytes de texto UTF-8 de fórmulas. São cerca de
21,1% menos texto e 11,6% menos fórmulas que o inventário inicial. A correção
posterior das barras altera marginalmente esse total; não atribuir esses bytes
exatos à oficial atual sem novo inventário completo. Não são medidas de RAM.

## Confirmação atual no Google, somente leitura

Oficial: `1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro`.
O modifiedTime retornado continua sendo `2026-10-23T16:38:21.310Z`, o mesmo
checkpoint registrado ao final da promoção. Metadados atuais: 27 abas,
710.587 posições, 60 regras condicionais, ANALISE com quatro colunas.

Amostras atuais confirmam:

- FD2 contém a fórmula compactada com LET, 10.371 caracteres;
- FX2 contém o aviso compactado, 16.831 caracteres;
- ANALISE!C5956 é texto literal, com apóstrofo e tipo string preservados;
- FICHA!S26/S30/S34 contêm SPARKLINE com guarda de zero;
- DADOS_AM!CS2:CS4 continuam usando CO1:CO2 para a rota correspondente,
  enquanto CS5 usa CO2:CO5. O catálogo fonte ainda tem `sementes: []`.

Foram localizados dois arquivos com o mesmo título de diagnóstico pós-promoção:
`1427V3IO_RSToQcsO1ZgAeArXoT_PdoHukN9jAVkBfy8` e
`1E9V_bvYXUsaCEmHr7dHa79REnRan9mopZ7JX7jkasMY`.
Ambos têm as mesmas propriedades de abas/grade e regras condicionais que a
oficial nesta leitura. O registro sanitizado não informa qual ID corresponde
ao teste funcional relatado. Identificar o controle correto antes de ensaio
que dependa de vincular o relato a um arquivo específico.

Essa conferência é focal; não é nova varredura integral das fórmulas, valores,
formatos ou automações. Não prova igualdade completa dos documentos atuais.

## Conferência do código e testes nesta revisão

Executados no commit 255b984, usando as dependências instaladas no ambiente:

- 23 testes unitários Python: aprovados, incluindo compactação/integridade.
- Runtime de cartões: 550 verificações aprovadas.
- Constantes: 603 conversões, sete restaurações e idempotência aprovadas.
- Paleta leve: igualdade de grade de cores, arte e fila; caminho leve sem
  carregar regras pesadas aprovado.
- Pacote: nove módulos, 25 abas-fonte, 249 contextos, geração
  `0c4547e1ace6efd9`; igualdade entre fontes GS versionadas e pacote aprovada.
- Teste de correção de abertura/âncoras/hash: aprovado.

O smoke geral NÃO passou: `nuvem-b47/conferir.py:65` exige exatamente oito
arquivos e omite PaletaAndroid.gs, que `r53/empacotar_script.py:33` publica.
Essa falha impede a execução automática do bloco posterior condicionado ao
sucesso inicial. Os testes focalizados acima foram executados separadamente;
isso não equivale a afirmar que o smoke completo passou. O workflow
`.github/workflows/nuvem.yml` usa esse smoke, portanto o verificador exige
manutenção. Não foi consultado resultado atual de execução remota do CI.

A geração montada a partir dos GS versionados foi inspecionada diretamente:
as três barras FICHA!S26/S30/S34 ainda não contêm a guarda de zero que existe
em `ficha-v01/ficha_pessoal.py:637` e na oficial. O teste de pacote passa porque
compara o pacote com esses mesmos GS. Ele não garante sincronismo com a fonte
Python nem com o delta instalado. Reempacotar GS antigos não resolve essa deriva.
Não promover o pacote integral atual como se refletisse todas as correções.

## Próxima investigação para a abertura

1. Fixar a identificação do controle funcional a partir das evidências/relato,
   preservando a oficial e a cópia que abre.
2. Reconciliar o estado instalado: código atual, propriedades do documento,
   estado de paleta pendente, acionadores e seus registros de execução. A
   evidência anterior conta três acionadores na oficial e zero na cópia; essa
   diferença é hipótese testável, não causa provada.
3. Correlacionar uma tentativa Android com horários e registros do Apps Script,
   verificando primeiro se ocorre execução ao abrir nesse cliente. Sem esse
   vínculo, não presumir que onOpen é o responsável.
4. Comparar conta/permissões e contexto do app para oficial e cópia. Cache,
   disponibilidade offline, histórico e estado específico do documento continuam
   hipóteses, sem contraprova que permita atribuir causalidade.
5. Escolher uma intervenção reversível por ensaio, com snapshot e critério de
   sucesso no mesmo aparelho. Alterar acionadores, substituir a oficial ou
   promover uma cópia não faz parte desta análise e exige escopo próprio.

O Google Drive/Sheets está acessível nesta sessão. Não há ferramenta exposta
de navegador ou Apps Script para reler código, propriedades e execuções.
Essa é uma dependência de acesso específica; não impede a análise de código
ou a leitura de células, e não exige necessariamente o PC anterior.

Sem executar construir/continuar, importar Office, reaplicar promoção, criar
acionadores, mudar permissões ou mesclar em main. A prioridade vigente é
resolver a abertura antes de retomar cores. As Sementes seguem separadas.

Logs e leituras desta revisão estão em
`nuvem-b47/saidas/retomada-auditoria-20261023/`, ignorado pelo Git.
Recomendação: GPT-6.1 Sol, High para a investigação de diferenças de documento;
Medium é suficiente para manutenção focal do verificador após definir o escopo.
