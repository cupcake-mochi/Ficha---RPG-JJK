# Versões guardadas dos cartões

Continuação da etapa 7, em 28/10/2026. Protótipo da PR 31, sem instalação,
integração com o bot ou liberação de criação. Oficiais e fichas de jogadores
permaneceram intactas. Este registro complementa CARTEIRA-MEMORIAS-2026-10-28.md.

## O que foi implementado

`montagens.gs` acrescenta `r53NovaFichaMontagensPrevia(ss, ctx, id)` e
`r53NovaFichaMontagensAplicar(ss, ctx, id, assinatura)`. O ID identifica um
cartão conhecido do editor; não aceita faixa, endereço ou perfil do navegador.

Cada um dos 249 cartões tem seu próprio diário. A rotina restaura os 33 campos
de todas as suas Classes aos valores de fábrica e remove notas pessoais
nessas entradas. São 48.015 posições no conjunto. Isso inclui feitiços comuns,
Liberações, Classe 0, Técnica Máxima e os quatro tipos de cartões das entidades.
A versão deixa de estar preparada; permissões, distribuições, dependências,
restrições e textos do personagem anterior não são reaproveitados.

Fórmulas dos títulos e das Classes máximas, números das Classes, rótulos,
formatos e instruções dos cabeçalhos são preservados. Valores recalculados do
nome e da Classe não fazem parte da identidade: suas fórmulas exatas fazem.
Fórmula inesperada numa entrada, rótulo alterado, validação ou mescla no bloco
causam recusa. O contrato é extraído da montagem completa e comparado com o
esquema, campos, defaults e endereços do editor instalado. Não usa cor de célula
para inferir permissão de escrita. Somente variantes exatas de fórmula são aceitas.

O executor financeiro e os contratos anteriores não mudaram. Continuam valendo
trava, assinatura, retomada, limite de quatro escritas por chamada, orçamento de
210 segundos e diário abaixo de 9.000 bytes. Uma matriz parcialmente gravada ou
edição concorrente desconhecida exige revisão; não há rollback cego. O diário
guarda hashes, nunca o conteúdo removido. Cache volátil é descartado ao sair.

## Validação

- 370 cenários offline novos passaram: todos os 249 contextos; queda antes/depois
  de cada escrita nos oito modos; repetição, concorrência, edição após uso,
  fórmulas, validações, mesclas, seleção inválida, oficial/arquivo registrado e
  corrupção de diário. O teste usa também o leitor real de versões do editor.
- 101 cenários financeiros passaram novamente; não houve alteração no executor.
- Os 249 diários sintéticos totalizaram 178.035 bytes; todos ficaram abaixo de
  9.000 individualmente. Isso não certifica a quota global de propriedades de
  uma cópia com os demais domínios, caches, automações e recuperações.
- Nas duas oficiais, leitura nativa de oito contextos representando os oito
  modos: por arquivo, 990 entradas e 310 guardas, sem divergências. Entradas
  sem notas ou validações. Metadados confirmaram MONTAGENS oculta com 9.467
  linhas e nove colunas. O fonte completo declara 12 colunas, mas os alvos
  conhecidos ficam dentro das nove existentes; não foi redimensionado nada.
- Dados de leitura e comparador ficaram em `nuvem-b47/saidas/montagens-20261028/`,
  ignorados. Nenhuma cópia, edição nativa, execução Apps Script ou OAuth novo.

A coleção anterior tinha 1.100 cenários; com este módulo são 1.470. O resultado
do CI desta revisão será registrado no fechamento, sem repetir a suíte do bot
por alterações exclusivamente documentais no consumidor.

## O que ainda falta

**MONTAGENS não é o cartão visível.** Os valores e validações dos campos
visíveis precisam ser inicializados juntos: o editor transforma funções
bloqueadas em listas contendo `—`, enquanto a fábrica usa números/checkboxes.
Não copiar defaults por cima dessas regras sem um protocolo próprio.

**MONTAGENS também não é o cache persistente.** O teste demonstrou que o leitor
real ainda encontra a versão antiga em `r53_versoes` após limpar as células.
Executar depois o grupo de memórias que remove esse cache faz o leitor voltar
aos defaults de todas as Classes. A orquestração deve impedir eventos/uso do
editor durante a limpeza, terminar as memórias e só então conferir o conjunto.
A rotina nova não apaga propriedades persistentes por conta própria nem atesta
que os outros 248 cartões já terminaram.

Próximos blocos: cartões visíveis/validações; entradas e recursos das entidades;
arte; orçamento global e ordem dos diários; automações/notas vivas/treinos;
novo responsável; integração drive.file e prova nativa completa. Não apagar
os diários para repetir sobre uma ficha usada. **Criação continua bloqueada.**

Para continuar: GPT-6 Astra / Alto; para revisão focal: Médio. Sem mudança
automática de modelo, merge em main, publicação ou novos acessos.
