# Campos visíveis dos cartões

Etapa 7 da Carteira viva, continuação de 28/10/2026. PR 31, sem instalação
ou integração de escrita no bot. Criação permanece bloqueada. Complementa
[MONTAGENS-2026-10-28.md](MONTAGENS-2026-10-28.md).

## Implementação

`cartoes.gs` fornece `r53NovaFichaCartaoPrevia(ss, ctx, id)` e
`r53NovaFichaCartaoAplicar(ss, ctx, id, assinatura)`. O ID seleciona um dos 249
cartões do contrato público; não aceita endereço ou perfil do navegador.

O contrato inclui nome, Classe e COMO É quando forem entradas, além dos campos
pessoais explícitos do editor: Forma, funções/pontos, Melhorias, Restrições,
Controle, uso pessoal e gasto de Frágil. Valores e notas voltam aos defaults
extraídos da montagem completa. Rótulos, fórmulas de contas/avisos e menus
fora das funções são preservados. Não limpa identidade/atributos/recursos das
entidades nem as versões guardadas em MONTAGENS ou caches persistentes.

A abertura das funções segue as mesmas portas do editor, com Amparo relido
sem cache e sua fórmula protegida. Só são aceitos Fechada, Livre, Neutra e
Normal; erro, vazio ou estado novo exige revisão. Função fechada recebe `—`;
aberta recebe zero ou checkbox desmarcado, conforme o cartão. O destino usa
a Classe de fábrica, depois de restaurar seu seletor. Os extras de entidade
aceitam Classe 0, mas o modelo atual começa em 1; não herdar a porta fechada
da Classe antiga nem mudar o default do modelo para satisfazer uma expectativa.

A validação é gravada antes do valor. Caixas podem alternar entre checkbox
padrão e lista contendo só `—`; pontos preservam a fórmula exata de validação,
com as variantes de idioma publicadas. Não afrouxa a fórmula de pontos nem
aceita qualquer lista/checkbox personalizado. Uma validação desconhecida
interrompe a prévia; menus preservados também entram na assinatura de estado.

`validacoes.gs` lê critérios, argumentos, permissão de inválidos e texto de
ajuda. O executor ganhou apenas o tipo `validacao`; os tipos anteriores,
contratos e assinaturas existentes foram mantidos. Fórmulas equivalentes e
checkbox padrão com argumentos booleanos explícitos são comparados pelo seu
significado conhecido. Não converte texto `sim/não` em checkbox padrão.

Um diário por cartão registra separadamente validações, valores e notas,
com quatro escritas por chamada e retomada. Queda entre a regra e seu valor
não exige reiniciar o diário. Conteúdo, notas, validações e estados de Amparo
alterados durante a execução não são sobrescritos. O diário contém hashes,
nunca o texto pessoal apagado. Cache volátil é invalidado nas entradas/saídas.
Não chama onEdit/r53Mostrar_, que gravariam estado adicional fora dos passos.

O mapa geral de áreas, esquema, campos/defaults e Amparo é verificado a cada
chamada. O contrato completo do cartão selecionado é verificado em separado,
evita recalcular todos os menus dos outros 248 cartões a cada retomada.

## Validação

- Leitura nativa das duas oficiais: nove contextos, incluindo o extra com
  Classe 0 opcional. Por arquivo, 124 entradas/notas, 210 guardas e 25
  validações de função, sem divergências. Fórmulas/estados de Amparo também
  reconhecidos. Nenhuma planilha foi escrita, copiada ou redimensionada.
- Sete regressões focais passaram: Classe antiga 0 → default 1; checkbox
  padrão explícito; idioma inglês; imagem; mescla nova; fórmula de validação
  com conta diferente. O ajuste das expectativas usou a célula de fábrica
  independente e variantes semânticas exatas; não alterou regra do produtor.
- 101 cenários financeiros e 441 de formação passaram novamente após ampliar
  o executor e a VM. O conjunto completo deste módulo é executado no CI;
  resultado e totais serão registrados no fechamento.
- A VM simula recusa de texto/número em checkbox e de valor fora da lista.
  Não executa fórmulas de validação nem certifica comportamento/latência do
  serviço Google. A prova de escrita Apps Script em descartáveis permanece
  pendente; leitura de contrato não é execução do inicializador.

Dados completos de leitura e comparação em
`nuvem-b47/saidas/cartoes-20261028/`, ignorados pelo Git. Protótipos permanecem
fora do pacote e do bot; não há ZIP ou publicação por esta extensão.

## Limite de armazenamento

Os diários completos dos 249 cartões ultrapassam a quota conjunta de
propriedades, embora cada um caiba abaixo de 9.000 bytes. A integração não
pode simplesmente executar todos e deixar todos os diários detalhados vivos.
Esse bloqueio é testado explicitamente. Precisa de orçamento global e um
protocolo de compactação/recibos que preserve vínculo, retomada e a recusa
à reinicialização de uma cópia já usada; apagar diários não é solução.

A referência Google consultada em 28/10 informa
[9 KB por valor e 500 KB por armazenamento de propriedades](https://developers.google.com/apps-script/guides/services/quotas).
Leitura/escrita dos critérios segue
[DataValidation](https://developers.google.com/apps-script/reference/spreadsheet/data-validation)
e [DataValidationBuilder](https://developers.google.com/apps-script/reference/spreadsheet/data-validation-builder).

## Continuação

Próximo: resolver retenção/orçamento dos diários antes da orquestração completa;
inicializar dados/recursos/equipamentos das entidades, arte, automações/treinos,
notas vivas, responsável e integração drive.file. Ensaiar ordem MONTAGENS →
campos visíveis → memórias finais, com eventos suspensos e conferência conjunta.
Não liberar criação pelo resultado isolado de um cartão ou da coleção offline.

GPT-6 Astra / Alto para implementação integrada; Médio para revisão focal.
Sem merge, deploy, escopo novo ou modelo pago nesta continuação.
