# R53 — plano de integridade e abertura no Android

Data: 23/10/2026. Base: `main` em `fbd6d156602958dc0f9da467a4a80100ad7b913f`.
Estado vigente: **B e C abrem nos aparelhos fracos; C recebeu a compactação de
efeitos/avisos, redução da grade e 15.869 constantes literais; varredura final
sem erros e geração íntegra. Cores adiadas por pedido do usuário.**
Leia primeiro [a retomada atual](diagnostico-android/RETOMADA-2026-10-23.md).
Os parágrafos seguintes registram as etapas preliminares do pacote recebido.

**Prioridade atual:** [ensaio A/B da abertura](diagnostico-android/ENSAIO-ANDROID.md).
A fatoração é aplicada diretamente às fórmulas nativas de uma cópia atual.
Corrigir gerador, sementes ou barras não é pré-requisito desse ensaio.
Esses achados independentes continuam registrados; nenhum explica por si só
a falha de abertura. P0–P5 abaixo descrevem o plano amplo, não uma ordem
que deva atrasar o teste no aparelho.

**Revisão encerrada em 23/10:** leia primeiro o
[fechamento técnico](diagnostico-android/REVISAO-FINAL.md). Ele classifica as
diferenças e registra 89 casos nativos aprovados. Acrescenta os defeitos de
sementes/barras, a alternativa de não materializar FD e a necessidade de
preservar a restauração da ANALISE. A oficial permanece intacta; os testes
de equivalência ocorreram em uma QA sintética separada; depois, foi preparado
o ensaio A/B de abertura em cópias completas, descrito no link acima.

A falha de abertura no app Google Planilhas do Android está confirmada pelo
usuário, inclusive em seu celular. O arquivo afetado foi identificado como a
[ficha oficial](https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit).
O objetivo é torná-la utilizável nesses aparelhos preservando suas mecânicas.
A causa exata e a eficácia de cada correção precisam de ensaio no aparelho.

## 1. Pente-fino: o que está estabelecido

O [inventário sanitizado](diagnostico-android/INVENTARIO-2026-10-23.json)
registra contagens por aba, hashes e diferenças sem fórmulas ou dados pessoais.
Foram lidas 710.587 posições em 72 blocos, com máscara de fórmulas/erros,
mais as 147.152 posições excedentes de ANALISE, lidas separadamente para
valores/notas/validações. A soma cobre a grade de 857.739 posições.
O modifiedTime permaneceu igual durante o inventário. Não houve escrita Google.

| Medida | Situação verificada |
|---|---:|
| Abas nativas | 27 |
| Fórmulas na planilha publicada | **137.180** |
| Texto UTF-8 dessas fórmulas | **34.725.005 bytes** |
| Erros de fórmula retornados no escopo lido | **0** |
| Fórmulas em DADOS_R53 | 44.607; 22.919.293 bytes |
| FD: efeitos dos cartões | 249 fórmulas; 8.877.041 bytes |
| FX: avisos dos cartões | 249 fórmulas; 5.240.399 bytes |
| Efeitos + avisos / texto de fórmulas nativas | **40,7%** |
| Maior fórmula nativa observada | 35.364 caracteres |
| Fórmulas constantes de texto em ANALISE!C | 15.869 |
| ANALISE!E:L sem valores, notas ou validações | 147.152 posições |
| Exportação atual | 18.393 chaves únicas |
| Cartões/contextos e versões possíveis | 249 / 1.455 |

### Correção da contagem preliminar

Os 70.098 registros mencionados na primeira análise são moldes compactados,
não todas as fórmulas que o gerador instala. `ficha/modelo.gs.js` copia os
retângulos `abaixo` durante a montagem. Expandindo esses retângulos, a fonte
atual produziria **135.735 fórmulas / 34.183.989 bytes**. A base pré-R53
ccbd053 produziria 64.243 fórmulas / 9.041.150 bytes.

