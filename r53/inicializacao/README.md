# Inicializar uma cópia nova

Protótipo do produtor para a etapa 7 da Carteira viva. **Não instalado nas oficiais, não
incluído no pacote e sem integração de escrita com o bot.** A criação pelo
bot permanece bloqueada. Não executar em ficha oficial ou de jogador.

O modelo do servidor é a ficha do sistema com configurações extras da mesa.
A cópia deve conservar essas regras e catálogos; não deve herdar identidade,
progressão, inventário, missões, cartões ou dinheiro de outro personagem.
Os protótipos cobrem financeiro, nível/base de XP, 14 textos pessoais,
19 escolhas básicas, 20 entradas de recursos/bônus, nove condições/descanso e
268 campos de Grau/Origem, Perícias, Ofícios/TR e armas, mais 11 entradas do
cabeçalho da técnica e 19 estados de Famílias. **Não oferecem uma ficha inteira
pronta para cadastro.** Base incorporada: main
`ef361ccdf7a0210781176e3c42d318cde147553d`, merge `a72adc0` (PRs 41–43).
Inclui XP manual e marcas de missões congeladas. A instalação/backup 13 das
oficiais foi feita por outro trabalho; não reaplicar nem reabrir a otimização.

## Financeiro

`financeiro.gs` fornece prévia, aplicação explícita e retomada com trava do
documento. Não registra menus, eventos, endpoints ou acionadores e não é
importado pelos geradores do pacote. A integração futura terá de chamar essa
rotina a partir de um criador confiável de cópias, depois de provar o destino,
o responsável, o modelo e o código instalado.

A rotina recusa as duas oficiais conhecidas, o próprio modelo, arquivos
registrados, documento vinculado diferente, modo salarial legado, abas
ausentes, fórmulas incompatíveis e grades financeiras acima de 5.000 linhas.
Os flags do contexto **não são autenticação nem prova de origem**. Não expor
esta função a um endpoint que aceite esses flags do navegador. O vínculo
com uma cópia recém-criada ainda precisa ser implementado pelo consumidor.

A prévia retorna apenas identificação da operação/destino, quantidade de
passos que alterariam estado e impressão digital. Valores, notas e textos
financeiros não vão ao retorno ou ao diário. O diário contém hashes, IDs e
versão de contrato; fica nas propriedades do documento, não nos relatórios.

| Inicializa | Preserva |
|---|---|
| EXTRATO A2:C, SALÁRIOS A2:L e DADOS_SALARIOS A2:J, até o fim físico, incluindo notas | Cabeçalhos, fórmulas auxiliares, proteção, formato e validação |
| Quatro entradas de cada missão: AW:AZ, BC:BF, BI:BL e BO:BR, linhas 15–87, incluindo notas | A quinta coluna de cada grupo, com XP calculado |
| N2, O86, BI11 e BO11 de seus respectivos domínios | Notas explicativas dos campos individuais |
| L2 = `{"versao":1,"graus":[]}` no modo salário por fórmula | Regras atuais de salário/campanha; nenhuma agenda ou data antiga |
| CONFIGURAÇÃO O39 e CARTEIRA AT3 desmarcados | O38 e AH3 continuam fórmulas de apresentação da emissão |
| Quatro propriedades salariais do documento e `salario_edicao` do script | Propriedades de editor, recuperação e paleta, que exigem outro domínio |

`O86` pode conter uma fórmula pessoal de lançamento; a prévia inclui sua
remoção. Fórmulas em outras entradas a limpar causam recusa, em vez de apagar
um modelo desconhecido. As sete faixas protegidas precisam corresponder ao
contrato de fórmulas do produtor. Só é normalizada a retirada das aspas
opcionais em `'DADOS_SALARIOS'!`, observada no salvamento do Google.

O estado de L2 não cria início de ciclo, emissão, histórico de Grau ou vínculo
de agenda. O leitor real `salarioEstado_` o aceita, e as fórmulas atuais
condicionam início/períodos vencidos a N2 numérica. Essa é evidência estática e
local, complementada pelo ensaio financeiro nativo anterior descrito abaixo.
Esse ensaio não valida as novas rotinas nem o executor extraído nesta rodada. Não usar esse
estado no modo legado. Dinheiro inicial permitido pela mesa será uma
operação explícita posterior; não converter o saldo herdado em crédito novo.

