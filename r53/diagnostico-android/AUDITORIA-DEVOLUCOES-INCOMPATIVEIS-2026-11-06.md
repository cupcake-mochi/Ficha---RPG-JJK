# Instalação da PR78 e auditoria de devoluções incompatíveis · 06/11/2026

## PR78 nas descartáveis

A PR78 `262e264` estava sem conflito e com os dois checks aprovados.
O teste local de Sem Volta e a conferência do transporte passaram.
O Código anterior e as fórmulas dos 753 alvos foram guardados antes
da aplicação. O Código.gs foi salvo e relido integralmente nas duas
descartáveis. SHA-256 do Código instalado
`01e6422424022d301f994c2dbae84ee630849d81e36ec80c41df04bee6db134e`.
O EditorR53 manteve o hash anterior.

Foram instaladas e relidas 753 fórmulas por cópia, em 21 lotes nas
colunas CK, CP e FX de DADOS_R53. A releitura encontrou zero erros
de fórmula e nenhuma diferença de nota ou validação.

| Cópia | Recuperações em cartões comuns | Recuperação em Classe 0 |
| --- | --- | --- |
| Era | CK2 e FX2 | CP252 |
| Ciclo | CP2 e CK2 | FX253 |

As seis fórmulas foram apagadas na interface e voltaram idênticas
à proposta. As execuções bem-sucedidas levaram entre 6,917 e
12,239 segundos no painel do Apps Script. A primeira edição de
CP2 no Ciclo ocorreu enquanto havia lotes em andamento. O
acionador simples chegou ao limite em 30,764 segundos e a célula
ficou vazia. Após o último lote, a fórmula proposta foi reposta
manualmente para repetir o ensaio. A nova edição isolada restaurou
a fórmula automaticamente e o acionador concluiu em 12,239 segundos.
A causa do primeiro estouro de tempo ficou indeterminada.

O bloco compactado de recuperação contém 736 moldes, ante 4 na
PR77. Descompactado, passou de 26.577 para 6.580.403 bytes. Essa
comparação mede o conteúdo do bloco e deixa em aberto o custo
efetivo na abertura e a contribuição para o estouro de tempo.

DADOS_R53 voltou a ficar oculta. O intervalo de transporte foi
relido vazio. A releitura de 595 células por cópia, incluindo 532
posições de MONTAGENS, encontrou zero diferenças fora do lote.

## Pente-fino

Regra R66 de `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Os casos abaixo foram reproduzidos na Era e no Ciclo, na Classe 3.
Cada combinação sinalizou REVISAR com o aviso previsto, mas a
Restrição continuou somando pontos ao saldo.

| Combinação | Crédito aplicado ao saldo | Crédito esperado |
| --- | ---: | ---: |
| Queima-Roupa em Toque | 3 | 2, da Forma Toque |
| Queima-Roupa em Aura | 2 | 0 |
| Queima-Roupa em aplicação exclusivamente pessoal | 3 | 0 |
| Queima-Roupa com Longe | 2 | 0 |
| Atrasar com Rápido | 3 | 0 |
| Parado com Reação | 2 | 0 |
| Carregar com Armado | 2 | 0 |

A devolução total é limitada aos pontos pagos em Melhorias.
Por isso o crédito efetivo pode ficar abaixo do valor bruto da
Restrição. Os controles conservaram +3 para Queima-Roupa em
Projétil, +2 em Explosão, +2 para Toque sozinho, +2 para Atrasar
com Precisão e +3 para Carregar com Rápido.

Em `r53/modelo.py`, a fórmula de crédito por vaga é montada
separadamente dos avisos de incompatibilidade. As condições desses
avisos já estavam na PR77 e não bloqueavam o crédito. Um eventual
ajuste deve manter os controles válidos, incluindo o crédito
intrínseco de Toque, e limitar o bloqueio à Restrição incompatível.

As regressões focais de Sem Volta passaram. Cura automática
ficou em REVISAR com crédito zero e a mescla declarada dependente
conservou os 3 pontos. Em Classe 0, Sobrecusto manteve 5d8
e zero crédito. Barulho, válido, manteve 6d8 e 1 ponto de crédito.

Foram 16 cenários por cópia. As 21 entradas temporárias foram
repostas. A releitura de 622 células por cópia, incluindo 539
posições de MONTAGENS, encontrou zero diferenças e zero erros.
A PR78 permanece instalada nas duas descartáveis ensaiadas.
Evidências privadas em `nuvem-b47/saidas/instalacao-sem-volta/`.
