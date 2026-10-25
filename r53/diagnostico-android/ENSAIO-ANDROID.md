# Primeiro ensaio de redução para abertura no Android

23/10/2026. O objetivo é testar a hipótese de peso no app Google Planilhas,
preservando a capacidade e as mecânicas. A falha relatada pelo usuário é real;
a relação causal com o peso ainda depende do teste no aparelho afetado.

## Entrega

- [A — controle](https://docs.google.com/spreadsheets/d/1mhrotVJIwblthbTT_lCoau8OmKYDezA0TphTSusUZqc/edit): cópia nativa atual da oficial, sem otimização.
- [B — otimizada](https://docs.google.com/spreadsheets/d/1rH1csUCpUWBoYRmyw4FdQahzdRqgcP9wk3Jer0rRUBE/edit): cópia de A, com fatoração de DADOS_R53!FD2:FD250.

A única intervenção no conteúdo de B foi substituir essas 249 fórmulas.
Continuam calculadas; nenhuma mecânica, cartão ou versão foi removida.
Abas, endereços, validações e estrutura são preservados. A oficial recebeu
somente consultas nesta etapa. Fontes de produção e script vinculado não
foram atualizados: isto é um candidato de teste, não publicação definitiva.

## Validação

O preparo confere todas as fórmulas originais contra o modelo completo,
sem passar pelo Workbook, e verifica a tradução relativa de todas as linhas.
A transformação já passou em 1.113 casos locais e em 89 casos nativos com
comparação exata de texto. Os campos de dependência são os mesmos.

`validar_android_ab.py` confere a releitura de todas as 249 fórmulas,
resultados atuais, formatos, validações e sentinelas de recursos/salários.
As contagens e reduções finais estão em `ANDROID-AB-2026-10-23.json`.
Não extrapolar redução de texto de fórmula para redução de RAM ou tempo.

O primeiro envio utilizou separadores ingleses e a releitura detectou erro
de análise de fórmula somente na cópia B. O preparo foi corrigido para `;`,
o piloto foi relido e o lote corrigido foi reaplicado. Evidências do erro e
da correção ficam no diretório privado; a validação final usa `final-*.json`.

Sem navegador conectado, a conferência de formato é pela API, não por imagem
renderizada. A abertura e a aparência no Android aguardam o ensaio abaixo.

## Teste no mesmo aparelho

1. Use a mesma conta, conexão e app Google Planilhas que falharam na oficial.
2. Abra B e registre se abre, tempo aproximado e se permite navegar pela ficha.
3. Feche o app e repita com A. Repita invertendo a ordem para reduzir o efeito
   de cache. Não edite dados entre os testes e não ative rotinas nas cópias.
4. Se houver falha, registre se fica carregando, exibe erro ou fecha o app.
   Informe também modelo do celular e versão do Android, se disponíveis.

Interpretação:

| Resultado | Próxima decisão |
|---|---|
| B abre e A falha, de forma repetida | Evidência favorável à redução; conferir uso e preparar manutenção definitiva. |
| A e B abrem | Copiar ou o estado do arquivo também pode influir; comparar novamente com a oficial. |
| A e B falham | A redução foi insuficiente ou existe outra causa; avançar em outra intervenção isolada. |
| A abre e B falha | Investigar regressão na cópia B antes de qualquer promoção. |

Cópias não recebem acionadores instaláveis da oficial. A e B estão sob a
mesma condição de cópia, mas resultados contra a oficial não isolam somente
o tamanho. O conteúdo do Apps Script vinculado não foi relido nesta sessão.
Não usar as cópias como fichas definitivas antes da revisão dessa dependência.

## Continuidade

A próxima rodada depende do resultado real no Android. Se necessário,
examinar avisos FX, excesso de grade/formatação e constantes em ANALISE,
sempre preservando contratos e restauração pelo script. Gerador, sementes e
barras são correções independentes; não são a causa demonstrada da abertura.

Snapshots, fórmulas completas, rollback e recibos estão em
`nuvem-b47/saidas/diagnostico-mobile-20261023/android-ab/`, ignorado pelo Git.
Os preparadores não enviam pedidos e recusam alvo diferente da cópia B.

Recomendação: GPT-6.1 Sol / Medium para interpretar o ensaio; High para a
próxima intervenção ou preparação de publicação.