Não tratar a diferença entre 70 mil e 137 mil como fórmulas descartáveis.
A compressão do script economiza transporte; os cálculos copiados continuam
existindo na planilha. A comparação expandida encontrou 134.569 fórmulas
canonicamente iguais, 1.163 diferentes, três ausentes e 1.448 adicionais
na nativa. Isso é uma fila de reconciliação, não uma lista de exclusão.
Parte das diferenças é esperada, como a instalação incremental de salários.

### Defeito de integridade confirmado no gerador

Dez moldes de `DADOS_R53!FD` estão cortados em 32.767 caracteres, com
parênteses incompletos. Sua propagação produziria **249 fórmulas incompletas**.
A contraprova atribuiu a fórmula nativa de 33.634 caracteres ao Workbook:
o valor passou a 32.767. `monta.py` usa essa atribuição antes de o emissor ler
o valor. As fórmulas nativas consultadas estão completas e sem erro retornado.

Portanto, é obrigatório corrigir a geração antes de qualquer reconstrução
ou promoção desses dados. Esse defeito não prova a causa da falha móvel.
Os testes atuais de AST/pacote não bastam para detectar uma fórmula que foi
cortada na passagem pelo Workbook.

### Outros alvos confirmados

- O texto de efeitos duplica expressões ao construir sufixos condicionais
  (`IF(condição, texto & sufixo, texto)`), depois repete a construção. Fatorar
  o texto comum é um alvo concreto sem retirar regras ou explicações.
- As validações repetem buscas, inclusive pares de opções nas quatro posições
  de Melhoria. `nome` e `rotulo_base` têm significados distintos: não podem
  ser substituídos um pelo outro numa tentativa de simplificação.
- ANALISE tem 34.247 fórmulas. As 15.869 constantes da coluna C representam
  **11,6% do total nativo**, não 22,6%; o percentual anterior usava os moldes.
- Existem 60 regras de formatação condicional. Só as três de INVOCAÇÕES
  cobrem 174.636 posições somadas; as de FICHA AMALDIÇOADA, outras 28.203.
  São alcances sobrepostos, não células únicas nem estimativa de RAM.
- O pacote atual descompacta cerca de 22,7 MB de fonte ao carregar o módulo
  completo. A abertura simples ainda delega ao módulo. Isso é custo de
  Apps Script, separado da memória do aplicativo Android.

### Revisão de viabilidade da fatoração · 23/10

Um experimento somente em memória substituiu as duas construções de sufixos
dos efeitos por concatenação condicional: `IF(c, texto & sufixo, texto)`
passa a `texto & IF(c, sufixo, "")`. Não alterou arquivos de produção,
o Workbook, o pacote publicado nem a planilha.

Com os mesmos intervalos sintéticos antes/depois, a fórmula de efeitos da
linha 2 passou de **33.653 para 10.797 caracteres**; na linha 100, de
35.381 para 11.309. Isso representa aproximadamente **68% menos texto nessa
fórmula**, não 68% menos memória ou tempo de abertura da ficha. Os 89 cenários
existentes passaram na base e retornaram dicionários idênticos no experimento
(16.287 campos comparados, incluindo entradas e resultados).

A [evidência de viabilidade](diagnostico-android/VIABILIDADE-FATORACAO-2026-10-23.json)
registra as medidas e limitações. O avaliador Python não certifica coerções,
propagação de erros ou desempenho do Sheets; ainda é necessário ensaio nativo.
Essa evidência prioriza a fatoração dos efeitos como primeira intervenção
de código na implementação: ela também pode evitar o corte atual no Workbook.
Mesmo assim, manter a verificação explícita contra truncamento no gerador,
para que uma fórmula futura não reintroduza silenciosamente o defeito.

Na varredura das fórmulas nativas não apareceram NOW, TODAY, RAND,
RANDBETWEEN, funções de importação externa ou faixas de coluna inteira.
Há 525 ocorrências textuais de INDIRECT, que exigem cuidado ao rastrear
dependências. Não atribuir a causa a funções voláteis sem evidência.

## 2. O que permanece incerto

- Modelo do aparelho, versão do Android/app e comportamento exato: fechamento
  do aplicativo, alerta, tela travada ou carregamento prolongado.
