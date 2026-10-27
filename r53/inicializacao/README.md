# Inicializar uma cópia nova

Protótipo do produtor para a etapa 7 da Carteira viva. **Não instalado nas oficiais, não
incluído no pacote e sem integração de escrita com o bot.** A criação pelo
bot permanece bloqueada. Não executar em ficha oficial ou de jogador.

O modelo do servidor é a ficha do sistema com configurações extras da mesa.
A cópia deve conservar essas regras e catálogos; não deve herdar identidade,
progressão, inventário, missões, cartões ou dinheiro de outro personagem.
A implementação abaixo cobre **somente o domínio financeiro**. Não oferece
uma ficha inteira pronta para cadastro.

## O que está implementado

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
local; ainda falta executar e conferir o resultado no Google. Não usar esse
estado no modo legado. Dinheiro inicial permitido pela mesa será uma
operação explícita posterior; não converter o saldo herdado em crédito novo.

Nível/XP não são parâmetros deste módulo. AH11, AN11 e a regra E46:G46 são
preservados e conferidos. A inicialização geral ainda deve decidir o nível
pessoal a partir da regra da mesa, sem gravar em XP calculado.

## Falhas e retomada

Cada chamada aplica no máximo quatro passos de escrita e usa um orçamento
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
```

99 cenários offline, incluindo todas as fronteiras de escrita antes/depois,
queda entre conteúdo/notas, propriedades parcialmente removidas, repetição,
edição concorrente, linhas físicas tardias, prévia envelhecida, alvo inválido,
modo legado, fórmula desconhecida, preservação de regras e ausência de texto
financeiro no diário. VM com serviços simulados; não executa fórmulas e não
mede latência do Google. O smoke de nuvem inclui este teste.

Conferência de leitura nativa em 27/10/2026: metadados e onze faixas pontuais
nas duas oficiais; grades financeiras de 1.000 linhas e âncoras esperadas
presentes. A leitura não aplicou o inicializador nem alterou as fontes.
Ensaio inicial em cópia descartável do Ciclo: prévia concluída em 115,013 s;
a aplicação atingiu seis minutos durante a conferência final, sem retornar
sucesso. Leitura externa dos sete intervalos completos confirmou zero
entradas/notas restantes e saldo/períodos/crédito pendente zero. Isso não
substitui concluir o diário. A retomada e a versão com orçamento são testadas
separadamente; consultar o registro nativo nesta pasta antes de continuar.

## O que falta antes de liberar criação

- Inventário e inicialização pessoal completos: identidade/imagens, escolhas,
  progressão, recursos, inventário, entidades, cartões e MONTAGENS.
- Propriedades de recuperação/editor que podem repor dados antigos.
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