Nível/XP não são parâmetros do domínio financeiro. AH11, AN11 e a regra
E46:G46 são preservados e conferidos nessa fase. O domínio seguinte trata
nível/base sem gravar em XP calculado.

## Nível inicial e base de XP

`progressao.gs` fornece `r53NovaFichaProgressaoPrevia` e
`r53NovaFichaProgressaoAplicar`, usando o executor interno de `financeiro.gs`.
Exige diário financeiro concluído **da mesma operação/cópia/modelo** e missões
vazias, com suas 292 fórmulas de total reconhecidas e recalculadas. Isso prova
uma fase registrada, não revalida todo o financeiro como certificado geral.

A rotina lê o nível resolvido da regra `CONFIGURAÇÃO!E46:G46` (nível inteiro
entre 1 e 30) e a curva atual `DADOS!AQ5:AR33`. Escreve apenas:

- `FICHA!AH11`: nível inicial resolvido da mesa;
- `DADOS!CZ54`: XP acumulado necessário para começar nesse nível; nível 1 usa 0.

A curva pode ser customizada pela mesa; não é substituída por uma tabela fixa.
A rotina recusa curva incompleta, decrescente, não numérica ou com fórmula
inesperada. As fórmulas `DADOS!CZ47` e `FICHA!AN11` são preservadas. O novo
campo de base é obrigatório: API não dispara o onEdit que ajusta XP numa
edição manual do nível. Não deduzir a base pelo XP total herdado.

O Google devolveu G46 com ponto e vírgula na leitura nativa. É aceita somente
a troca dos separadores da fórmula conhecida; mudar referências, operações
ou o limite de nível continua causando recusa. O mesmo vale para os totais
de missão. Não distribui atributos, concede marcos, escolhe Caminho/Origem,
limpa treinamentos ou inicializa recursos.

## Textos pessoais

`identidade.gs` fornece `r53NovaFichaIdentidadePrevia` e
`r53NovaFichaIdentidadeAplicar`, também com diário/retomada próprios. Trata
somente os campos abaixo e suas notas de entrada:

| Aba | Entradas |
|---|---|
| CARTEIRA | O9: nome volta ao texto de preenchimento; AK22: registrado por |
| FICHA PESSOAL | AI11 idade; AO11 altura; Q15 olhos; Y15 cabelo; AG15 pele; AO15 gênero |
| FICHA PESSOAL | Q19 aparência; AI19 cicatrizes; Q23 traço; Q27 história; Q35 laços/anotações; D31 personalidade |

Os 14 rótulos precisam corresponder ao fonte. Notas de fábrica dessas entradas
são vazias; instruções nos cabeçalhos são preservadas. Os espelhos de nome/foto
em `FICHA!AB2`, `FICHA PESSOAL!Q11/D10` continuam fórmulas. `CARTEIRA!Z22`
(servidor usado), Grau e escolhas de jogo não são modificados por este domínio.

Só aceita C8 vazia ou com o marcador de foto do modelo. Imagem em célula,
fórmula de imagem ou outro conteúdo causa recusa. Isso **não inspeciona nem
remove imagens sobrepostas**: fotos/arte continuam pendentes no retorno.
Textos e notas pessoais não são colocados no diário ou na resposta.

## Escolhas, recursos e condições

`pessoal.gs` e `contrato_pessoal.gs` acrescentam três perfis independentes:

| Perfil / funções Previa e Aplicar | Cobertura |
|---|---|
| `r53NovaFichaEscolhas*` | 19 escolhas básicas da FICHA: Caminho, Trilha, Origem, cinco atributos base, cinco distribuições de Corpo, três contadores de marcos e três seletores pessoais de atributo |
| `r53NovaFichaRecursos*` | 20 entradas: Vida/Energia/Integridade atuais, seus bônus/temporários/caixas ± e oito bônus pessoais de estatísticas |
| `r53NovaFichaCondicoes*` | Nove entradas: descanso/último descanso, três Sequelas, Sequelas extras, Exaustão, resistências e imunidades |

Escolhas voltam aos valores de fábrica da ficha, incluindo os convites de
Caminho/Trilha e a Origem Latente. Atributos/distribuições/marcos ficam em 0;
isso **não distribui os pontos nem conclui a criação**. Não escolhe Grau,
treinos, capacidades da Origem, técnica, Famílias ou cartões.