- RAM/pico de memória, tempo até a primeira tela e até a primeira edição.
- Identidade atual do código vinculado e logs no momento da falha. O código
  instalado não foi relido nesta sessão; o inventário é de Sheets e Git.
- As diferenças fonte/nativa foram classificadas. Resta conferir código
  remoto e consumidores externos antes de remover resultados ou resíduos.
- Contribuição individual de cálculos, formatação, imagens e acionadores.

Esses pontos não colocam em dúvida a falha relatada; delimitam o diagnóstico
e os ensaios necessários. Bytes, quantidade de fórmulas e grade não medem RAM
nem garantem percentuais proporcionais de melhora.

## 3. Preservação obrigatória

Preservar por padrão:

- regras R53: custos, limites, dados, cura, PV temporários, Controle, TR,
  alcance/área, Amparo, restrições, efeitos e exceções;
- 249 contextos, 1.455 versões possíveis, escolhas por Classe, Classe 0,
  básicas, Liberações e máximas; alternância sem perda de pontos ou texto;
- 12 invocações, nove posições de Família por invocação e autonomia individual;
- catálogos do livro e custom, capacidades atuais e reutilização;
- vida, PE, progressão, perícias/ofícios, equipamentos e demais contas;
- dados pessoais, notas manuais, imagens e configuração do jogador;
- salários, datas, ciclos, histórico, idempotência e saldo manual;
- contrato ANALISE12/esquema2: mesmas chaves, fontes, tipos, valores e versões,
  com leitura estável pelo consumidor existente, sem alterar o bot;
- cópias funcionais, automação disponível hoje e nenhuma nova ativação ou
  dependência de rede sem explicitar o impacto.

Ocultar uma funcionalidade, exigir mais cliques ou trocar cálculo automático
por atualização manual também altera comportamento. Registrar esses efeitos;
não classificá-los como otimização gratuita.

## 4. Plano em etapas e entregáveis

### P0 — fechar integridade e linha de base

1. Guardar backup nativo, snapshot completo das entradas/notas e código remoto;
   o inventário de fórmulas desta auditoria não substitui esses snapshots.
2. Usar a classificação encerrada das 1.163 diferenças, três ausências e
   1.448 adições. Preservar salários e a entrada manual AH11; conferir código
   remoto e consumidores externos antes de qualquer remoção.
3. Corrigir o corte das fórmulas na geração; comparar o modelo anterior à
   serialização, o artefato emitido e as fórmulas instaladas no ensaio.
   Acrescentar contraprova com fórmulas acima de 32.767 caracteres e recusa
   explícita de cortes. Fatoração pode evitar o limite, sem eliminar validações.
   Corrigir também a extração vazia das quatro sementes e sua lista nativa,
   em intervenção separada: a revisão reproduziu a regressão dessa rota.
4. Medir a ficha identificada no Android afetado e registrar a falha como
   resultado da linha de base. Criar uma cópia de controle idêntica.

Entrega: fonte reconciliada, geração íntegra e ficha de medições. Não executar
construir/continuar na oficial nem reaplicar lotes históricos.

### P1 — isolar a causa em cópias diagnósticas

Usar o mesmo conteúdo, conta, rede e condições comparáveis. Cópias não levam
acionadores instaláveis: registrar/configurar essa diferença antes de comparar.

| Ensaio | Pergunta respondida |
|---|---|
| Cópia idêntica, sem otimização | Copiar o documento sozinho muda a falha? |
| Cópia com cálculos congelados em valores | Quanto da falha depende do cálculo/grafo? |
| Cópia com apresentação simplificada | Quanto depende de formatação/imagens/grade? |
| Execução sem rotinas de abertura, quando aplicável | Qual é o custo dos acionadores? |

O congelamento e a simplificação são experiências descartáveis, nunca versões
de entrega. Manter uma variável por ensaio; consultar logs quando disponíveis.
Uma cópia sem acionadores não comprova que a otimização resolveu a original.

Entrega: evidência que ordena os próximos passos. Sem acesso ao aparelho,
marcar o teste como pendente, não como sucesso.

### P2 — reduções sem alteração pretendida de comportamento

