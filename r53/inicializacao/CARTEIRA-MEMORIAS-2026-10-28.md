# CARTEIRA e memórias · 28/10/2026

Protótipo da PR 31, etapa 7 da Carteira viva. Não instalado e criação bloqueada.
Main do produtor ef361cc e bot de42447 reconferidas; branches iguais ao remoto,
árvores inicialmente limpas. Nenhuma integração de main necessária.

## Campos

Perfil carteira: CARTEIRA!O13, O27 e O30, conteúdo e notas de fábrica. Guardas
em 12 cabeçalhos/espelhos. O27 é o nome realmente consumido por DADOS_AM; um
sentinela antigo do teste de técnica usava D24, que é só uma posição vazia.
O teste foi corrigido para O27 e ganhou prova independente na montagem completa.
Servidor Z22, nome O9, jogador AK22, foto C8 e emissão AT3 preservados por este
perfil. Identidade e financeiro já tratam seus próprios campos; foto continua
pendente. Não limpa áreas por cor nem o interior das mesclas.

## Memórias

Contrato gerado do EditorR53: 253 chaves conhecidas, quatro caches
(r53_versoes, r53_marcas_custom, r53_amparo_direto, r53_amparo_sujo) e 249
r53_classe_visivel_<contexto>. Onze grupos fixos de até 24, cada qual com diário
independente. A assinatura do editor confere armazenamento, IDs e Classes;
fonte divergente exige revisão. A lista não encolhe durante a retomada.

Recuperações r53_recuperacao_<timestamp de 13 algarismos> são inspecionadas
pelos nomes, sem copiar seu conteúdo. Cada uma recebe prévia/diário próprio,
com seletor estrito. Isso mantém a identidade da operação mesmo depois de
excluir a propriedade, sem depender de um manifesto de tamanho variável.
Namespace desconhecido provoca recusa; demais propriedades ficam preservadas.
Não há deleteAllProperties, escrita em células, rede ou instalação automática.

Executor financeiro reutilizado sem alteração: trava, hashes antes/depois,
quatro escritas por chamada, 210 s e diário até 9.000 bytes. Cache volátil do
editor invalidado após aplicação/falha para impedir releitura do estado antigo
no mesmo processo. Memórias recriadas após conclusão não são apagadas de novo.
A inspeção final ainda pode indicar recuperações criadas durante outras fases.

## Verificações desta rodada

- 441 cenários de formação/CARTEIRA (24 novos).
- 155 cenários novos de memórias: todos os grupos, falhas antes/depois de cada
  escrita nos grupos extremos e recuperação, idempotência, concorrência,
  contrato inválido, alvo oficial, trava, conteúdo grande e leitura real do cache.
- 101 financeiros passaram; layout/assinatura financeira v1 preservados.
- Hashes dos nove contratos de formação anteriores preservados.
- Total esperado no CI: 1.100 (101/82/78/243/441/155). Conferir resultado abaixo
  antes de declarar a coleção completa aprovada nesta rodada.
- Leitura das duas oficiais: 15 entradas/guardas cada e as três notas de entrada,
  zero divergências com variantes exatas dos separadores. Sem escrita.
  Uma consulta de metadados recebeu 429; repetição posterior foi suficiente.
- Nenhuma cópia criada, projeção de escrita ou execução Apps Script nesta rodada.
  PropertiesService/retomada nativa seguem sem prova nativa deste código.

## Próximo

Entidades, cartões e MONTAGENS; fotos/arte; orquestração, conferência conjunta,
automações/notas vivas, novo responsável, integração executável drive.file e
ensaio completo com falha/retomada. Os protocolos isolados não autorizam
cadastro. Manter a cópia inacessível ao jogador durante a sequência; automações
não podem repor dados enquanto a inicialização está em andamento. Não zerar
os diários para ignorar essas diferenças. Não houve merge, deploy, pacote
publicado, modelo pago, escopo novo nem edição de oficial/jogador.

Implementação seguinte: GPT-6 Astra / Alto. Revisão focal: Médio.
