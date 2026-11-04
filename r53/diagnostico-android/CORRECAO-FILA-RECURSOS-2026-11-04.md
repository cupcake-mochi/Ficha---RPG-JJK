# Ajustes ± — correção de A03/A09, preparada para revisão

Base: PR59 `06b777f060a7305faa5feab975aa3f10cac3e44c`, sobre a pilha 51–58.
Ramo: `codex/correcao-fila-recursos-20261104`. Não houve aplicação no Google,
merge, edição de oficiais/jogador/PR31, novos acionadores ou mudanças de acesso.

## Problemas e mudança

A09: com saldo 20, duas edições −5 e −3 já entregues à célula deixavam 17:
a primeira execução lia o −3 mais recente e apagava a caixa antes da segunda.
Agora os eventos de célula única usam `e.value`; os dois eventos entregues,
na ordem testada, deixam 12. Isso vale no módulo completo, no atalho da FICHA
e nas 12 entidades. Um evento antigo de exclusão com `oldValue` não consome
uma nova entrada.

A03: colar em INVOCAÇÕES!X13:Y13 aplicava X13 e apagava também Y13 (reserva de
PE). A limpeza fica restrita à caixa ±. O mesmo vale nos dois lados das 12
entidades. A leitura imediatamente anterior à limpeza evita apagar uma entrada
de valor diferente já visível naquele momento.

`r53/recursos_delta.gs` é o motor comum, embutido em Codigo.gs e no atalho gerado.
A trava de documento serializa estes ajustes ±, com espera máxima de 1 segundo.
As gravações são enviadas antes de liberar a trava. Falha de trava ou escrita
emite aviso; o atalho não tenta aplicar de novo pelo módulo. A aritmética existente
foi preservada, inclusive os problemas fora deste escopo, como A08.

Na revisão da PR60, simulamos a recusa de −5 pela trava seguida da aplicação
de −3. O saldo termina em 17 e a caixa fica vazia. O aviso agora identifica
o valor recebido e a caixa, quando o valor já é conhecido, para que o usuário
saiba qual ajuste conferir. O aviso antigo só mandava olhar a caixa. O teste
novo falhou com o aviso antigo e passou com o novo. A recusa continua sem
repetição automática.

## Verificações

- `node r53/testes/recursos_fila.js`: 504 verificações, 18 rotas, onEdit completo
  e dispatcher rápido simulados. Duas entradas diferentes/iguais, TEMP, exclusão,
  limites, decimais, atuais vazios das entidades e colagens; falha da trava,
  falha depois da gravação, flush/liberação e ausência de segunda aplicação.
- `node r53/testes/recursos_fila_incremental.js`: 10 verificações portáteis;
  18 com snapshots privados recuperados das QA. Recusa de hash divergente,
  reaplicação e âncoras divergentes; paridade das funções; reversão byte a byte
  comprova preservação de todo o restante do Codigo e do módulo integrado.
- `node r53/testes/pacote_leve.js`: 134 verificações. A conferência dos remendos
  históricos desfaz as duas substituições posteriores exatas antes de comparar;
  não removeu a verificação do remendo 11 nem mudou suas expectativas.
- Atalho regenerado deterministicamente; mapa, gatilhos, marcas e hashes de
  origem preservados. Não houve regeneração dos catálogos pesados.
- O diagnóstico amplo segue com divergências intencionais dos demais achados;
  ele não é uma suíte inteiramente aprovada. O caso enfileirado do atalho agora
  entrega explicitamente os dois eventos, assim como o caso do módulo.

O smoke portátil (`python3 nuvem-b47/conferir.py --smoke`) terminou com código
0, incluindo descanso 66, cura 35 e SOCORRO 98. Os testes históricos de atalho
integrado, caixas horizontais e cartas custom pularam seus trechos dependentes
de exportação privada ausente; isso não conta como aprovação desses cenários.
A primeira rodada falhou na comparação histórica do remendo 11; após explicitar
a reversão das duas funções novas, a suíte focal e o smoke completo passaram.

Esses testes não são eventos nativos, não medem latência nem recálculo Google.
O controle de navegador está desativado no Work; os conectores disponíveis não
instalam/executam o Apps Script vinculado. Edições por API não testam onEdit.

## Instalação incremental ainda pendente

`preparar_recursos_fila.js` opera somente offline. Aceita o Codigo da integração
51–56, SHA-256 `8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0`.
Produz `e5338f56d61fc6a2e5e665db0219daccc3a6e91c7e49ec642c85e1bb70e717b9`.
O snapshot recuperado não substitui um snapshot atual antes de aplicar.

1. Habilitar o controle do navegador e criar cópia descartável da integração.
2. Capturar novamente o projeto inteiro; confirmar hash e guardar backup privado.
3. Preparar a proposta offline. O pacote troca o bloco exato do atalho e insere
   o patch das duas funções antes da instanciação do módulo. Preserva os trechos
   anexados de descanso, cura e SOCORRO e os fragmentos compactados.
4. Aplicar somente Codigo na cópia; salvar, recarregar e reler o código completo.
5. Editar pela interface: três ± do personagem e 12 entidades; −5/−3 seguidos,
   repetidos, TEMP, colagem com reserva vizinha, exclusão, decimais na localidade
   da ficha e reserva atual vazia. Confirmar a forma de `e.range` nas mesclagens.
6. Medir impacto da trava/flush, falhas por contenção e menus Recursos. Restaurar
   os campos da cópia e registrar evidências sanitizadas antes de promover a PR.

Não executar construir()/continuar(). Não usar o preparador antigo que substitui
o atalho até o fim do arquivo: ele descartaria os incrementos anexados.

## Limites que continuam abertos

- O Google enfileira no máximo dois eventos simples de onEdit. A correção não
  recupera eventos nunca entregues, nem garante ordem de chegada ou deduplicação.
  [Documentação de gatilhos](https://developers.google.com/apps-script/guides/triggers).
- `value`/`oldValue` estão disponíveis para edição de uma única célula. Colagens
  de intervalos continuam usando a célula atual; duas colagens já sobrescritas
  não podem ser reconstruídas por esse payload.
  [Objeto de evento](https://developers.google.com/apps-script/guides/triggers/events).
- A trava de documento também é usada por cura, descanso, SOCORRO e Famílias
  das invocações. Inclua uma dessas operações no ensaio de contenção. A trava
  não impede edições humanas entre a releitura e a limpeza. Não existe
  transação entre saldo/TEMP/limpeza; falha parcial exige conferir os saldos.
- Um segundo evento pode exceder a espera de 1 segundo e exigir reaplicação
  manual após aviso. A escolha do limite precisa do ensaio de latência nativa;
  não declarar resolvida toda a fila nem a demora de 19–20 segundos relatada.
  [Flush antes de liberar a trava](https://developers.google.com/apps-script/reference/lock/lock).
- A00/A01/A02/A04/A05/A06/A07/A08 e a limitação B01 da auditoria permanecem na
  fila documentada. Não houve alteração de regras para eliminar avisos legítimos.

Próxima ação: revisão Sol/Medium; ensaio nativo e ajustes Sol/High, sem alterar
configurações automaticamente. PR deve permanecer rascunho até o ensaio nativo.