Ensaiar separadamente:

1. **Grade excedente da ANALISE:** reduzir de 12 para quatro colunas somente
   depois de conferir também dependências, intervalos nomeados, proteções e
   consumidores. Mantém todas as linhas/chaves. Remove 147.152 posições da
   grade atual, mas não promete redução igual de RAM ou tempo.
2. **Constantes da ANALISE:** testar texto bruto em vez de fórmula na coluna C,
   preservando apóstrofos, endereços e CSV. Aceitar somente com igualdade de
   leitura; não apagar chaves. Teto dessa intervenção: 15.869 fórmulas.
   A igualdade nativa de texto passou em cinco casos; preservar também a
   restauração por devolverConta_ e validar CSV/consumidor. Converter apenas
   as células não fecha essa dependência.
3. **Formatação condicional:** restringir o alcance às células que realmente
   precisam dos avisos, comprovando aparência e mensagens antes/depois.
   Não remover estados de inválido ou ocultar avisos para economizar cálculo.

Entrega: delta de estrutura, contrato igual e medições no Android por mudança.

### P3 — fatoração do motor R53

A numeração agrupa frentes, não impõe concluir toda a limpeza estrutural antes
de atacar fórmulas. A fatoração dos efeitos deve começar junto da correção de
integridade em P0, com ensaio isolado antes de combinar com P2. Não há motivo
para aguardar todas as reduções de grade para testar esse alvo comprovado.

- Priorizar FD/efeitos e FX/avisos: juntos, aproximadamente 14,1 MB de texto
  nativo, ou 40,7% do total. Também revisar cálculos repetidos em DADOS_INVOC
  e DADOS_AM depois de mapear seus consumidores atuais.
- Reutilizar expressões semanticamente iguais, preservando ordem e conteúdo
  das mensagens. Estudar LET versus poucas auxiliares com medições; acrescentar
  muitas colunas pode trocar um custo por outro.
- Evitar duplicar blocos de texto inteiros para acrescentar sufixos. Não cortar
  instruções, restrições ou efeitos como atalho para diminuir a fórmula.
- Preservar tratamento de vazio, zero, FALSE, erro, nomes `* ? ~`, aliases e
  cadastros custom. Evitar ciclos e mudanças no momento em que um erro aparece.
- Executar casos nativos. O avaliador Python sozinho não exercita a fórmula
  serializada; o defeito de corte mostrou essa lacuna.

Entrega: fórmulas menores com resultados e mensagens iguais, medidos na cópia.

A fatoração de FD passou em 1.113 cenários locais e nos 89 cenários nativos.
FD não apresentou consumidores nas fórmulas, validações, formatação ou
referências literais de INDIRECT examinadas. A revisão prevê avaliar deixar
de materializar esse resultado após conferir código remoto e consumidores
externos. Não excluir a coluna física nem somar esse ganho ao da fatoração.

### P4 — abertura e carregamento

Investigar uma abertura simples que não descompacte toda a construção quando
só precisa dos controles. Preservar continuação de paleta pendente, revisão
instalável, salários, cópias e retomada após interrupção. Evitar duplicar módulos
ou acionadores. As correções publicadas de abertura em 20/10 já existem;
não apresentá-las como trabalho novo.

Esse eixo pode melhorar espera de serviços, mas não elimina sozinho o peso
das fórmulas no cliente. Medir separadamente; não atribuir ganhos móveis a VM.

### P5 — alternativas estruturais, somente se necessárias

| Alternativa | Mecânicas | Custo/risco de comportamento |
|---|---|---|
| Materializar cálculos apenas quando usados | Pode preservar integralmente | Invalidação de cache, atualização ao mudar campanha/custom e primeira edição; provar funcionamento nas cópias/Android |
| Interface móvel leve com motor completo preservado | Pode preservar cálculos e catálogo | Novo produto/fluxo, rede, autenticação, manutenção e migração; exige desenho próprio |
| Versão de consulta congelada | Perde edição e atualização automática | Serve como contingência explícita, não substitui a ficha completa |
| Cortar invocações, cartões, versões ou catálogos | Reduz funcionalidade/capacidade | Não propor como primeira solução; exige necessidade demonstrada e decisão específica do usuário |