Recursos atuais voltam a `=J26`, `=J30` e `=J34`, o comportamento do modelo.
Assim acompanham seus máximos enquanto o personagem é montado; não recebem
um número herdado ou deduzido do resultado antigo. Os máximos e demais
fórmulas protegidas não são sobrescritos. Fórmula pessoal desconhecida num
campo atual é recusada; número de recurso gasto pode ser inicializado.

As notas das 48 entradas voltam às notas de fábrica. Isso remove texto
pessoal sem apagar a instrução de Sequelas extras. Notas dos cabeçalhos,
formatos, validações, regras e catálogos ficam fora das escritas.

Contrato gerado apenas dos campos listados da fonte pública Ficha.gs:

```sh
node r53/inicializacao/gerar_contrato_pessoal.js --conferir
```

`--conferir` não regenera nada; divergência exige revisão do produtor antes
de usar o gerador sem a opção. Não identifica código instalado no Google.
Os hashes aceitam só as variantes conhecidas dos separadores e das aspas
opcionais em FICHA/DADOS_PROGRESSAO, preservando textos entre aspas duplas.
Mudanças na conta/referência continuam recusadas. A conferência de rótulos e
fórmulas desses perfis usa duas leituras em bloco de `FICHA!D10:AT70`;
não guarda as leituras entre chamadas nem elimina a releitura antes das escritas.

O primeiro desenho juntava 29 entradas de cena e ultrapassava o tamanho por
valor do diário. Recursos e condições foram separados; o executor agora
recusa qualquer diário acima de **9.000 bytes UTF-8 antes de gravar**. Não
alterar a expectativa para permitir um diário que só cabe na VM. O formato e
a assinatura financeira v1 continuam iguais.

502 cenários de inicialização passaram (101 financeiro, 80 nível/base, 78
textos, 243 escolhas/recursos/condições). Leitura nativa das duas oficiais:
112 conferências por documento, zero divergências após tratar as variantes
Google. Projeção dos efeitos em cópia privada do Ciclo: 48 campos/notas e
11.634 comparações delimitadas preservadas sem diferença. Recursos ligados
aos máximos, nota de Sequelas extras restaurada; cópia na lixeira. Não é
execução nativa dos diários. [Registro](ESCOLHAS-RECURSOS-2026-10-27.md).

## Ordem e limite entre domínios

São perfis fixos do produtor, nunca um plano arbitrário enviado pelo navegador.
O diário financeiro v1 e sua assinatura foram preservados na extração do
executor; uma regressão usa a assinatura capturada do código `4f3555d`.
Cada perfil mantém sua própria prévia, assinatura e diário. Todos retornam
`criacaoDisponivel=false`, mesmo quando `concluido=true` no domínio.

No ensaio do protocolo, concluir financeiro antes de nível/XP; a fase textual
é independente. **Não reiniciar a sequência do primeiro domínio a cada
retentativa.** O financeiro protege o nível que existia na sua prévia; depois
de inicializar o nível, aquela conferência financeira antiga deve recusar.
A retomada atual é por domínio, não um orquestrador global pronto para uso.

Ainda falta uma conferência final combinada: fases concluídas não garantem
que outro domínio permaneceu intacto após uma edição. A cópia deve ficar
isolada do jogador até esse fechamento. A abertura pode recriar
`salario_proximo`; isso precisa de tratamento explícito na ativação e na
conferência final, sem apagar diários para aceitar um estado diferente. Não apagar diários nem fabricar um
diário financeiro concluído para testar o domínio seguinte.

## Falhas e retomada

Cada perfil aplica no máximo quatro passos de escrita por chamada e usa um orçamento
local de 210 s antes de iniciar outro passo ou a conferência final. Se o
orçamento acabar, retorna `concluido=false, retomar=true`; isso não libera
cadastro. A mesma operação continua em uma chamada posterior. O tempo gasto
pelo próprio serviço Google não é cancelável e esse orçamento **não garante**
latência máxima ou ausência de timeout externo.

