# Descansos de Existência Artificial

PR66, empilhada sobre PR65 `5f6abea`. Corrige D01/D02 da
`AUDITORIA-DESCANSO-ORIGENS-2026-11-05.md`. Livro R66 em
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`,
Existência Artificial → Repouso. Os demais requisitos para descansar
continuam necessários.

## Alteração

`regraDoDescanso_` calcula o local efetivo sem modificar a tabela comum.
Corpo Amaldiçoado publicado ou custom válida com essa base considera
qualquer local propício. O curto preserva o grau antigo marcado; a regra
de local propício impede que ele reduza a recuperação. O longo aplica
a recuperação normal do local propício. O resumo explica a exceção.

Para herança custom, `descansar_` lê B121:B127 da DADOS_CUSTOM uma vez.
Só B121 verdadeiro e B123 igual à base publicada concedem a exceção.
Essa leitura também fornece B126/B127 para as regras corporais anteriores.
A Origem publicada Artificial e os corpos publicados conhecidos dispensam
essa leitura. Não foi medida uma nova latência; não há promessa de ganho
de velocidade ou de recuperação de eventos perdidos pelo Google.

## Transporte e atualização futura

A entrega incremental muda somente Codigo.gs de uma instalação com
PR65 revisada. `preparar_descanso_origens.prepararCodigo` exige SHA-256
`19ae4c19660ce322f6cf3df8041469f8a65a7cfa18a9260c7c32f2c760ec77ac`.
A proposta é
`d5845c0367be94e63f12b799053d5432d0ec4af5beea3a3d05bf32b607a2a084`.
Três funções exatas são conferidas antes de qualquer substituição.
Base divergente, âncora duplicada ou aplicação repetida são recusadas.
O pacote integral também foi empacotado com a fonte corrigida; não foi
instalado nas fichas. Os catálogos e moldes não foram regenerados.

`reverterFonte` serve apenas à conferência de extratores e incrementos
históricos. O teste do módulo completo continua usando a fonte nova;
o teste específico compara as três substituições com essa mesma fonte.
Não se remove a correção do pacote destinado à instalação.

Uma futura promoção exige snapshot novo, confirmação da cadeia anterior,
preparação, ensaio em cópia e releitura do código salvo. Não executar
construir/continuar, nem reaplicar catálogos para esta correção.
Nenhuma autorização para oficiais ou merge foi usada nesta etapa.

## Validação local

- Descanso: 78 cenários aprovados, incluindo limites, imutabilidade da
  tabela, custom válida/inválida, base Nenhuma, corpos especiais e queda ativa.
- Transporte: fonte final idêntica, recusa atômica e replay sobre o pacote
  antigo real aprovados; Código proposto compilado sem executar serviços.
- Pacote leve: 138 verificações aprovadas. O smoke completo passou após
  ajustar o teste histórico para desfazer somente as três funções exatas.

## Validação nativa

Codigo.gs foi salvo, reaberto e relido integralmente nas duas descartáveis
com o SHA-256 proposto acima. Sete cenários mecânicos por cópia e uma
recusa de descanso normal com queda ativa por cópia passaram inicialmente.
Após a autorização pelo usuário, o comando de descanso com queda ativa
também passou nas duas cópias: 18 cenários nativos no total.
Os eventos foram edições reais de D45; a API preparou e restaurou os estados.
O menu voltou ao estado inicial e o resumo foi conferido antes de mudar
a montagem. Não se contabilizaram leituras durante o processamento como
resultados concluídos.

| Cenário | Era | Ciclo |
| --- | --- | --- |
| Artificial, curto fora, Exaustão marcada 3 | PE 0 → 15; grau 3 preservado | PE 0 → 5; grau 3 preservado |
| Artificial, longo fora, Exaustão marcada 3 | Vida 6 → 77; PE 0 → 60; grau 0 | Vida 6 → 37; PE 0 → 20; grau 0 |
| Latente, longo fora | Vida 6 → 38; PE 0 → 30 | Vida 6 → 18; PE 0 → 10 |
| Custom válida com base Corpo Amaldiçoado, curto fora | PE 0 → 15 | PE 0 → 5 |
| Mesma custom com rota incompatível, curto fora | PE permaneceu 0 | PE permaneceu 0 |
| Corpo Exaurido, longo propício | Vida 6 → 25 | Vida 6 → 15 |
| Recuperação Abundante, curto propício | PE 0 → 24 | PE 0 → 8 |
| Morrendo, longo pelo menu normal da célula | Recusado, recursos e registro preservados | Recusado, recursos e registro preservados |
| Artificial em Morrendo, longo fora pelo menu Recursos | Vida 0 → 77; PE 0 → 60; grau 0; queda encerrada | Vida 0 → 37; PE 0 → 20; grau 0; queda encerrada |

Os máximos naturais da montagem eram vida 77/37 e PE 60/20. B121/B123
foram relidos como válido/base correta no controle positivo e inválido/base
vazia no negativo. A custom inválida não recebeu benefício por ter o texto
da base escrito no cadastro. Os ensaios assumem os requisitos de segurança
e permissão da mesa para realizar o descanso.

**Ensaio de menu concluído:** o Google exigiu autorização nas duas cópias,
concluída pelo usuário. Novo snapshot foi salvo e os registros de Morrendo
foram preparados novamente. Pela interface Recursos → Descanso longo com
queda ativa, informou-se 2 (fora de lugar propício). As duas cópias aplicaram
a exceção, zeraram Exaustão e Sequelas e gravaram Encerrado no descanso.
Referência, Classe, escolha, necessário, tratamento zero e janela foram
preservados no registro. O resumo explica o local efetivo e o encerramento.
O ensaio usou registros controlados por API; não é um novo teste de
Registrar queda nem das conversões de tratamento, cobertas em outras entregas.
Não há pendência conhecida deste lote; não certifica todas as mecânicas.

Vinte e três campos de entrada por cópia foram restaurados, incluindo o
cartão custom, e SOCORRO A1:C30 foi restaurada. Releitura de 432 células
materializadas por cópia encontrou zero diferenças em valores/fórmulas,
notas e validações em relação ao snapshot inicial, e zero erros nos
intervalos conferidos. Isso não é uma nova varredura integral da ficha.

Após o ensaio autorizado, as mesmas 23 entradas por cópia e SOCORRO foram
novamente restauradas a partir do snapshot fresco. Releitura ampliada de
1.074 células materializadas por cópia encontrou zero diferenças em
valores/fórmulas, notas, validações e formatos de célula, e zero erros nos
intervalos conferidos. D39 e os campos escritos pelo registro de socorro
também estão nessa comparação. Os dados temporários de Morrendo foram
desfeitos. Nenhum código precisou mudar depois dos 16 cenários iniciais.

Snapshots, leituras e recibos permanecem em
`nuvem-b47/saidas/correcao-descanso-origens/`, ignorado pelo Git. O JSON
ao lado deste relatório contém somente resultados sanitizados.

Sem merge, oficiais, jogador, PR31 ou acionadores novos. Autorizações
das duas cópias concluídas pelo usuário; nenhum acesso concedido pelo agente.
Sol/Medium para revisão; Sol/High para futuros ensaios. Não mudar ajustes.
