# B47 C+D — integração das três frentes

Checkpoint de 16/10/2026. C está ligada no núcleo local; a prova nativa conjunta,
a migração pontual da revisão preenchida e o fechamento de D continuam em andamento.
O usuário transferiu para este integrador o trabalho que faltou quando os créditos
da frente Claude acabaram. Não há mais dependência de uma entrega futura dela.

## Origem e conciliação

- Base A+B: `dce00ab8a244f53218c978293d10c5c1894b1ef8`.
- Preparação comum: `0d4d64e2847dfea29b0e3804ab6f0853c52ea6fd`.
- Comuns: `7752c9115f168effe74092d125dfdd5352bd44a3`.
- Personagem: `e9af8d336716385488b442e31a6f1a596ed19068`, recebido pelo merge
  `3e7e842f9e8f924e1816e46915c5d248ab4cefff`; série `base-7752c91` 01 → 02 → 03.
- Entidades e revisão parcial: `045f6991f387787454c24f764a0b9d0b040574d0`,
  recebido pelo merge `3fda15ea61763022ceec4d041aa5733c64984169`.

O rascunho Claude `50bcc00` foi retirado antes desta integração. Sua retirada
permanece no histórico; não foi confundido com a entrega posterior. Os patches
concorrentes foram conciliados pelo integrador: comuns → personagem → entidades.
As entidades ficam depois de personagem, preservando os endereços já testados
de Formas/Aptidões/Talentos. `EntidadesAnalise.gs` recebe sua cauda própria;
nenhuma exportação nova volta ao arquivo principal já próximo do teto.

O contrato local é ANALISE 11, **8.190 chaves**: 7.356 anteriores, 80 de comuns,
524 de personagem e 230 de entidades. As primeiras 7.356 linhas mantêm identidade,
ordem, fontes e escopo, salvo a mudança explícita da versão. Bot permanece externo.
Capacidades: dez Danos, dez Formas, dez Aptidões/Bênçãos, dez Talentos do personagem,
dez Tipos de entidade e vinte Talentos de entidade. Condições compartilham os
trinta cadastros de Melhoria existentes. Não foram acrescentadas posições de uso.

## Correções da integração

1. Menus de Condição usam faixas auxiliares estáticas por cadastro. O constructor
   Apps Script não aceita `INDIRECT(IF(...))` como endereço de `getRange`, embora
   a validação REST aceite essa expressão. As listas alternam entre os 83 nomes
   de Melhoria e as 14 Condições do livro.
2. Registro permanente dos novos transportes no emissor, incluindo os fragmentos
   numerados de Formas. Leitores Python e carregador JS recompõem as mesmas abas.
3. Complementos tardios de valores copiados são reexpandidos, com precedência
   das exceções explícitas e idempotência. As duas ordens de chegada foram testadas.
4. O limite de linhas nativo inclui alturas declaradas em linhas finais vazias.
5. Vazios de texto do livro são emitidos como `=""`, evitando que `INDEX` devolva
   zero e invalide uma herança. Forma sem segundo componente permanece no grau 0.
6. Campos numéricos/lógicos das linhas custom inativas devolvem 0/FALSE. Isso
   resolve a causa dos achados P7/P7b da revisão Claude. Resumos das cartas do
   livro continuam os resumos anteriores; descrições completas ficam nos cartões.
7. Entidades têm guardas de capacidade/aplicação repetida, categoria numérica
   inteira 1–3 e requisitos literais visíveis no texto do talento selecionado.
8. Definição e efeito do Tipo aparecem como nota no seletor existente da invocação.
   A DEFINIÇÃO livre do jogador é preservada. A ajuda herda a base válida e
   respeita texto explícito; o gatilho conserva notas manuais, limita a prévia
   longa e mantém o conteúdo integral no cadastro/exportação.

Os achados P1–P3 e P7/P7b foram tratados nas fontes canônicas. A revisão Claude
foi parcial: não é apresentada como leitura integral ou recálculo preenchido
concluído. O integrador assume essas verificações restantes.

## Prova local deste checkpoint

Fontes alteradas sobre `3fda15e`; os hashes da geração identificam o conteúdo
efetivamente testado, pois o SHA sozinho não identifica a árvore ainda não publicada.
Geração `9273911dd8b6f47a`: **35 GS**, **7.067.846 bytes** no total; maior
`Configuracao.gs`, **840.243 bytes**, todos abaixo de 900.000. **22 abas**.

- 75 testes focais de personagem, sem falhas/erros.
- 7 testes da combinação: contrato/ordem, campos, consumidores, notas e mesclagens.
- 3 testes estruturais adicionais do módulo canônico de entidades: capacidades
  10/20, 5/7 e 1/1, preservação das doze definições livres, exportação e guardas
  de capacidades inválidas, início sobreposto e aplicação repetida.
