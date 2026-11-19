# Pontos de atributo colados como texto · 08/11/2026

Colar um dígito de `0` a `6` como texto em uma caixa de pontos da
entidade agora produz a mesma conta que o número correspondente.
A planilha preserva o tipo e o valor da entrada e conserva a
validação estrita do menu. Outros textos continuam sem somar pontos.
Os valores numéricos e os campos de Buff/Debuff seguem suas contas
anteriores.

O caso confirmado na revisão da PR91 foi repetido nas descartáveis
Era e Ciclo. Na entidade de nível 1, Força 3 e Destreza 3, a colagem
de `3` textual em Constituição agora produz Constituição 3, nove
pontos gastos e 8 PV. Antes, a mesma colagem produzia Constituição 0,
seis pontos gastos e 5 PV. O controle com o número `3` também deu
Constituição 3, nove pontos e 8 PV.

## Delta

As 60 fórmulas de `DADOS_INVOC!DJ2:DN13` tratam os cinco atributos
das 12 entidades. Para texto, exigem exatamente um dígito ASCII
entre 0 e 6 antes de converter. Entradas que não são texto
preservam o caminho anterior de `N()`. Não há mudança de validação, nota,
endereço, estrutura ANALISE ou montagem.

A geração `ec14f1ff36db9816` foi comparada em 280.056 posições
de 26 abas. O plano integral contém exatamente as 60 fórmulas
e coincide byte a byte com o candidato emitido pelo gerador e
ensaiado nas duas QAs. Pacote local com cinco partes e
SHA-256 `0bdd207cbe0f99cecad9700a3474581547efb8da37db12d2e3ff409a7a351881`.

Cada descartável recebeu um lote de 60 fórmulas após a
verificação do snapshot fresco e dos alvos da PR91. As fórmulas
foram relidas. A aplicação nativa ocorreu nas células da aba
auxiliar. O pacote integral foi gerado para revisão no Git.

## Validação

A matriz nativa verificou 96 observações de entidade e fez 480
conferências de entradas. Cobre as 60 caixas por cópia em quatro
cenários, com os dígitos `0` a `6` em texto, os números
correspondentes, outros textos e vazios ou fórmulas. Os casos
textuais e numéricos tiveram os mesmos pontos, totais, gastos,
PV, limites de perícia e avisos. Espaços, quebras de linha,
sinais, decimais, zeros à esquerda e caracteres fora da faixa
continuaram sem entrar na conta como pontos. Os casos de
fórmula cobriram retorno vazio, número e dígito como texto.

Nas duas interfaces, digitei apóstrofo e `3` em `INVOCAÇÕES!O21`,
copiei e usei **Colar somente valores** em `Q20`. A releitura
confirmou texto `3` no destino, validação estrita e o resultado
esperado. Repeti com o número `3`. O formato numérico das duas
células, alterado pelo ensaio de colagem, foi reposto ao final.
Como o menu continua estrito, o Sheets ainda pode mostrar
**Inválido** para o valor textual. A captura do cenário já
recalculado confirma que esse aviso de tipo convive com os 8 PV.

As 60 entradas da matriz foram restauradas e relidas. No cenário
de interface, foram repostos os seis valores e dois formatos que
haviam mudado em cada cópia. A comparação final cobriu 86.594
posições por cópia, incluindo MONTAGENS inteira `A1:I9543`.
Apenas as 60 fórmulas do plano divergiram. Os metadados
coincidiram, incluindo a formatação condicional. As abas
de teste foram fechadas.

Os testes focais locais verificaram a geração, o plano, a aplicação
e a reversão em pt_BR/en_US, além da recusa de alvos divergentes.
O comparador compartilhado reproduziu também o plano anterior
da PR91. Os ensaios em Sheets foram em pt_BR.

## Retomada

Ramo `codex/corrige-colagem-atributos-20261108`, empilhado sobre
a PR91. O plano versionado é `atributos_entidades_delta.json`.
A evidência sanitizada está em
`atributos_entidades_validacao_2026-11-08.json`.
Snapshots e capturas ficaram em
`nuvem-b47/saidas/correcao-colagem-atributos-20261108/`.
A aplicação foi restrita às duas descartáveis.

O preparador `preparar_atributos_entidades.js` recebe os
diretórios GS de antes e depois e o destino do plano JSON.
Seu `pedidos(delta, snapshot)` só produz a atualização se os
60 alvos corresponderem à base. Para reversão, informe o
snapshot posterior e o terceiro argumento `true`.