Não há evidência atual que torne necessária a retirada de uma mecânica.
Se as etapas anteriores falharem, apresentar qual operação/capacidade seria
afetada, por que isso resolveria o limite observado e quais alternativas
preservariam a regra. Não realizar cortes preventivos.

## 5. Testes e critérios de aceitação

- Android que falhou: ao menos três aberturas com app recém-fechado e três
  reaberturas; registrar falhas, tempo até tela utilizável e primeira edição.
  Não limpar cache/reinstalar entre variantes sem registrar a mudança.
- Android de controle e computador: verificar regressão. Não limitar o aceite
  a um aparelho que já conseguia abrir.
- Três cargas em cópias: padrão, personagem representativo e carga alta com
  dados sintéticos dentro das capacidades. Nunca preencher testes na oficial.
- Executar os 89 casos R53 existentes, negativos e herança/custom; conferir
  nativamente tudo que tiver fórmula emitida alterada, não apenas AST.
- Testar as 12 entidades/nona Família, autonomia, Amparo abrir/fechar, custos,
  Classe 0/máximas, pontos, textos longos e alternância rápida de Classe.
- Preservar a correção flush/lock de 20/10: três rodadas de 12 trocas rápidas,
  valores por Classe e leitura estabilizada. Medir salvar, fechar e reabrir.
- Contrato: igualdade das 18.393 chaves atuais, fontes, partes, valores/tipos
  e versões em cada cenário; nenhum erro/aviso suprimido indevidamente.
- Salários: créditos, datas e ciclos iguais; nenhuma duplicação de pagamento
  ou acionador, O86 e saldo preservados. Usar os 112 testes e cenários nativos
  pertinentes quando sua dependência for alterada.
- Restaurar valores/notas/alturas dos testes; conferir menu, paleta, imagens,
  primeira/última vaga e cópia funcional.

Aceite: abrir e permitir uso nos aparelhos afetados sem perda de dados ou
mecânicas, com equivalência demonstrada e melhora registrada. Três tentativas
são um critério funcional inicial, não garantia para todos os modelos Android.
Definir alvo de tempo após medir o aparelho, sem prometer segundos arbitrários.
Uma redução no número de fórmulas que não resolva a abertura não encerra o caso.

## 6. Publicação e continuidade

Este pedido autoriza planejamento; nenhuma etapa de otimização foi aplicada.
Na implementação, trabalhar em ramo separado da base reconciliada, com commits
por intervenção, snapshots novos e ensaio. Antes de promover, registrar delta,
evidências e procedimento de recuperação que preserve alterações posteriores.
As escritas Sheets são atômicas por lote, não por sequência. Não repetir
cegamente limpeza, remoção de colunas ou migrações após timeout.

Não alterar bot, permissões ou main por este plano. A oficial permanece somente
leitura nesta etapa. Dados pessoais, snapshots e código remoto privado ficam
fora do Git; no PC podem ser organizados em `D:\JJK - Project` conforme a
autorização anterior. Não depender do HD antigo para reproduzir o gerador.

Materiais disponíveis: inventário, reconciliação encerrada, contraprovas,
auditoria das 6.440 validações e 60 regras condicionais, equivalência local
e nativa da fatoração e regressões locais aprovadas. A ação imediata é medir
as cópias A/B no aparelho. Para futura publicação ou mudanças estruturais,
ler o código vinculado, obter snapshot/backup atuais e conferir nomes e
proteções não expostos. Corrigir o gerador antes de regenerar o pacote. A revisão não
equivale à aplicação das correções ou à resolução da falha Android.

Referências técnicas: [limites no Android](https://support.google.com/docs/answer/6000292?co=GENIE.Platform%3DAndroid&hl=en)
e [desempenho do Sheets](https://support.google.com/docs/answer/11468464?hl=en).

Recomendação para a próxima ação: **GPT-6.1 Sol, High**, para implementar
as intervenções isoladas com os critérios de validação definidos.