A aplicação nova reaproveita a leitura integral que acabou de comparar com a
prévia. Cada passo alterado continua relido antes/depois, e uma conclusão com
escritas exige conferência integral. Na retomada sem escrita, todos os passos
já foram conferidos na entrada; a rotina não lê o livro inteiro uma segunda
vez sem necessidade. Essas mudanças tratam um timeout nativo de seis minutos
observado na primeira implementação, não reduzem os critérios de conclusão.

Cada limpeza de conteúdo, limpeza de notas e exclusão de propriedade tem
seu próprio estado anterior/posterior. Isso permite retomar após uma queda
entre chamadas do Google, inclusive entre duas propriedades. Não existe
transação que reúna toda a planilha.

Antes de qualquer retomada, todos os passos precisam estar no estado
anterior ou posterior conhecido; fórmulas/estrutura protegidas também são
conferidas. Cada passo é relido imediatamente antes/depois da escrita. Uma
edição desconhecida interrompe a operação. A cópia incompleta não pode ser
cadastrada. O lock coordena execuções de script; **não impede edições humanas
nem constitui um compare-and-swap atômico do Sheets**. É por isso que o alvo
precisa ser uma cópia nova, isolada do jogador durante a inicialização. Se
for necessário descartar, não oferecer o arquivo incompleto como ficha pronta.

Repetir uma operação concluída, sem mudança, só verifica e retorna, sem
reescrever. Se a cópia já foi usada, a mesma chamada recusa em vez de limpar
novamente. O diário nunca é apagado automaticamente para iniciar outra
limpeza. Não há opção “forçar” ou rollback automático de dados pessoais.

## Validação disponível

```sh
node r53/testes/inicializacao_financeiro.js
node r53/testes/inicializacao_progressao.js
node r53/testes/inicializacao_identidade.js
node r53/testes/inicializacao_pessoal.js
node r53/testes/inicializacao_formacao.js
```

782 cenários offline: 101 financeiros, 82 de nível/base, 78 de textos,
243 de escolhas/recursos/condições e 278 de formação/técnica/Famílias. Incluem
falha antes/depois das escritas, retomada, concorrência, fórmulas desconhecidas,
notas e compatibilidade dos contratos anteriores. A VM não executa fórmulas
nem mede latência Google. O smoke inclui os cinco arquivos de testes.
Resultados anteriores e limites nativos ficam nos relatórios datados; o registro
atual está em [TECNICA-FAMILIAS-2026-10-28.md](TECNICA-FAMILIAS-2026-10-28.md).
Regressão independente de XP: `node r53/testes/xp_nivel.js`, 20.643
verificações/9.900 combinações sem a exportação nativa opcional.

Conferência de leitura nativa em 27/10/2026: metadados e onze faixas pontuais
nas duas oficiais; grades financeiras de 1.000 linhas e âncoras esperadas
presentes. A leitura não aplicou o inicializador nem alterou as fontes.
Ensaio inicial em cópia descartável do Ciclo: prévia concluída em 115,013 s;
a aplicação atingiu seis minutos durante a conferência final, sem retornar
sucesso. Leitura externa dos sete intervalos completos confirmou zero
entradas/notas restantes e saldo/períodos/crédito pendente zero. Isso não
substitui concluir o diário. A retomada concluiu em 236,503 s. Em outra cópia, a versão com orçamento
concluiu em 283,416 s; repetição em 150,489 s, com estado comparado igual.
As duas cópias foram enviadas à lixeira. Essa prova se refere ao código
financeiro anterior `4f3555d`, antes da extração do executor e da main atual.
O custo ainda exige otimização e
integração própria antes de uso pelo jogador; consultar [o registro nativo](NATIVO-2026-10-27.md) antes de continuar.

Na continuação de 27/10, uma nova cópia descartável da Era recebeu uma
**projeção dos efeitos via Sheets API**, sem executar os diários Apps Script.
14 textos/notas e nível/base aprovados; 8.998 comparações de campos preservados
sem diferença. XP 3.700 → 3.750 com missão de 50 → 3.700 ao retirá-la.
Isso valida o cálculo nativo e os alvos de escrita; não prova a execução dos
novos perfis, retomada nativa, OAuth próprio ou automações. Cópia na lixeira.
Detalhes em [NIVEL-TEXTOS-2026-10-27.md](NIVEL-TEXTOS-2026-10-27.md).

## O que falta antes de liberar criação

