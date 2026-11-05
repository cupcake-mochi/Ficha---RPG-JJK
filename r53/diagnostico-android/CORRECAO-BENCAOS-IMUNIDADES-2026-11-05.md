> Atualização: a pendência custom foi corrigida em f8c86e5. Consulte
> `IMUNIDADE-CUSTOM-CORRIGIDA-2026-11-05.md` para o estado e o hash atuais.
> O registro abaixo preserva a etapa anterior.

# Correção de Bênçãos e imunidades

PR65, base PR64, implementação `6a35402`. Responde a B01, B02 e I01 de
`BENCAOS-IMUNIDADES-2026-11-05.md`. Sem merge ou alterações nas oficiais,
jogador, PR31, acionadores ou acesso. Livro de referência R66,
JJK---Project `e3058ad29180fdec2efec75b512446c49bf87b3d`.

## Comportamento

- Casco acrescenta metade do nível, para baixo, à vida máxima e +1 no
  TR de Vigor. Exige rota Sem Energia, Lapidação 7, Constituição 4,
  compra de Casco e orçamento suficiente. Não acumula por duplicação.
  Somar acumula; Trocar por continua definindo o resultado final, inclusive
  zero. Não cura vida atual nem aumenta Integridade.
- Corpo Amaldiçoado ignora as penalidades da Exaustão marcada no movimento
  e no aviso. O estágio digitado permanece registrado. Ao trocar a Origem,
  a nova regra é recalculada. Esta alteração não adiciona combate automático
  ou manipulação da condição Envenenado.
- O aviso de Exaustão também passa a usar o estágio efetivo de Vigília,
  como o movimento já fazia, sem remover o estágio real.
- Estímulo passa a indicar arma ou desarmado. A nota mantém a exclusão de
  Katas e a restrição de crítico, salvo permissão expressa de habilidade.

O gerador resolve nível, Origem e Constituição pelo índice de layout.
Contrato, chaves, tipos e endereços da ANALISE preservados. Comparação das
26 abas geradas encontrou somente os seis alvos abaixo e metadados de
geração novos; não houve alteração de grade, estilos, menus ou mesclagens.

## Entrega incremental

`preparar_bencaos_imunidades.js` exige SHA-256 da base PR64
`a09bf672a520e0750d239386f23f14e300eda84094668b7771cee605e028ebac`.
Produz Codigo com SHA-256
`170273ca8ecb3f7da41310dc1e15c37f89894775a4c16ebfa1af30f429c34310`.
O plano contém cinco fórmulas e uma nota: FICHA J26, O49, O67, AP109;
DADOS_AM KV67; nota FICHA AMALDIÇOADA L436. Não substituir coordenadas
globalmente. Planejar com snapshot novo, conferir as seis precondições,
aplicar os seis pedidos e o Codigo proposto, reler ambos. A reversão tem
precondições próprias. Nunca usar construir/continuar em ficha preenchida.

Fontes GS regeneradas e pacote conferido localmente. Nas duas descartáveis
foi instalado somente o incremental, não o pacote integral.

## Ensaios nas descartáveis Era e Ciclo

Treze cenários mecânicos em cada cópia:

| Caso | Resultado |
|---|---|
| Casco válido, nível 26 | Vida 261 → 274, Vigor 4 → 5; vida atual 6 e Integridade máxima 145 iguais |
| Constituição 3 | Vida 235 e Vigor 3, sem bônus |
| Lapidação insuficiente | Vida 189 e Vigor 4, sem bônus |
| Nível 30 | Vida 297 → 312, Vigor 4 → 5 |
| Orçamento excedido | Vida 261 e Vigor 4, sem bônus |
| Duplicata sem orçamento | Sem bônus; não esconde o excesso de compras |
| CONFIGURAÇÃO Somar 10 | Vida 284 |
| CONFIGURAÇÃO Trocar por 100 | Vida 100 |
| CONFIGURAÇÃO Trocar por zero | Vida 0 |
| Corpo Quebradiço | Vida 130 e movimento 0 m, sem bônus de Casco de outra rota |
| Corpo Amaldiçoado, Exaustão 2 | Movimento 9 m e aviso de imunidade |
| Sem imunidade, Exaustão 2 | Movimento 4,5 m |
| Vigília, Exaustão 2 | Movimento 9 m, aviso do estágio efetivo 1 |

A primeira fixture de CONFIGURAÇÃO omitiu a fonte H11. A ficha recusou a
entrada com #N/A e diagnóstico de entrada inválida. Os três casos foram
repetidos com fonte e passaram. A recusa legítima foi preservada; não se
alterou validação para produzir resultado verde.

Mais onze seleções por cópia conferiram nome, CE, requisito e texto completo
das cartas: Ímpeto, Presilha, Faro, Sem Pegada, Vulto, Esteio, Antecipar,
Represália, Sangue Frio, Campo e Assombro. Não foi automatizada nem simulada
a resolução de mesa dessas capacidades. Os cinco degraus de dano de
Estímulo têm ensaio anterior conforme o relatório de diagnóstico.

Oito edições reais pelo navegador, quatro em cada cópia, substituíram
J26, AP109, O67 e O49 por marcadores. O onEdit recuperou as fórmulas novas,
conferidas em releitura completa dos seis alvos. A auxiliar DADOS_AM não
foi tratada como campo com recuperação automática. Codigo foi salvo,
reaberto e relido com o SHA-256 proposto nas duas cópias. Não foi pedida
autorização nova. Texto do adicional inspecionado no layout nativo de ambas.

Dezenove entradas temporárias por cópia restauradas e relidas iguais ao
snapshot, incluindo CONFIGURAÇÃO C11:H11 e todos os atributos usados.
Os seis alvos incrementais permaneceram iguais ao plano novo. Evidências
privadas ignoradas em `nuvem-b47/saidas/bencaos-imunidades/`, sem dados ou
snapshots versionados.

## Verificações locais e limites

Teste focal dos seis alvos, preflight, reversão, idempotência, recusa de
base divergente e locales pt_BR/en_US passou. Teste de equipamento passou.
Smoke passou após atualizar as duas comparações históricas de fórmula para
reconhecer a cadeia estrita do novo plano. Os testes antigos de instalação
e rejeição de estado divergente continuam cobrando suas próprias bases.
Checks da implementação aprovados. Conferir novamente o head final.

Não é uma certificação de todas as mecânicas. Ainda cabem testes de borda
dos demais requisitos, cartas custom e situações de mesa. Uma futura
aplicação nas oficiais exige autorização própria, snapshot atual e ensaio
da pilha completa. PR31 permanece fora desta entrega.

Revisão recomendada Sol/Medium; novos ensaios Sol/High. Sem alterar ajustes.
