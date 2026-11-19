# Imunidade herdada corrigida — PR65

Implementação `f8c86e5`, resolve o P2 de `REVISAO-PR65-2026-11-05.md`.
O gerador agora considera a Origem publicada ou a base Corpo Amaldiçoado
de uma Origem custom válida. Consulta B121 e B123 da DADOS_CUSTOM; não
infere herança de nome parecido nem do texto bruto de cadastro inválido.
A condição vale tanto para o aviso O49 quanto para o movimento O67.
O estágio de Exaustão marcado permanece registrado.

## Preparação incremental

Fontes regeneradas e pacote conferido. Comparação com a versão anterior
encontrou apenas duas fórmulas alteradas: FICHA O49 e O67, além dos
metadados de geração. Não houve mudanças de layout, estilos, menus,
contrato ANALISE ou dados de personagem.

O preparador da PR65 continua aceitando a base PR64 com SHA-256
`a09bf672a520e0750d239386f23f14e300eda84094668b7771cee605e028ebac`.
Agora também expõe `atualizarCodigoRevisao` e `planejarRevisao` para
descartáveis com a primeira PR65 instalada. Essa rota exige Codigo
`170273ca8ecb3f7da41310dc1e15c37f89894775a4c16ebfa1af30f429c34310` e
snapshot atual das duas fórmulas. Seu plano próprio tem reversão guardada.
As duas rotas produzem o mesmo Codigo final, SHA-256
`19ae4c19660ce322f6cf3df8041469f8a65a7cfa18a9260c7c32f2c760ec77ac`.

O plano integral desta PR continua com seis alvos. A revisão de dois alvos
não deve ser aplicada sobre PR64 ou em fichas sem a primeira PR65.
Não usar construir/continuar ou substituir coordenadas globalmente.
O pacote integral regenerado não foi instalado nas fichas.

## Ensaios nativos nas duas descartáveis

Sete cenários por cópia, usando o cadastro geral da reprodução anterior:

| Caso | Validade/base | Resultado |
|---|---|---|
| Origem publicada, Exaustão 3 | Corpo Amaldiçoado | Imune, 9 m |
| Origem custom, Exaustão 3 | Válida, base Corpo Amaldiçoado | Imune, 9 m |
| Custom sem base do livro | Válida, Nenhuma | Penalidades, 4,5 m |
| Custom com base declarada mas rota incompatível | Inválida, base efetiva vazia | Penalidades, 4,5 m |
| Custom revalidada | Válida, base restaurada | Imune, 9 m |
| Outra Origem publicada | Latente | Penalidades, 4,5 m |
| Custom válida sem Exaustão | Válida, base Corpo Amaldiçoado | Imune, 9 m |

O grau 3 permaneceu marcado nos casos que o usaram. Não se removeu a
Exaustão para fazer o teste passar. MESTRE VIU permaneceu falso: é um
lembrete, não aprovação mecânica no bot. Os diagnósticos de cadastro
inválido foram preservados.

Depois, duas edições reais do grau (uma por cópia) mantiveram a custom
em 9 m com grau 3. Quatro sobrescritas reais, O49 e O67 em cada cópia,
recuperaram as fórmulas novas automaticamente. Codigo foi salvo, reaberto
e relido nas duas cópias com o SHA-256 final. Nenhuma autorização nova
foi pedida. Aviso e movimento conferidos visualmente no Google Sheets.

Dez entradas por cópia restauradas e relidas iguais ao snapshot. O
movimento voltou ao 0 m original da montagem de Restrição corporal.
Os seis alvos da PR65 foram relidos iguais ao plano final, não somente
os dois desta revisão.

## Verificação e limites

Teste focal passou com preflight, reversão, recusa de base incorreta,
idempotência e locales pt_BR/en_US. A atualização do Codigo anterior
produziu exatamente o mesmo resultado da preparação a partir da PR64.
Smoke local aprovado; os dois checks do commit de implementação passaram.
Conferir também o head final com este relatório.

Snapshots, pedidos e resultados estão somente em
`nuvem-b47/saidas/imunidade-custom/`, ignorado pelo Git. Não foram editadas
as oficiais, jogador ou PR31; sem merge, acionadores ou acesso novo.
PR31 relida no hash `765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`.

Esta rodada corrige a pendência de herança; não certifica todas as
mecânicas da ficha. Os limites de cobertura das rodadas anteriores continuam
documentados. Sol/Medium para nova revisão, Sol/High para novos ensaios.
Não alterar configurações automaticamente.