- Inicialização pessoal completa: fotos/arte, campos restantes da CARTEIRA
  (incluindo nome declarado da técnica), inventário/equipamento, entidades,
  cartões e MONTAGENS. Os domínios já tratados têm protótipos, sem aceite
  nativo completo dos executores. Famílias ainda exigem sincronização com
  cartões, amparo e recuperações; não basta restaurar seus menus.
- Propriedades de recuperação/editor que podem repor dados antigos, incluindo
  caches novos `r53_versoes` e `r53_marcas_custom`, além de Classe/amparo/recuperações.
- Orquestração entre fases, conferência combinada, limites de custo e prova
  de preservação do financeiro depois de concluir os outros domínios.
- Prova do código instalado, origem da cópia e novo responsável; os flags
  atuais são pré-condições do protótipo, não um certificado para o bot.
- Integração permitida com `drive.file`, sem inventar execução remota de
  Apps Script nem ampliar escopos.
- Ensaios nativos de aplicação/falha/retomada em Era, Ciclo e modelo sintético,
  fórmulas/resultados/proteções preservados, duas identidades e automações.

Não reconstruir a ficha, não instalar este protótipo nas oficiais, não mudar
seus escopos nem adicionar acionadores para contornar esses itens. Próxima
implementação integrada: **GPT-6 Astra / Alto**; revisão focal: esforço Médio.
A indicação não altera a configuração do modelo automaticamente.

## Grau, Origem e treinos

`formacao.gs` usa `contrato_formacao.gs`, extraído de Ficha/Pessoal e do módulo
salarial. Confira sem regenerar com
`node r53/inicializacao/gerar_contrato_formacao.js --conferir`.

| Perfil | Células | Inicialização |
|---|---:|---|
| Grau/Origem | 10 | Grau 4 de fábrica, menus/histórico vazios e fórmulas originais de descrição, Ofício e talento |
| Perícias | 99 | Treinos/especialidades desmarcados e bônus pessoais zerados |
| Ofícios/TR | 94 | Treinos/bônus, atributos padrão e fórmulas dos atributos de Ofícios custom |
| Armas | 65 | Grupos e armas individuais desmarcados |

Não infere Grau pelo nível nem concede treinos de Caminho. Não há seletor de
Grau inicial de campanha reconhecido neste contrato; uma opção futura exige
semântica explícita. Catálogos custom permanecem: os bônus pessoais novos estão
em AL, enquanto campos antigos da B47 são espelhos derivados ou mesclas.
Notas de fábrica voltam, inclusive a instrução extensa da Origem.

As matrizes de conteúdo e notas seguem o mesmo diário/trava, quatro escritas
por chamada e limite de 9.000 bytes. Fórmula Google só é reconhecida se constar
na lista exata do campo. Se uma escrita de matriz deixar estado intermediário,
a rotina recusa continuar: não sobrescreve nem faz rollback automático.
Relatório e provas: [FORMACAO-2026-10-27.md](FORMACAO-2026-10-27.md).

## Técnica e Famílias

Dois perfis em `formacao.gs`, com funções `r53NovaFichaTecnicaPrevia/Aplicar`
e `r53NovaFichaFamiliasPrevia/Aplicar`, usam o mesmo executor e seus limites.
O gerador inclui `R53Cartoes1.gs`, responsável pelo cabeçalho final da aba.

- Técnica: limpa J12, J16, D18, J18, P18, D22, D26, L26, L29, D33 e P33 da
  FICHA AMALDIÇOADA. Nome, atributo, conjuração e CD derivados são protegidos;
  o nome declarado na CARTEIRA não pertence a este domínio e segue pendente.
- Famílias: nove estados do livro voltam a Neutra. O41:O50 recupera as fórmulas
  originais: custom válida fica Neutra; sem definição válida fica vazia.
  As definições da mesa, nomes e fórmulas derivadas são preservadas.

Não concede Famílias, aprova custom ou limpa cartões/amparo. Fórmula pessoal
não reconhecida provoca recusa antes de escrever. As variantes de aspas e
separadores aceitam somente a fórmula inteira conhecida. Na projeção pela
Sheets API em locale pt_BR foi necessário usar ponto e vírgula; isso não prova
qual comportamento terá `setValues` no Apps Script, cujo ensaio segue pendente.
O teste nativo delimitado e suas ressalvas estão no relatório de 28/10.
