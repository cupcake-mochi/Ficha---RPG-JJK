# Origens da ANALISE · correção e auditoria de 30/10/2026

Correção separada da Carteira viva/PR31, baseada na main `ef361cc`. A PR31
continua aberta, sem incorporar ou reescrever seus commits. Nenhuma oficial ou
ficha de jogador recebeu esta atualização. Somente uma cópia nativa descartável
foi alterada no ensaio; ao terminar foi movida para a lixeira e sua aba fechada.

## Causa e alcance

`analise.trocas()` e os exportadores de domínio geram A (chave), B (fórmula), C
(origem) e D (parte). Depois, a apresentação horizontal da CONFIGURAÇÃO, as
extensões custom e a expansão/relocação dos cartões mudam endereços físicos.
Os operandos RANGE de B acompanhavam o mapa. Parte de C era texto dentro de uma
fórmula constante (`="'ABA'!A1"`) ou uma lista de referências; esses textos não
acompanhavam todas as transformações. A relocação de âncoras também precisava
transportar o metadado, além do consumidor real.

O exemplo informado foi reproduzido: `passiva.1.categoria`, linha 2809, B lendo
`'FICHA AMALDIÇOADA'!F392` e C declarando F379. O valor e a categoria estavam
corretos; o defeito era a indicação de onde procurar o campo.

Foram corrigidas **2.627 células C**, em origens da FICHA, FICHA AMALDIÇOADA,
INVOCAÇÕES e CONFIGURAÇÃO: 2.417 leituras de uma célula e 210 fórmulas compostas.
O manifesto JSON ao lado contém exclusivamente chaves e endereços do modelo
público, não dados de jogador. As chaves, sua ordem, B, D, estilos, validações,
notas, mecânicas e o restante do modelo não mudaram.

`referencias_origem.py` só reconhece referências qualificadas e listas completas
delas. Conserva cifrões, aspas, separadores e a representação literal/fórmula
constante. Não procura coordenadas dentro de prosa nem aplica uma substituição
global. Os mesmos mapas físicos são usados em `extensoes_custom.deslocar`,
`configuracao_horizontal.aplica` e na relocação de `cartoes_diretos.aplica`.
O contrato de domínio exportado antes da apresentação permanece inalterado.

## Validação e limites do pente fino

- Todas as **18.393 chaves** da ANALISE foram auditadas. Depois da correção,
  nenhuma referência de uma célula diverge de B.
- **3.264 fórmulas compostas/intervalos** foram tratadas separadamente. Suas
  **5.885 origens declaradas** coincidem com dependências efetivas de B. Não se
  transforma um MAP/INDEX ou intervalo em uma referência à primeira célula.
  Os 1.704 usos do nome local `item` em LAMBDA não são endereços quebrados.
- **45.698 referências qualificadas**, de B e de C, foram conferidas quanto à
  existência da aba e aos limites de grade: nenhuma fora do modelo.
- Comparação estrutural de todas as 26 abas geradas: somente as 2.627 origens
  mudaram em relação à base desta tarefa. O comparador histórico também aceita
  as seis mudanças de XP já existentes na main, totalizando 2.633 diferenças em
  relação à sua base antiga, e recusa qualquer outra mudança.
- Ensaiada aplicação nativa das 2.627 células, com leituras completas de A:D
  antes/depois. A, B e D permaneceram integralmente idênticos, inclusive tipos,
  valores calculados, notas e validações retornados. C conserva seu tipo de
  entrada e seus apóstrofos. Nenhum erro de cálculo retornado na ANALISE.
- Nova preparação sobre a cópia corrigida: zero pedidos, 2.627 já atualizadas.
  Reversão e reaplicação de três amostras (origem única, lista e origem de aviso)
  foram executadas e relidas iguais no Google. A reversão completa foi gerada,
  mas não foi executada integralmente.
- Testes focais cobrem texto literal/fórmula, nomes com apóstrofos, intervalos,
  inserções sucessivas, mapeamento horizontal, prosa intacta, falhas de chave/B/C/D,
  estilo, limite de grade, formato regional e repetição. Registrados no smoke.
- A suíte Python final passou nos **44 testes**, incluindo 14 testes focais de
  origens/migração. Os 89 casos do motor e 584 verificações do editor passaram. O transporte do
  pacote passou: nove arquivos, 26 abas de dados e 249 contextos.

