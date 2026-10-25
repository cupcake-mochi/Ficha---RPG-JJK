# Fila revisada em 23/10/2026

Base: fa54ab633313b2f230c4c669041b6d552a66c9c6, ramo remoto
`codex/otimizacao-android-r53`. O usuário pediu continuar até concluir a fila.
Correções locais concluídas e validadas; aplicação operacional ainda parcial.
Não houve merge em main, alteração de acesso, bot ou acionadores.

## Estado por problema

| Item | Resultado | Falta para encerrar |
|---|---|---|
| Abertura Android da original | Causa específica não isolada; conteúdo da cópia funcional igual na comparação anterior | Confirmar qual cópia foi testada, configurar automações próprias e retestar Android antes da adoção definitiva |
| Sementes Sem Técnica | Extrator corrigido, catálogo com quatro opções, geração/lista/dropdown corrigidos; quatro rotas aprovadas na QA Google | Publicar delta na ficha escolhida junto com recuperação de fórmulas e validações do Apps Script, após captura atual e ensaio do código |
| Cores lentas | Fonte já relia progresso sob lock; acrescentada saída imediata quando outro callback já terminou; módulo leve regenerado | Instalar atualização do código e medir no Android. Nenhuma alegação de tempo real ou solução definitiva da lentidão |
| Smoke | Corrigido contrato dos nove arquivos, incluindo PaletaAndroid.gs; smoke completo aprovado | Nada local; execução remota do CI não consultada |
| Barras zero no pacote | GS regenerados a partir da fonte com a guarda de zero; delta integral conferido | Nenhuma reaplicação nas barras nativas: já estavam corrigidas. Pacote integral novo não instalado |

## Escopo das correções

O livro põe Domínio Simples, Energia Reversa, Pétala e Aptidão Própria no mesmo
nível de título de Sementes. O extrator procurava somente filhos e retornava
lista vazia. Agora lê o trecho delimitado, aceita a estrutura atual e a anterior,
e recusa quantidade/nomes duplicados incompatíveis com a declaração do livro.
Não altera requisitos, custos, capacidades ou benefícios das opções.

Na planilha atual as quatro strings já existiam em DADOS_AM!CO2:CO5,
mas CS2:CS4 consultavam CO1:CO2 e o dropdown J16 terminava em CS4.
A fonte antiga ainda tinha catálogo vazio. A correção harmoniza as duas pontas.
CS2:CS5 passa a consultar CO2:CO5 e J16 inclui as quatro linhas, mantendo
validação estrita. Técnica Marcial continua usando os três equipamentos.

Na paleta, a nova guarda evita buscar a célula e entrar na convergência quando
outro callback concluiu entre a consulta inicial de pendência e a obtenção do
lock. O teste simula progresso, término concorrente, lock ocupado e ausência de
pendência tanto na fonte integral quanto no módulo leve. Não estima tempo real.

## Geração e preservação

Geração atual: `7477944d1a09c3ed`, 25 abas-fonte, 249 contextos, nove módulos.
70.090 moldes de fórmula; maior fórmula 17.729 caracteres; nenhum truncamento
ou geração misturada detectado. Os moldes não são o total expandido da planilha.

`node r53/testes/delta_fila.js` compara todas as abas geradas com fa54ab6,
indexando células por coordenada e ignorando somente tags de geração.
Exige exatamente 12 diferenças: três barras, quatro strings, quatro fórmulas
de menu e um intervalo de validação. Demais campos iguais, inclusive ANALISE,
capacidades, notas, formatos e estrutura representados na geração.
Isto não equivale a comparação visual nem à migração de dados da ficha jogada.

`python ficha-v01/monta.py` produziu o XLSX de cálculo apenas localmente.
Esse artefato foi movido para a saída privada; o XLSX histórico versionado foi
preservado. Não importar Office no Google. O pacote integral é para construção
de descartáveis e futuras entregas planejadas; NÃO executar construir/continuar
em planilha preenchida e NÃO substituir automaticamente o carregador instalado.

## Validações executadas

