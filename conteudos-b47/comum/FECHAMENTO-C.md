# B47 — C concluída; parada antes de D

Em 16/10/2026, C foi concluída na
[revisão nativa autorizada](https://docs.google.com/spreadsheets/d/1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0/edit#gid=47001).
Não executar `construir` ou `continuar` nessa ficha preenchida. A migração foi
pontual: acrescentou cinco auxiliares e a área de cadastro, atualizou fórmulas
e validações e preservou os endereços das entradas e as abas de estudo.

## Conteúdos e provas

- Tipos de dano compartilhados com o livro; Condições nos mesmos 30 cartões
  e orçamento de Melhoria. Formas, Aptidões/Bênçãos e Talentos do personagem;
  Tipos e Talentos de entidade. Capacidades 10/10/10/10/10/20.
- Geração `9273911dd8b6f47a`: 35 GS, máximo 840.243 bytes, abaixo do teto
  de 900.000 por arquivo. Código das três frentes integrado no núcleo.
- Construção do zero apenas na descartável: 22 abas e leitura de 467.365
  células sem erro. Essa comparação com A+B identificou a restauração dos
  rótulos/defaults que o transporte antigo perdia; não se presume igualdade
  de toda a grade vazia entre os dois construtores.
- [Cenários preenchidos](CENARIOS-C-NATIVOS.json): 1.216 verificações,
  201 seletores de Forma, 985 saídas pareadas livro/alias, Técnica Máxima,
  24 cartas de Aptidões/Talentos, mecânica nas 12 entidades e interações com
  dano e Condição. Um alias gratuito é selecionável, sem virar capacidade
  inicial automática; avisos de Família mostram o nome literal selecionado.
  Pesos de Condição usam Leve/Média/Pesada, não número colado. Restauração
  dos valores/notas/validações confirmada em 18 blocos após os cenários.
- [Ensaio da migração preenchida](MIGRACAO-C-DESCARTAVEL.json) e
  [aplicação na revisão](MIGRACAO-C-REVISAO.json): backup nativo distinto,
  snapshot/releitura iguais, 26 abas, zero erros de fórmula e zero diferenças
  inesperadas de valores, notas ou validações. Não houve reconstrução na revisão.
- Revisão: 133 lotes e 7.025 pedidos após fracionamento; 63 blocos iniciais,
  63 de releitura e 76 finais. Conferidas 3.837 notas antigas e 83.677 células
  antigas com valor que não receberam escrita. Todas as 7.356 chaves antigas
  da ANALISE mantiveram seus valores, salvo a versão 10→11.
- ANALISE 11: 8.190 chaves únicas, fontes/ordem/escopos conferidos. O leitor
  mantém o mesmo único aviso anterior de escolhas de perícia incompletas.
  Nenhum novo aviso de conteúdo foi introduzido pela migração.
- [35 GS e manifesto da revisão](NATIVO-CODIGO-REVISAO-C.json) persistidos e
  relidos em sessão independente, com hashes iguais. O ensaio da migração
  também teve essa prova de persistência. Isso não declara auditoria D dos gatilhos.
- Testes offline de migração: 13 guardas, seis testes dos lotes e seis de
  normalização nativa. A normalização aceita representação numérica do Sheets
  (`9.0`/`9`, `1E99`/`1E+99`) e intervalo de uma célula (`A2:A2`/`A2`),
  preservando texto literal, booleanos, endereços e diferenças de valor real.

Os snapshots, recibos, dados crus e relatórios detalhados estão fora do Git,
em `D:/JJK - Project/B47/evidencias/2026-10-16/cd/`. O Git guarda somente código,
roteiros e provas resumidas sem os dados preenchidos. O backup da revisão
está identificado na prova publicada; não reutilizar os lotes de outra cópia.
Não importar XLSX. Calc continua ausente neste Windows; o recálculo descrito
acima foi feito no Google Sheets, não no Calc.

## Limite da parada

**D não foi iniciada.** Ficam para eventual autorização futura o acabamento
geral da interface, auditoria para retirar estudos/exemplos, revisão visual
completa, bateria geral de interações/gatilhos e entrega integral do projeto.
Não confundir isso com os testes focais e a migração necessários para concluir C.

Oficial, bot, main e acessos permanecem fora deste trabalho. Não há tarefa
agendada nem nova frente delegada. Modelo/esforço recomendado para uma
retomada solicitada pelo usuário: GPT-6.1 Sol, Médio; ler este fechamento e
o limite vigente antes de qualquer execução.