- 37 checagens do carregador em 20 ordens: 22 abas/8.190 chaves, valores completos
  iguais à referência Python, ausências e gerações divergentes recusadas.
- Compactação/reexpansão Python/JS: 22 abas de produção e três fixtures.
- 150 checagens da construção simulada, em três fases; construção interrompida e
  retomada equivalente à integral. A VM foi completada com `getDisplayValues`,
  método real do Apps Script exigido pela nova ajuda contextual.
- 9 testes das notas: preservação manual, atualização, limpeza, idempotência,
  texto longo, leitura delimitada e abertura de cópia.
- Smoke: 180 fontes Python, sintaxe de 45 JS/GS e catálogo/progressão/Kaori.

Modelos e logs atuais ficam ignorados em `nuvem-b47/saidas/cd/`. Estes testes
não recalculam fórmulas. Calc não está instalado neste Windows; os resultados
Linux/Calc da frente Claude são evidência reportada por ela, não execução local.

## Prova nativa focal já feita e seus limites

Comuns: descartável `1BzVzrqjKsarh6DCAu6FGZ_yOxy0aBzttfX4n1JH2QFI`.
As 48 asserções iniciais, 12 reusos e restauração de 29 campos permanecem válidos
para aquele ensaio. Mais 90 pedidos corrigiram as validações estáticas; primeira
e última vaga passaram 83 → 14 → 83 opções, com modalidade restaurada.

Personagem + comuns: descartável `1mZaDlSvdYsAcsD-2dJmX5GG0Geo2ObJBJFhA0sFwTok`.
104 lotes/1.343 pedidos confirmados uma única vez. Depois, 211 vazios tipados
do livro e dez fórmulas de segundo componente foram corrigidos. Resultado:
291 asserções de herança e 91 asserções em dez cenários negativos/literais/sem
base, 94 entradas restauradas exatamente, 31.580 células finais sem erro.
Essas duas cópias conservam GS e ANALISE principal v10: foram ensaios focais
com exportação técnica auxiliar, sem migração da revisão e sem consumidores
completos de C. Não provam a geração integrada atual nem o fechamento de D.

Nova descartável para construir o pacote completo:
`14Ad8e5hUECLimCFuilEGSIxrhv0IWpDUEjEBR4N8N-Q`, cópia nativa da descartável
A+B `12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc`.
Projeto vinculado confirmado pela navegação Extensões → Apps Script:
`1YUnYSyI_BeRGKeRY2gVRK_oEDduiCDUmENdD9LQMn2rfcTSJ_ZTFX5vR`.
**35 GS e manifesto salvos e relidos integralmente iguais** após recarga,
também conferidos pelo verificador independente da infra. A leitura pelo
clipboard normaliza exclusivamente CRLF para LF, antes de comparar o texto
integral e os hashes das fontes locais LF. Sem remoções ou arquivos inesperados.
[Hashes e comparação](NATIVO-CODIGO-INTEGRADO.json).

Ao iniciar `construir` exclusivamente nessa nova descartável, o Google abriu
“Autorização obrigatória”. O usuário foi chamado a concluir a autorização do
novo projeto. Após a confirmação dele, a solicitação antiga foi encerrada e a
execução foi iniciada novamente, às 20:41:27 locais. Construção em andamento;
nenhuma migração C aplicada na revisão preenchida. A prova de código persistido
já está encerrada; a prova de execução/recálculo ainda não. A primeira tentativa
parou às 20:41:49 com falha do serviço Planilhas em `insertSheet` (primeira aba).
Metadados relidos confirmaram apenas `__montando__`, sem preenchimento de C;
a construção foi reiniciada exclusivamente nessa descartável.

Evidências completas privadas: `D:\JJK - Project\B47\evidencias\2026-10-16\cd`.
Não versionar leituras da ficha, backups ou dados do jogador.

## Próximos passos obrigatórios

1. Concluir a construção em andamento somente na nova descartável. Os 35
   GS/manifesto já foram relidos iguais e o usuário concluiu a autorização.
   Testar a combinação preenchida, todos os consumidores
   e as notas/gatilhos em cópia funcional sem ativação manual.
2. Concluir D: auditoria dos menus e dependências, acabamento/visual, texto e
   cópia. Retirar estudos apenas após auditar dependências nativas reais.
3. Preparar migração própria v10 → v11, com backup/snapshot novos, cobertura de
   todas as células alteradas e guardas relidas imediatamente antes da escrita.
   Não reutilizar os 102 lotes históricos v9 → v10 nem rodar construir/continuar
   na revisão preenchida. Validar primeiro numa cópia descartável da revisão.
4. Só então migrar pontualmente a revisão autorizada, preservar entradas/notas,
   validar ANALISE/leitor, código persistido, visual e gatilhos e publicar a prova.

Oficial, bot, main, acessos e dados da revisão preenchida permanecem intactos.
Próxima ação: GPT-6.1 Sol, High, para testes nativos e migração guardada.