- `ficha-v01/extrair_tecnica.py --confere`: catálogo igual ao livro.
- `python -m unittest discover -s r53/testes -p 'test_*.py'`: 27 testes aprovados.
- `nuvem-b47/conferir.py --smoke`: aprovado, incluindo pacote, salários,
  abertura/notas, sintaxe e conferências de catálogo/progressão/Kaori.
- `r53/testes/pacote_runtime.js`: nove módulos, 25 abas, 249 contextos;
  igualdade de estado, autonomia e recusa de corrupção aprovadas.
- `r53/testes/delta_fila.js`: 12 mudanças previstas, demais campos iguais.
- `r53/testes/paleta_leve.js`: seis abas, aparência/arte/fila iguais e zero
  carregamentos do catálogo pesado no caminho leve.
- `r53/testes/paleta_concorrente.js`: oito cenários aprovados.
- `regressao-paleta.js`: todos aprovados, incluindo verificações nas 122 variantes.
- `r53/testes/cartoes_diretos_runtime.js`: 550 verificações aprovadas.
- `r53/diagnostico-android/testes_constantes.js`: 603 conversões, sete
  restaurações e idempotência aprovadas.
- QA nativa de Sementes: quatro rotas, resultados esperados e dropdown estrito
  aprovado. Fórmula de rota A2 restaurada e relida igual. Evidência sanitizada
  em `SEMENTES-QA-2026-10-23.json`.

A primeira tentativa da QA usou separadores de argumentos incompatíveis com
pt_BR e retornou erros de parsing. Foi corrigida para ponto e vírgula; todas as
rotas foram repetidas com sucesso. Não ocultar esse incidente nem reutilizar
os primeiros resultados como aprovação.

## Aplicação nativa pendente e sequência de retomada

Drive/Sheets funcionam; continuam indisponíveis ferramentas para ler/escrever
Apps Script, propriedades e acionadores. A nova cópia de QA é
`1qE13EJn5Iid_El3u3xuxtOx2sZnNpei4cG0RR9c4Aq8`. Não é a ficha escolhida para uso.
Não substituir essa escolha pela QA automaticamente.

Original e cópia candidata 1427... não foram escritas. Metadados finais mantêm
respectivamente `2026-10-23T16:38:21.310Z` e `2026-10-23T17:01:01.739Z`.
São recibos de modificação, não medição de memória nem prova de causalidade.

1. Confirmar o ID da cópia que abriu no telefone (há duas de mesmo título).
2. Com acesso ao editor/API Apps Script, capturar e reler o código instalado,
   propriedades e acionadores visíveis. Usar o diagnóstico já preparado;
   nenhum dado copiado de agenda prova que os acionadores existem na cópia.
3. Preparar um delta estrito sobre esse código atual e ensaiar em descartável.
   Incluir recuperação das quatro opções/fórmulas e da validação J16: alterar
   somente células sem atualizar o restaurador antigo pode desfazer o conserto.
   Atualizar a paleta leve sem duplicar funções/módulos de salários.
4. Fazer snapshot novo da ficha escolhida, comparar pré-condições e aplicar
   somente as diferenças ensaiadas, com rollback condicionado ao estado aplicado.
   Não reutilizar IDs/lotes da QA como lote da ficha escolhida.
5. Pelo proprietário, configurar as rotinas próprias da cópia conforme
   CONTINUIDADE-DOCUMENTO-ANDROID.md; não reinstalar salários inicializados,
   não apagar históricos e não reemitir créditos. Retestar Android depois.
6. Medir troca de cores e observar logs após resolver a abertura. Não repetir
   o teste já falho do link direto da original à CARTEIRA.

Não há evidência para cortar mecânicas. A recomendação continua sendo adotar
a cópia funcional quando automações e aceite Android estiverem conferidos.
Recomendação de modelo: GPT-6.1 Sol, High para aplicação integrada; Medium
para a conferência focal posterior. Configuração do modelo não foi alterada.

Logs/snapshots privados: `nuvem-b47/saidas/*-fila*.log`, `sementes-antes.json`,
`sementes-qa.json`. Não versionar dados completos de jogadores nem credenciais.
