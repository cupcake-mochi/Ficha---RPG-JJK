# Ajustes ± da PR60

## Reteste da correção em 04/11/2026

A leitura do evento reconhece a vírgula decimal quando a planilha usa pt-BR.
A trava aguarda até 12 s. O script usa a leitura feita sob a trava para
decidir se limpa a caixa e envia as gravações juntas. Antes, reler a caixa
depois de escrever os saldos introduzia um envio intermediário. A janela
entre leitura e limpeza continua sem proteção contra edição humana.

A mesma descartável recebeu Codigo.gs com SHA-256
`6aec0d0a1e88f777475bc7578fc231c982f0d9b08783c6e8fbe90becdf920455`.
A releitura após salvar confirmou o hash e os outros nove arquivos GS
mantiveram seus hashes. A API preparou e relê os saldos. Cada comando
abaixo foi inserido pela interface.

| Cenário | Resultado observado | Duração de onEdit |
| --- | --- | --- |
| Vida 20 com −5 e −3 seguidos | Vida 12 e caixa vazia | 20,105 s e 11,191 s |
| PE 8 com −1,5 em pt-BR | PE 6,5 e caixa vazia | 13,370 s |
| Vida 10 e TEMP 3, colar −5 e 7 em INVOCAÇÕES!X13:Y13 | Vida 8, TEMP 0, X13 vazio e Y13 igual a 7 | 20,006 s |
| Integridade 20 e TEMP 3 com −5 | Integridade 18, TEMP 0 e caixa vazia | 11,590 s |
| Vida 12 com −2 isolado | Vida 10 e caixa vazia | 12,539 s |
| PE 6,5 com −2 isolado | PE 4,5 e caixa vazia | 9,610 s |

Os dois eventos rápidos começaram no intervalo de um segundo no registro.
Os tempos são do onEdit inteiro. A colagem anterior levou 29,260 s e
a desta rodada levou 20,006 s. Uma execução por versão não mede ganho típico.
Os 12 campos de teste foram restaurados e relidos iguais. O Google não pediu
autorização. Os 11 redutores restantes e os menus não fizeram parte do reteste.

Passaram 543 verificações locais em 18 rotas, 18 verificações incrementais com
snapshots privados, 134 do pacote leve e o smoke portátil. A espera continua
limitada e o aviso de recusa permanece. Os descontos testados são comutativos.
Uma mistura de ganho e perda ainda pode depender da ordem de execução do
Google. O gatilho também pode deixar de entregar eventos em rajadas maiores.

## Primeiro ensaio nativo em 04/11/2026 (histórico)

Foi criada uma cópia descartável da QA integrada da Era. O hash atual de
Codigo.gs era `8a0f2ed6…`. Apenas Codigo.gs recebeu o patch de `26ce13e`.
Depois de salvar e recarregar, o arquivo tinha o hash previsto `e5338f56…`
e os outros nove arquivos GS mantinham seus hashes. Os comandos da tabela
foram inseridos pela interface. A API serviu para preparar e reler os
saldos. A planilha tinha localidade pt-BR.

| Cenário | Resultado | Duração de onEdit |
| --- | --- | --- |
| Vida 20, digitar −5 e −3 em FICHA!AM26 | **Falhou.** Vida 15 e −3 permaneceu na caixa. O esperado era 12 e caixa vazia. O Google entregou ambos os eventos e registrou contenção no segundo. | 18,185 s e 7,735 s |
| Vida 10, TEMP 3, colar −5 e 7 em INVOCAÇÕES!X13:Y13 | **Passou.** Vida 8, TEMP 0, caixa ± vazia e vizinha Y13 igual a 7. | 29,260 s |
| Vida 15, digitar −2 isolado em FICHA!AM26 | **Passou.** Vida 13 e caixa vazia. | 17,156 s |
| PE 8, digitar −1,5 em FICHA!AM30 | **Falhou.** PE 8 e a caixa reteve o número −1,5. O esperado era PE 6,5 e caixa vazia. | 5,716 s |
| PE 8, digitar −2 na mesma caixa | **Passou.** PE 6 e caixa vazia. | 14,549 s |
| Integridade 20, TEMP 3, digitar −5 em FICHA!AM34 | **Passou.** Integridade 18, TEMP 0 e caixa vazia. | 14,602 s |

A execução que recusou o segundo desconto registrou “ajuste ±: outro ajuste
de recurso ainda está em execução”. Os tempos são de cada onEdit inteiro.
Eles não isolam a duração da trava nem o custo de flush. A hipótese para o
decimal é que o texto localizado do evento não passa em `Number(e.value)`.
O teste confirmou o efeito na planilha, mas não capturou o texto do evento.

Nesse primeiro ensaio, A03 passou e A09 e decimais impediram o aceite.
A duração observada na colagem ficou perto do limite do gatilho simples.
Antes de repetir as demais rotas, corrigir o tratamento de números localizados
e rever como processar dois ajustes entregues que disputam a trava. Os outros
11 redutores continuam com cobertura local. Menus, exclusão e medições da
trava isolada não foram testados nesta rodada.

Os 12 campos editados foram restaurados e relidos iguais, inclusive fórmulas
e vazios. O patch permanece somente na descartável. Os eventos testados
não exigiram autorização. A PR60 fica em rascunho.

Base: PR59 `06b777f060a7305faa5feab975aa3f10cac3e44c`, sobre a pilha 51–58.
Ramo: `codex/correcao-fila-recursos-20261104`. A preparação anterior ao ensaio ocorreu sem aplicação no Google.

## Preparação e revisão anteriores ao ensaio (histórico)

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

A bateria acima é local. Para os eventos nativos, veja o resultado no início deste registro.

## Procedimento para instalação incremental

`preparar_recursos_fila.js` opera somente offline. Aceita o Codigo da integração
51–56, SHA-256 `8a0f2ed68117420c28df342f5fee4621ea648eb6aa32765a75a620bccba8b7a0`.
Produz `6aec0d0a1e88f777475bc7578fc231c982f0d9b08783c6e8fbe90becdf920455`.
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
- Um segundo evento pode exceder a espera de 12 segundos e exigir reaplicação
  manual após aviso. A escolha do limite precisa do ensaio de latência nativa;
  não declarar resolvida toda a fila nem a demora de 19–20 segundos relatada.
  [Flush antes de liberar a trava](https://developers.google.com/apps-script/reference/lock/lock).
- A00/A01/A02/A04/A05/A06/A07/A08 e a limitação B01 da auditoria permanecem na
  fila documentada. Não houve alteração de regras para eliminar avisos legítimos.

Próxima ação: revisão Sol/Medium; ensaio nativo e ajustes Sol/High, sem alterar
configurações automaticamente. A PR permanece em rascunho para revisão após o reteste.