Os menus CE foram preservados. Não houve alteração do RPG---BOT nem da correção
da PR85. Todos os valores de aviso em B da cópia ficaram iguais: diferenças de
compras na Ampliação, peças incompatíveis com Classe 0 e orçamento negativo
continuam sujeitos às validações anteriores. Não se declara uma ficha preenchida
aprovada por ter metadados corretos, nem se promete ausência universal de bugs.

Este pente fino cobre metadados/referências, integridade do modelo e regressões
mecânicas locais. Não repete todos os cenários de jogo no Google, não mede RAM ou
latência Android e não é uma nova validação funcional da Carteira viva.

## Artefatos

As fontes GS foram regeneradas: geração `5ddce2b71c0732ad`. A mudança de selo em
vários arquivos é esperada; dados fora de ANALISE C foram comparados. O pacote
integral foi conferido, **não instalado** em nenhum projeto Google. Não substituir
o pacote otimizado existente pelo integral para esta correção de metadados.

`r53/origens_analise.py` é um auditor/preparador offline: não tem cliente Google,
não executa código da planilha e não escreve remotamente. Gera guardas, pedidos
limitados a `ANALISE!C`/`userEnteredValue` e reversão. Não altera fórmulas B,
validações, notas, menus, categorias ou aprovações.

## Atualizar uma ficha existente

1. Com autorização para aquele alvo, faça snapshot nativo atual da ficha e de
   seu projeto. Ensaiar primeiro em uma cópia. Nunca construir/continuar.
2. Confira os metadados da planilha e leia A:D da ANALISE em blocos limitados,
   usando `userEnteredValue,effectiveValue,note,dataValidation`; salve as respostas
   JSON fora do Git. Não copie dados pessoais para o manifesto público.
3. Gere o modelo final em uma pasta ignorada:

   ```sh
   mkdir -p r53/saidas nuvem-b47/saidas/origens-local
   python3 ficha-v01/monta.py --exportar-r53 nuvem-b47/saidas/origens-local/modelo.json
   python3 r53/origens_analise.py --modelo nuvem-b47/saidas/origens-local/modelo.json --snapshot nuvem-b47/saidas/origens-local/leitura-*.json --saida nuvem-b47/saidas/origens-local/plano.json
   ```

4. Revise `mudancas`, `auditoria`, `limites`, `compostas` e `plano`. O preparador
   localiza por **chave**, não por número de linha da ficha existente. Confere a
   fórmula B contra o modelo, D e o texto anterior de C. Tolera apenas diferenças
   de notação equivalentes (separador regional, cifrões e aspas de nome de aba),
   preservando textos e estrutura de matrizes. Se qualquer campo divergir,
   interrompe a preparação inteira; não adapta automaticamente um layout antigo.
5. Imediatamente antes da escrita, releia os alvos e confira as `guardas`
   A/B/C/D do plano. Sem edições concorrentes, aplique os `pedidos` pela API
   nativa, no ID confirmado do alvo autorizado. O hash registra o preflight;
   **a API não fornece compare-and-swap**: o arquivo de plano, sozinho, não trava
   a planilha nem detecta edições posteriores. Não reaproveite um plano antigo.
6. Releia A:D integralmente. Exija somente as mudanças C previstas, A/B/D
   idênticos, tipos/apóstrofos/notas/validações preservados e ausência de novos
   erros retornados. Uma nova preparação deve produzir zero pedidos. Se houver
   aplicação parcial, leia novamente e prepare o restante; origens já corrigidas
   são reconhecidas. A `reversao` pertence ao snapshot daquela ficha.

Atualizar C resolve o metadado da ficha existente; não muda seu cálculo. O novo
gerador evita reincidência nas próximas construções. Em versões cujo código
ainda restaure a ANALISE a partir de um molde antigo, esse molde também precisa
de atualização incremental específica e teste de recuperação antes de liberar
o modelo. Não promover o pacote integral por cima dos incrementos instalados.
Nenhuma atualização de código/restauração da ANALISE de projetos antigos foi
ensaiada nesta tarefa; este limite deve acompanhar a entrega.

Snapshots, nomes/valores de personagens, planos aplicados, logs e captura da
limpeza estão somente em `nuvem-b47/saidas/origens-analise-20261030/`, ignorado.
Não houve novo acionador, acesso, reconstrução, merge ou alteração da PR31.
Sol/High para integração futura; Medium para revisão focal, sem mudar opções
automaticamente.
