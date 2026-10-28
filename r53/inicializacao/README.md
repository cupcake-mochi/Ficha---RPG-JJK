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
cabeçalho da técnica, 19 estados de Famílias, 129 campos de inventário/equipamento
e quatro notas vivas, três campos restantes da CARTEIRA, memórias conhecidas,
as versões guardadas dos 249 cartões em MONTAGENS e seus campos visíveis,
com validações das funções, além de 1.165 entradas das 12 entidades e do conjunto. **Não oferecem uma ficha inteira
pronta para cadastro.** Base incorporada: main
`ef361ccdf7a0210781176e3c42d318cde147553d`, merge `a72adc0` (PRs 41–43).
Inclui XP manual e marcas de missões congeladas. A instalação/backup 13 das
oficiais foi feita por outro trabalho; não reaplicar nem reabrir a otimização.

## Sequência dos domínios — ainda sem liberação

`sequencia.gs` coordena 599 perfis de escrita e duas inspeções de imagens,
com até 32 recuperações adicionais capturadas no início. Uma prévia/aplicação
por chamada, assinatura durável e cursor; trava única durante filho e avanço.
Não reinicia no financeiro depois de a progressão mudar o nível. Não adota
fases avulsas ou apaga diário para começar outra operação. Não recebe plano
do navegador. Continua fora do pacote/bot e mantém criação bloqueada mesmo
ao percorrer todas as fases; conferência conjunta/automação/prova nativa faltam.
Leia [SEQUENCIA-2026-10-28.md](SEQUENCIA-2026-10-28.md) para a ordem e os limites.

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
node r53/testes/inicializacao_memorias.js
node r53/testes/inicializacao_montagens.js
node r53/testes/inicializacao_cartoes.js
node r53/testes/inicializacao_recibos.js
node r53/testes/inicializacao_entidades.js
node r53/testes/inicializacao_arte.js
node r53/testes/inicializacao_inventario_imagens.js
node r53/testes/inicializacao_sequencia.js
```

Coleção atual: **2.893 cenários**, zero falhas, incluindo 79 de imagens e 67 da
sequência. CI completo [40716269167](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40716269167)
aprovado no código `408a31abbdb8824bbe39f2e2997e80e30c65914e`, 28/10 às
12:32:28 Brasília: 2.893 cenários/zero falhas. Pacote nove arquivos, sintaxe
277 Python/247 JS-GS e demais regressões passaram. Duplicado 40716253746
cancelado; fechamento só documental [skip ci], sem nova suíte/publicação.

Coleção anterior às imagens/sequência: 2.747 cenários offline (101 financeiros, 82 de nível/base, 78 de
textos, 243 pessoais, 441 de formação/inventário/CARTEIRA, 155 de memórias, 370 de MONTAGENS, 791 de cartões visíveis, 44 de recibos/quota, 305 de entidades e 137 de fotos). Incluem
falha antes/depois das escritas, retomada, concorrência, fórmulas desconhecidas,
notas e compatibilidade dos contratos anteriores. A VM não executa fórmulas
nem mede latência Google. O smoke agora inclui treze arquivos: mais 79 cenários de imagens e a bateria da sequência. Consulte o relatório mais recente para o CI completo.
CI das fotos `350c56d` aprovado: [40706336130](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40706336130), 2.747 cenários, em 28/10 às 11:32:49 Brasília. Pacote nove arquivos/sintaxe 277 Python/242 JS-GS e demais regressões passaram; duplicado 40706329406 cancelado.
CI das entidades `baf652d` aprovado: [40701063975](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40701063975), 2.610 cenários, em 28/10 às 10:58:19 Brasília. Pacote nove arquivos/sintaxe 277 Python/238 JS-GS; demais regressões passaram. Duplicado 40701053252 cancelado.
CI dos recibos `af8e83f` aprovado: [40697164990](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40697164990), 2.305 cenários, em 28/10 às 10:34:44 Brasília; pacote nove arquivos/sintaxe 277 Python/234 JS-GS. Duplicado 40697154581 cancelado.
CI anterior a recibos `216e44c` aprovado: [40694498546](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40694498546), 2.261 cenários, em 28/10 às 10:16:56 Brasília.
CI anterior aos cartões visíveis, `5749b3a`, aprovado: [40690086385](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40690086385), 1.470 cenários, em 28/10 às 09:45:06 Brasília.
CI anterior a MONTAGENS, `8bb9335`, aprovado: [CI 40686604745](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40686604745), com 1.100 cenários.
CI anterior ao bloco CARTEIRA/memórias, `86410be`, aprovado: [40683614201](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40683614201), com 921 cenários.
CI anterior à extensão de inventário, `763a78b`, aprovado: [40681468287](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40681468287).
Resultados anteriores e limites nativos ficam nos relatórios datados; o registro
atual está em [CARTOES-VISIVEIS-2026-10-28.md](CARTOES-VISIVEIS-2026-10-28.md).
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

- Inicialização pessoal completa: imagens fora das caixas de foto, arte e
  protocolo global de diários e aplicação conjunta. Cartões visíveis/validações,
  MONTAGENS e os outros domínios já tratados têm protótipos, sem aceite
  nativo completo dos executores. Famílias ainda exigem sincronização com
  cartões, amparo e recuperações; não basta restaurar seus menus.
- Integrar e validar nativamente o protocolo de memórias abaixo; tratar sua
  ordem com MONTAGENS e a regeneração de Classe/amparo após a limpeza.
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

`formacao.gs` usa `contrato_formacao.gs`, extraído de Ficha/Pessoal, do módulo
salarial e do overlay R53Cartoes1. Confira sem regenerar com
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
  o nome declarado na CARTEIRA pertence ao perfil `carteira`, separado.
- Famílias: nove estados do livro voltam a Neutra. O41:O50 recupera as fórmulas
  originais: custom válida fica Neutra; sem definição válida fica vazia.
  As definições da mesa, nomes e fórmulas derivadas são preservadas.

Não concede Famílias, aprova custom ou limpa cartões/amparo. Fórmula pessoal
não reconhecida provoca recusa antes de escrever. As variantes de aspas e
separadores aceitam somente a fórmula inteira conhecida. Na projeção pela
Sheets API em locale pt_BR foi necessário usar ponto e vírgula; isso não prova
qual comportamento terá `setValues` no Apps Script, cujo ensaio segue pendente.
O teste nativo delimitado e suas ressalvas estão no relatório de 28/10.

## Inventário e equipamento

`r53NovaFichaEquipadosPrevia/Aplicar`, `r53NovaFichaEquipaveisPrevia/Aplicar`
e `r53NovaFichaItensPrevia/Aplicar` acrescentam 129 campos ao mesmo executor.
Soco, mão livre e Traje 1 são defaults do modelo; bônus de carga e situação do
Traje reiniciados. Nomes/quantidades do estoque são limpos, fórmulas originais
restauradas inclusive nas linhas livres e Volumes sobrescritos. Catálogos da
mesa, dinheiro, treinos, mesclas, formatos e validações ficam preservados.

Quatro notas vivas antigas são limpas sem escrever suas fórmulas protegidas.
A regeneração delas depende das automações finais; não liberar criação com
avisos vazios como se isso fosse aprovação. Contratos anteriores iguais.
Volume pt_BR aceita somente a variante exata do decimal 0,1. Valores,
referências ou contas diferentes continuam recusados. Relatório com alvos,
testes e projeção nativa: [INVENTARIO-2026-10-28.md](INVENTARIO-2026-10-28.md).

## CARTEIRA e memórias do editor

`r53NovaFichaCarteiraPrevia/Aplicar` restaura somente O13 (complemento do
nome), O27 (técnica declarada) e O30 (resumo), incluindo notas de fábrica.
Z22, servidor usado, fica preservado. Nome e jogador já pertencem à identidade;
emissão pertence ao financeiro. Foto/arte continuam pendentes. São três âncoras
pessoais, não uma limpeza da aba inteira. Cabeçalhos e espelhos são conferidos.

`memorias.gs` usa `contrato_memorias.gs`, gerado do editor público. A inspeção
`r53NovaFichaMemoriasInspecionar(ss, ctx)` retorna quantidade de memórias,
número de grupos e identificadores das recuperações. Nunca retorna seu conteúdo
nem aprova a criação. Usa `getKeys`, não lê todas as propriedades do documento.

- `r53NovaFichaMemoriasPrevia(ss, ctx, grupo)` e `...Aplicar(ss, ctx, grupo, hash)`:
  grupos fixos 0–10, até 24 chaves cada. Cobrem quatro caches e 249 marcadores
  de Classe. Não recalcular os grupos a partir das chaves que ainda existem:
  a lista fixa permite retomar depois de exclusões parciais.
- `r53NovaFichaRecuperacaoPrevia(ss, ctx, chave)` e
  `...Aplicar(ss, ctx, chave, hash)`: uma recuperação por diário, somente a
  chave exata `r53_recuperacao_` seguida de um timestamp de 13 algarismos,
  formato emitido pelo editor atual. Selecionar a chave retornada pela inspeção.
  Não existe função para apagar uma propriedade arbitrária recebida do navegador.
- Grupos e recuperações usam o mesmo executor: quatro exclusões por chamada,
  orçamento de 210 s, diário com hashes abaixo de 9.000 bytes, trava, prévia,
  releitura, retomada e recusa de alteração concorrente. O executor financeiro
  e as assinaturas anteriores não foram modificados.
- O cache volátil `R53_REF_CACHE_` também é invalidado ao sair da aplicação,
  inclusive em falha. Caso contrário, o mesmo processo poderia reler uma versão
  antiga mesmo depois de excluir `r53_versoes` do documento.

Nenhuma célula, MONTAGENS, configuração, propriedade de script/usuário ou diário
alheio é apagado por esse protocolo. Um nome desconhecido nos namespaces de
Classe/recuperação provoca recusa, sem expor seu nome/valor e sem apagar nada.
Novas recuperações conhecidas aparecem na inspeção seguinte; concluir um grupo
não garante que o conjunto esteja vazio. Inspecionar novamente ao final.

A ordem integrada ainda falta: a cópia deve ficar isolada, as automações não
podem produzir estado novo durante a limpeza e MONTAGENS/cartões precisam ser
reinicializados antes de religar os consumidores. Limpar caches não limpa os
cartões armazenados. Depois, regenerar amparo/notas e conferir o conjunto.
Não apagar os diários para tentar de novo. Ver
[CARTEIRA-MEMORIAS-2026-10-28.md](CARTEIRA-MEMORIAS-2026-10-28.md).

## Versões guardadas dos cartões

`montagens.gs` e `contrato_montagens.gs` cobrem as 48.015 posições das versões
dos 249 cartões. As funções `r53NovaFichaMontagensPrevia` e
`r53NovaFichaMontagensAplicar` recebem o ID conhecido do cartão, além do
contexto confiável; cada cartão tem diário separado. Defaults restaurados,
notas pessoais das entradas removidas, fórmulas/rótulos protegidos. Validações
ou mesclas inesperadas no bloco impedem a execução.

Isso não inicializa os campos visíveis nem suas validações, não limpa as
entidades e não elimina o cache persistente do editor. A sequência completa
precisa terminar o domínio de memórias e conferir tudo sem eventos intermediários.
Não usar a conclusão de um cartão como certificado de criação. Relatório e
limites: [MONTAGENS-2026-10-28.md](MONTAGENS-2026-10-28.md).

## Campos visíveis dos cartões

`cartoes.gs`/`contrato_cartoes.gs` e `validacoes.gs` acrescentam as funções
`r53NovaFichaCartaoPrevia` e `r53NovaFichaCartaoAplicar`, com ID conhecido do
cartão e contexto confiável. Restauram Classe/nome/COMO É e entradas explícitas
do editor, mais notas. Regras das funções são aplicadas antes dos valores;
função bloqueada recebe `—`, respeitando Amparo e Classe de destino. Preservam
fórmulas/rótulos e demais menus. Ver
[CARTOES-VISIVEIS-2026-10-28.md](CARTOES-VISIVEIS-2026-10-28.md).

## Espaço dos registros de retomada

Cartões visíveis e MONTAGENS guardam o diário detalhado enquanto estiverem
incompletos. Após a conferência final, o executor substitui o valor na mesma
chave por um recibo, sem apagar a chave. O recibo guarda hashes da operação,
cópia/modelo/domínio, layout, guardas e de todos os resultados esperados.
Uma repetição só confere: não volta à limpeza nem gera um novo estado anterior.
Diários antigos concluídos desses dois perfis também podem ser compactados,
mas somente depois de conferir seus dados e sua assinatura. Os demais perfis
continuam no formato anterior, inclusive a dependência financeiro → progressão.

Toda gravação de diário confere os 9.000 bytes por valor e a ocupação conjunta
de **450.000 bytes**, contando chaves e valores UTF-8, inclusive propriedades
alheias. Falta de espaço impede criar o diário antes de limpar entradas. Uma
substituição que reduza espaço pode continuar acima da margem para recuperar
um diário existente; isso não libera novas operações. O valor é relido após
a gravação. Nem registros alheios nem recibos são apagados para abrir espaço.

A simulação conjunta ampliada de 572 recibos (cartões, entidades e fotos),
com reserva de 100 KB, fica em 412.570 bytes (pico 412.936). É prova do protocolo offline, não medição no Google nem
reserva real de todos os domínios futuros. O orquestrador ainda terá de limitar
fases simultâneas, considerar recuperações/novos domínios e conferir o conjunto
antes de cadastrar. Lock não bloqueia edição humana nem outros escritores que
não cooperem; a cópia precisa continuar isolada. Hash não é autenticação.

Relatório: [RECIBOS-2026-10-28.md](RECIBOS-2026-10-28.md). Continuam pendentes arte, automações, orquestração, integração drive.file e prova
nativa do conjunto. Os dados das entidades são tratados no domínio abaixo.
Criação permanece bloqueada.


## Dados das entidades

`entidades.gs` e `contrato_entidades.gs` oferecem `r53NovaFichaEntidadePrevia` e
`r53NovaFichaEntidadeAplicar`. Recebem somente o contexto confiável, uma chave
conhecida de grupo e a assinatura da prévia. Chaves: `1_identidade`,
`1_atributos_treinos`, `1_recursos`, `1_familias`, `1_inventario`,
`1_talentos_expansao`, repetidas de 1 a 12, e `conjunto` para Defesa usa.
73 perfis, 1.165 entradas; não aceitam endereços livres.

| Grupo por entidade | Entradas |
|---|---|
| Identificação | 9: nome, tipo, ofício, aquisição/nível obtido, talismã, autonomia, corpo e definição |
| Atributos e treinos | 29: pontos/Buff-Debuff, quatro TRs e escolha treinada, atributo de acerto/Físico usa e sete Perícias |
| Recursos | 8: vida atual, temporária, ±, reserva, alma, Integridade atual, condições e anotações |
| Famílias | 19: nove escolhas e dez fórmulas de estado custom |
| Inventário | 18: três equipados/seus Volumes e seis guardados/seus Volumes |
| Talentos e Expansão | 14: oito talentos, três da Trilha e nome/COMO É/degrau da Expansão |

Vida/Integridade atuais voltam às fórmulas originais de fábrica; máximos,
tetos, resultados e catálogos são preservados. As definições custom da mesa
não são limpas. Cartões R53, MONTAGENS e caches persistentes são outros domínios.
As notas de entrada voltam ao fonte; notas contextuais do tipo precisam ser
regeneradas pela futura fase de automações. Não liberar cadastro entre fases.

Menus conhecidos são conservados, aceitando as versões estrita publicada e
não estrita do fonte. O descritor real entra na assinatura: mudança durante a
retomada recusa. Toda mescla das entradas precisa ter a geometria do contrato.
Fórmulas regionais conhecidas são comparadas por inteiro, inclusive a barra
SPARKLINE com separador de coluna `\` no pt_BR; não normalizar fórmulas arbitrárias.

Foto em célula/fórmula desconhecida provoca recusa, sem apagar. Só aceita
marcador de fábrica ou célula vazia; imagens sobrepostas e arte permanecem
pendentes. A limpeza de arte terá de preceder esses grupos quando houver foto.
Os grupos usam os recibos/quota existentes; 73 recibos reais somam 36.719 bytes,
maior diário pendente 3.165 na VM. Ainda falta o orquestrador final.

Ver [ENTIDADES-2026-10-28.md](ENTIDADES-2026-10-28.md) para validação e limites.


## Fotos nas caixas conhecidas — arte parcial

`arte.gs`/`contrato_arte.gs` acrescentam `r53NovaFichaFotosPrevia/Aplicar`.
Uma fase restaura as 13 caixas de foto e o espelho pessoal, incluindo notas,
sem escrever nas dez decorações do modelo. Usa recibos e os limites anteriores.
A operação especializada `foto` reconhece texto/URL, fórmula IMAGE e CellImage;
figuras desconhecidas recusam, sem mudar os leitores dos demais domínios.
URL de conteúdo/alt text são usados apenas dentro de hashes, sem armazenamento
ou retorno. Identificação temporária instável provoca recusa, sem nova limpeza.

Fotos devem preceder identidade textual e dados das entidades. Presença de
imagem sobreposta ou desenho em qualquer aba impede a aplicação; nada é
removido por heurística. **Imagens em outras células ainda não são auditadas**;
isso aparece como pendência no retorno, que mantém `criacaoDisponivel=false`.
O suporte real a CellImage/estabilidade da URL precisa de ensaio Apps Script
em cópia descartável. Não confundir o perfil com arte integralmente resolvida.

Ver [FOTOS-2026-10-28.md](FOTOS-2026-10-28.md) e as ações obrigatórias de continuidade.
