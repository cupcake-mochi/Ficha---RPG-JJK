# CONFIGURAÇÃO horizontal — trabalho em andamento

Pedido posterior à entrega B47: limpar notas inúteis, organizar listas
recolhíveis para a direita como as invocações e ocupar o vão ao lado dos
cartões custom. Autorizado editar a oficial para esse redesenho; não usar
construir/continuar. Não mexer no bot ou em permissões, nem importar XLSX.

Estado atual: **somente cópia de ensaio alterada; oficial ainda vertical**.
Cópia `1tVDYqhLpBc2ag174OON5qnmiqeZJrM3rQlATagcKt_8`.
Painel reorganizado: 14 listas, grade de 400 × 238; 25 cartões gerais em
pares. 2.575 notas genéricas/duplicadas removidas, 1.434 ajudas preservadas
(incluindo 14 orientações de lista). Geral ganha índice no vão à direita.

Primeira comparação nativa: 8.190 chaves e valores de ANALISE iguais,
zero diferenças em A:B. Ainda faltam a auditoria dos endereços publicados,
menus/notas/cartões, prova dos textos longos e visual final; depois código,
backup novo, migração da oficial, releitura final e remoção da cópia temporária.

Fontes novas: `ficha-v01/configuracao_horizontal.py` faz a transformação
final; os testes mecânicos de domínio continuam exportando antes dessa etapa.
`acabamento-b47/reorganizar-configuracao.py` emite pedidos REST offline,
preservando entradas por cópia nativa e atualizando referências, sem rede.
O leitor INDEX antigo de Melhorias/Restrições virou referência direta à mesma
célula, necessária quando os cadastros deixam de compartilhar uma matriz vertical.

Recibos e modelos na pasta privada
`D:/JJK - Project/B47/evidencias/2026-10-17/pos-d/`, prefixo `horizontal-`
ou `configuracao-horizontal-`. Ensaio foi aplicado em 44 lotes, com recibos
00–43. O lote 42 foi rejeitado antes de aplicar por nomes de propriedades;
corrigido para gridProperties, aplicado com sucesso. Fundo novo reparado em
30 retângulos e índice aplicado. Não repetir os 44 lotes no ensaio atual.
Títulos verticais e links ajustados para o topo. Há uma abertura visível por
lista, sem repetir explicações em cada cartão/célula, conforme esclarecimento
do usuário. Formas explica ALC, P, E, Classes e TR. Os pares de cartões têm
largura igual; a introdução fica acima deles.

Checkpoint de código: geração completa pelo gerador canônico, incluindo
XLSX de fábrica (sem dados de personagem). Ensaio nativo: 2.960 campos e
1.110 validações preservados; 1.434 notas idênticas ao alvo; ANALISE sem
diferenças em chaves/valores e origens remapeadas corretamente; zero erros
na CONFIGURAÇÃO. O comparador aceita só normalizações sintáticas do Sheets
(aspas opcionais de nomes simples). Validações são comparadas ao snapshot
nativo, incluindo caixas de seleção, não a regras exclusivas do XLSX.

O transporte copyPaste também copia regras condicionais e deixou restos da
geometria anterior. Corrigido no ensaio: 27 regras canônicas, sem duplicação;
o planejador agora remove as regras da origem temporária e do destino antes
de copiar, depois instala as 27 já remapeadas.

`testar-configuracao-horizontal.js`: quatro cenários de altura compartilhada
passaram, inclusive limpar o texto de outra categoria mantendo a categoria
longa, e restaurar o piso ao limpar todos. Uma leitura em lote por edição.
`conferir-configuracao-horizontal.py`: prova de preservação por snapshots;
saída com contagens/coordenadas, sem dados do personagem.

Publicação do ensaio em andamento, com hash antes de salvar e espera do
salvamento de cada arquivo. Ainda falta releitura 36/36 após recarregar,
teste nativo de edição, backup novo, migração oficial e limpeza dos temporários.

Próxima ação: Sol/Médio para continuar a auditoria e publicação; aumentar
esforço se surgir diferença mecânica. Não declarar a oficial horizontal antes
de concluir as provas e a publicação nela.
