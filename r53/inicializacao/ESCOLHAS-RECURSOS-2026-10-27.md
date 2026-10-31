# Escolhas, recursos e condições · 27/10/2026

Continuação da PR 31 em rascunho. Main `57117fbe5c2361e6a09bfa00f037b4bcfaa8437f`
incorporada pelo merge `6d4ddf1`: a PR 38 só registra a instalação salarial e
backup 11 por outro trabalho. Não foram reaplicados nas oficiais. Rotinas
novas fora do pacote/bot e sem eventos, acionadores, endpoints ou modelo pago.

## Implementação

- Contrato público reproduzível das fontes, conferido sem regeneração pelo
  teste. Campos listados explicitamente, sem deduzir entradas por cor/estilo.
- 19 escolhas básicas; 20 recursos/bônus; nove condições/descanso. Alvos,
  defaults e instruções estão em `contrato_pessoal.gs`; APIs em `pessoal.gs`.
- Recursos atuais voltam às fórmulas de ligação ao máximo, sem copiar valor
  calculado. Máximos protegidos e fórmula pessoal desconhecida recusada.
- Notas de entrada voltam à fábrica, incluindo a instrução de Sequelas extras;
  cabeçalhos, fórmulas, formatos e validações ficam preservados.
- Executor recebeu escrita de fórmula e nota conhecida; mesma assinatura e
  diário financeiros v1. Quatro escritas por chamada, orçamento/retomada mantidos.

O teste inicial juntava as 29 entradas de cena e o diário excedeu 9.000 bytes.
Não se mudou o teste para aceitar isso. Os domínios foram separados e foi
adicionada guarda de bytes UTF-8 antes de qualquer gravação do diário.
A regressão com contexto grande exige zero escrita e ausência de diário.

## Validação offline

```sh
node r53/testes/inicializacao_financeiro.js
node r53/testes/inicializacao_progressao.js
node r53/testes/inicializacao_identidade.js
node r53/testes/inicializacao_pessoal.js
```

502 cenários passaram: 101/80/78 anteriores e **243 novos**. Todos os pontos de
escrita dos três domínios com falha antes/depois, repetição, nota nova após
uso, prévia antiga, fórmula/cabeçalho incompatíveis, imagem, preservação de
outros domínios, limite de quatro passos, contrato ausente, variantes nativas
positivas/negativas e diário abaixo de 9.000 bytes. VM não avalia fórmulas,
não valida latência Google nem certifica automações. Incluído no smoke Linux.

## CI Linux

Código `a55517deb9b77c43b796c80ac41f1029c0fdebd7` aprovado no
[run 40540295538](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40540295538) em 27/10 às 16:24:13 UTC
(13:24:13 Brasília). Log conferido: 101/80/78/243 cenários, pacote autossuficiente
de nove arquivos, regressões salariais/missões/editor, sintaxe de 277 fontes
Python/212 JS-GS, catálogo, progressão e Kaori. Run duplicado do push
40540284431 também concluiu aprovado antes da tentativa de cancelá-lo; não foi
possível cancelar um run já encerrado. Não somar as duas execuções como cobertura.
Registro posterior apenas documental com `[skip ci]`, sem nova bateria ou pacote.

## Leitura das oficiais

Somente leitura das duas oficiais: metadados de 30 abas e três intervalos
pequenos da FICHA. 112 conferências por documento entre rótulos, fórmulas
protegidas e entradas. Sete fórmulas inicialmente divergiam apenas porque o
Google remove aspas opcionais de FICHA e DADOS_PROGRESSAO; separadores também
são `;`. O contrato passou a incluir exatamente essas variantes, com testes
para preservar texto literal e recusar alteração de conta. Resultado final:
zero divergências nos dois documentos. Nenhuma alteração nas oficiais.

## Projeção no Sheets

Cópia **QA Carteira — escolhas e recursos — DESCARTÁVEL — 27-10-2026**,
`11PiUl5W…`, feita da oficial Ciclo. ID distinto, 30 abas, privada na pasta
ChatGPT e alvo FICHA conferidos antes das escritas. Grade e validações lidas;
opções de Caminho/Origem e descanso vieram das listas reais, sem trocar menus.

1. Inserir estado fictício e notas pessoais nas 48 entradas. Conferir todas
   antes de aplicar. Trilha ainda sem opção conservou seu convite no ensaio;
   a troca de Trilha preenchida é coberta na VM, não neste caso nativo.
2. Aplicar efeitos em três lotes de Sheets API (19/20/9), com máscaras só de
   conteúdo e notas. Não instalar Apps Script nem simular eventos.
3. Conferir 96 estados de conteúdo/notas: sem divergência; nota de Sequelas
   extras igual à fábrica, recursos com `=J26`, `=J30`, `=J34`.
4. Comparar 11.634 campos delimitados de conteúdo/nota não alterados,
   fórmulas, formato, validação e chips: zero diferenças. Não é comparação
   integral de todos os catálogos ou do workbook. Nenhum erro de cálculo
   retornado nos intervalos lidos. Recursos atuais/máximos 0/0, 0/0 e 25/25.
5. Exercitar depois as ligações: escolher Bastião, Constituição base 2 e
   Essência base 1 na cópia. Fórmulas dos atuais permaneceram; resultados
   atuais/máximos 23/23, 8/8 e 26/26. Não é nova análise de regras nem prova de
   onEdit — só recálculo nativo da ligação restaurada.
6. Conferir visualmente a FICHA e as condições de cena, sem refazer estilos.
   Enviar só essa cópia à lixeira; tela confirmou descarte e aba foi fechada.

**Foi projeção dos efeitos pelo conector, não execução dos novos perfis/diários
Apps Script, trava ou retomada. Não foi criação pela Carteira/OAuth das Guias.**
Não reutilizar essa cópia. Dados de ensaio fictícios; nenhuma ficha de jogador
foi editada. Nenhuma nova autorização Google ou escopo foi solicitado.

## Limites e continuação

A criação continua bloqueada. Restam Grau, treinos, capacidades de Origem,
técnica/Famílias, inventário, entidades/cartões/MONTAGENS, fotos/arte e
propriedades de recuperação/editor. A cópia de modelo pode reintroduzir estado
por cache/eventos: não declarar personagem pronto por ter estes diários.
Falta orquestração/conferência final conjunta, ativação, novo responsável e
ensaio real dos executores nas três classes de modelo e duas identidades.
Não reiniciar fases concluídas nem apagar diários. Sem merge em main/deploy.
Próxima implementação: GPT-6 Astra / Alto; revisão focal: Médio.
