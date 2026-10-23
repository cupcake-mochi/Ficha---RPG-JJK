# Revisão de dependências e validação — Android / R53

23/10/2026. Base conferida em `origin/main`:
`fbd6d156602958dc0f9da467a4a80100ad7b913f`.

**Revisão técnica concluída no escopo abaixo; otimizações ainda não aplicadas.**
A falha no Android é confirmada pelo usuário. O excesso de estrutura e de
expressões repetidas oferece alvos concretos, mas a causa específica da falha
e a melhora de abertura precisam ser medidas no aparelho afetado.
Não há justificativa demonstrada para cortar mecânicas ou capacidades.

Este fechamento complementa o [plano](../PLANO-OTIMIZACAO-ANDROID.md).
Nenhum arquivo de produção foi alterado. A oficial permaneceu em leitura;
seu `modifiedTime` continuou `2026-10-22T06:31:37.695Z` ao final. As únicas
escritas Google foram na [QA sintética](https://docs.google.com/spreadsheets/d/1mxyAuekbltMsPd1RcvJ7wv6WMollcZFoecWR2mcwBEc/edit),
criada na pasta ChatGPT, sem copiar dados de personagem ou instalar scripts.

## 1. Resultado da validação da fatoração

A proposta substitui duas duplicações de texto em `r53/modelo.py`, somente
em memória. Mantém os sufixos, condições e ordem das mensagens:

`IF(condição, texto & sufixo, texto)` → `texto & IF(condição, sufixo, "")`.

- Apenas a árvore de `efeitos` muda; a lista e a ordem dos campos permanecem.
- As dependências de `efeitos` são idênticas nos modos normal e registro livre.
  Nenhuma coluna auxiliar, função nova, dependência ou ciclo foi acrescentado.
- 89 cenários existentes e 1.024 adicionais determinísticos: **1.113 cenários,
  203.679 campos idênticos**, incluindo entradas e resultados.
- Os quatro estados de sufixos foram exercitados: nenhum, só prazo, só TR e
  ambos. Há 45 cenários com ambos, 31 só com prazo e seis só com TR.
- No **Google Sheets**, os **89 critérios mecânicos originais passaram** e
  as **89 comparações EXACT dos efeitos foram verdadeiras**. Nenhum erro
  efetivo retornou no retângulo de cálculos `CASOS!A1:GD90`.
- A fonte original completa foi enviada diretamente como fórmula nativa.
  Não houve passagem por Workbook/XLSX nem corte para fazer o ensaio passar.
  A compactação dos pedidos foi reexpandida e comparada antes do envio.
- Contrato, migração, tipos e cartões: **20 testes Python aprovados**.
  Runtime de cartões: **550 verificações**. Salários: **112 verificações**.
  As mensagens de falha impressas pelos testes de runtime/salários são os
  cenários negativos previstos; os processos terminaram com código zero.

As referências sintéticas iguais antes/depois produziram fórmulas de efeitos
de 33.653 → 10.797 caracteres na linha 2 e 35.381 → 11.309 na linha 100.
A redução de aproximadamente 68% é do texto dessa fórmula. Não mede RAM,
tempo de abertura ou tempo de edição do Android. Os ensaios nativos aprovam
os casos exercitados; não certificam qualquer corrupção arbitrária de células.

Os 89 cenários cobrem o motor R53, não todas as mecânicas da ficha: a falha
no menu de sementes abaixo é uma lacuna concreta dessa cobertura.

Evidências: [equivalência local](EQUIVALENCIA-LOCAL-2026-10-23.json),
[validação nativa](VALIDACAO-NATIVA-2026-10-23.json) e
[viabilidade inicial](VIABILIDADE-FATORACAO-2026-10-23.json).

## 2. Reconciliação completa das diferenças inventariadas

As 1.163 diferenças de fórmulas da comparação inicial foram classificadas:

| Quantidade | Causa | Consequência |
|---:|---|---|
| 906 | Normalizações de números, matrizes e intervalos unitários | Não são regras diferentes; preservar separadores de linhas/colunas e textos ao comparar |
| 249 | Fórmulas FD cortadas na fonte emitida | Corrigir a integridade da geração; a nativa tem o texto completo |
| 3 | Intervalo de sementes invertido e normalizado pelo Google | A normalização é explicável, mas o intervalo gerado está errado; ver item 3 |
| 3 | Barras com `__xludf.DUMMYFUNCTION` | Função incompatível escondida por IFERROR; ver item 3 |
| 2 | Emissão fixa e total com salários | Extensão legítima documentada; preservar |

Das **1.448 fórmulas adicionais** na nativa:

- **1.158** são iguais à base pré-R53;
- **248** são iguais à base após as 12 inserções de dez linhas da publicação
  R53 em INVOCAÇÕES; todas as transformações foram comparadas;
- **42** são a extensão salarial em CONFIGURAÇÃO.

Isso fecha a origem das 1.406 fórmulas herdadas, não autoriza excluí-las.
Não foram encontradas saídas do conjunto herdado para fórmulas externas ao
próprio conjunto, nem consumidores nas validações/formatações conferidas.
Há dependências internas entre resíduos, que não podem ser confundidas com
uso pela ficha. Scripts remotos, nomes definidos e consumidores externos
ainda precisam de conferência antes de eventual remoção.

Três fórmulas da fonte não aparecem como fórmulas na nativa:

- `FICHA!AH11`: há um número digitado (10), em lugar do valor padrão por
  fórmula. Preservar como entrada; não restaurar indiscriminadamente.
- `FICHA AMALDIÇOADA!M355:N355`: células vazias, onde a fonte prevê os rótulos
  de Cura/PV temporários da Técnica Máxima. Conferir mesclagens e apresentação
  na implementação; não inferir perda de cálculo somente pelo rótulo ausente.

Evidência detalhada: [reconciliação](RECONCILIACAO-2026-10-23.json).

## 3. Defeitos confirmados além do problema de abertura

### Integridade das fórmulas longas

Dez moldes de FD são truncados pelo `Cell.check_string` do openpyxl em
32.767 caracteres; as cópias produzem 249 expressões incompletas no artefato.
O caminho é `ficha-v01/monta.py` → Workbook → `ficha/emitir_gs.py`.
A atribuição de uma fórmula nativa de 33.634 caracteres reproduziu o corte.

A fatoração evita o limite nas amostras, mas a geração também precisa comparar
o texto antes/depois da atribuição e recusar truncamento futuro. Um teste que
apenas descompacta o pacote e confere seu próprio hash não detecta esse defeito.
Não reconstruir/republicar o gerador atual como se ele fosse íntegro.

### Sementes da rota Sem Técnica

O livro vigente, em `referencias-r53/LIVRO-COMPLETO.md`, linhas 12141 em
diante, mantém quatro opções: Domínio Simples, Energia Reversa, Pétala e
Aptidão Própria. O catálogo `ficha-v01/tecnica-do-livro.json` guarda
`rotas.sementes=[]`.

O extrator `extrair_tecnica.py:387` procura subseções de Sementes. No livro
atual, Sementes e os quatro nomes usam o mesmo nível de título; a seção
recortada não contém as quatro entradas. `_Dados.faixa()` não trata tabela
vazia e emite `$CO$2:$CO$1`.

Na oficial, `DADOS_AM!CS2:CS4` usa `$CO$1:$CO$2`. A lista de
`FICHA AMALDIÇOADA!J16` aponta para `DADOS_AM!$CS$2:$CS$4`. Com a rota 2,
as três expressões resultam em **semente / Domínio Simples / vazio**,
em vez das escolhas corretas. `CS5` ainda contém a quarta fórmula herdada,
mas está fora da lista atual. O efeito foi reproduzido na QA sem mudar a rota
da oficial. A correção deve recuperar as quatro opções do livro e validar
as suas regras, não retirar a rota nem reaplicar opções antigas sem fonte.

Prioridade de integridade mecânica: corrigir extração, guarda de tabela vazia,
fórmulas e validação como uma intervenção própria, com teste da rota completa.

### Barras visuais da FICHA

`S26`, `S30` e `S34` contêm `__xludf.DUMMYFUNCTION` dentro de IFERROR.
A QA confirmou erro tipo 5 (função desconhecida) na função fictícia e ausência
desse erro com SPARKLINE nativo. A ausência de erro efetivo na oficial não
certifica essas barras: o IFERROR mascara a falha. Corrigir em cópia e
conferir cores, proporções, zero e máximo; não é causa demonstrada da falha
de abertura no Android.

## 4. Dependências que mudam a estratégia

Foram conferidas as fórmulas do inventário, **6.440 células com validação**,
**60 regras condicionais** e as referências literais nas **225 fórmulas que
usam INDIRECT** (525 ocorrências da função). O relatório separa essa análise
de referências dinâmicas gerais e de código remoto.

### Efeitos FD: candidato a deixar de ser materializado

Não apareceu consumidor de `DADOS_R53!FD` nas fórmulas nativas, nas validações,
nas condições de formatação nem nos endereços literais de INDIRECT examinados.
Na fonte atual, `cartoes_diretos.py` substitui o resumo antigo por avisos e
outros resultados; `montagens_r53.exporta()` não exporta `efeitos`.
O runtime direto e seu JSON de configuração também não apontam para FD.

Portanto há duas intervenções possíveis, preservando a regra do motor:

1. Fatorar e continuar materializando: já tem prova local/nativa dos casos.
2. Após conferir o código instalado e consumidores externos, deixar de
   materializar esse resultado sem uso, conservando a definição no motor e
   seus testes. Isso retiraria 249 fórmulas e aproximadamente 8,88 MB de texto
   nativo (25,6% do total medido), sem apagar cartões, versões ou catálogos.

A segunda opção é candidata, não está liberada pela simples ausência de
referências estáticas. Não excluir a coluna física: isso deslocaria endereços.
Não somar os ganhos das duas opções, pois são alternativas sobre o mesmo alvo.
Muitos cartões vazios já possuem IF de guarda; o custo de carregamento do
texto/grafo não deve ser confundido com executar todos os ramos a cada edição.

### ANALISE: converter constantes exige preservar a restauração

O ensaio nativo confirmou igualdade de texto e tipo em cinco casos de
`stringValue`, incluindo apóstrofos e texto que parece fórmula/booleano.
Mas `Codigo.gs:485` chama `devolverConta_`, que só restaura entradas do modelo
iniciadas por `=`. Trocar apenas as 15.869 constantes por texto deixa dois riscos:

- com o script antigo, uma edição pode reinstalar a fórmula antiga;
- com um modelo só de literais, pode desaparecer a restauração que hoje existe.

A implementação precisa tratar explicitamente esses campos antes calculados,
preservar a restauração e validar CSV/consumidor. Não chamar a conversão de
mera limpeza sem essa mudança coordenada. Os endereços de fonte e as 18.393
chaves devem continuar iguais.

Não apareceu consumidor de ANALISE em fórmulas, validações ou condições lidas.
Isso não elimina o bot/CSV, os scripts nem nomes/proteções não expostos. Reduzir
E:L exige essa última conferência; as colunas estavam vazias no inventário.

### Outros cuidados

- FX/avisos tem consumidores e não pode ser eliminado como FD. Reutilizar
  `rotulo_base` corretamente; ele não é o campo `nome` das Melhorias.
- A análise mais completa encontrou **104 referências abertas**, incluindo
  duas a linhas inteiras em DADOS_INVOC e referências ao histórico salarial.
  Não limitar o histórico a um número fixo que descarte pagamentos futuros.
- A abertura atual já evita as varreduras antigas no evento simples. Só
  atribuir custo ao onOpen no Android se os logs mostrarem sua execução nessa
  abertura. Tempo do servidor e memória do aplicativo são medições distintas.

Evidência: [dependências](DEPENDENCIAS-2026-10-23.json).

## 5. Ordem final de implementação e limites do fechamento

1. Corrigir a integridade do gerador e a extração/lista de sementes, com
   regressões próprias. Preservar os dados digitados e a publicação salarial.
2. Ensaiar a fatoração de FD em cópia completa; avaliar a alternativa de não
   materializar FD somente após conferir o código remoto e consumidores.
3. Medir cópia de controle e cada intervenção no Android que falhou. Comparar
   abrir, editar, salvar, fechar e reabrir; conservar conteúdo e acionadores
   comparáveis. A QA de fórmulas deste fechamento não substitui esse ensaio.
4. Tratar FX, constantes da ANALISE com sua restauração, grade excedente,
   formatação e resíduos históricos em intervenções separadas, guiadas pelas
   medições. Corrigir as barras e conferir os rótulos faltantes.
5. Só considerar arquitetura móvel separada ou redução funcional se as
   intervenções preservadoras forem insuficientes e o limite estiver medido.

Pendências explícitas para aplicação: leitura atual do Apps Script instalado;
nomes/proteções e visual não expostos; snapshot completo/backup novo; ensaio
em cópia completa; Android afetado. As ferramentas Google funcionaram para
Sheets. Não há ferramenta de leitura/execução do Apps Script ou navegador
exposta nesta sessão. O pedido de metadados completos com lote vazio foi
recusado pelo schema antes de execução; nenhuma operação substituta alterou
a oficial para contornar essa limitação.

Não é necessário o PC antigo para implementar e validar a maior parte do
trabalho. O teste físico no Android continua indispensável. Inspeção visual
da QA foi limitada à releitura de valores e formatos pela API.

Recomendação: **GPT-6.1 Sol, High** para implementar os lotes isolados;
**GPT-6 Astra, High** se uma mudança no motor ou nas dependências exigir
revisão adicional. Sem merge em main, bot ou alteração de acesso nesta etapa.

## Reprodução local

Na raiz do checkout preparado:

```bash
.venv/bin/python r53/diagnostico-android/revisar.py nuvem-b47/saidas/diagnostico-mobile-20261023
.venv/bin/python r53/diagnostico-android/auditar_consumidores.py nuvem-b47/saidas/diagnostico-mobile-20261023
.venv/bin/python r53/diagnostico-android/ensaiar_fatoracao.py
.venv/bin/python -m unittest discover -s r53/testes -p 'test_*.py'
node r53/testes/cartoes_diretos_runtime.js
node salarios/testes.js
```

Os dois primeiros comandos dependem das leituras privadas ignoradas; não
fabricam aprovação se elas faltarem. O terceiro é portátil, cria o candidato
em memória, testa localmente e gera pedidos sintéticos offline. Nenhum desses
comandos envia pedidos ao Google ou modifica fontes de produção. Logs e
recibos nativos completos permanecem fora do Git.
