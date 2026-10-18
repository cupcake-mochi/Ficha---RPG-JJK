# B47 — medidas após D · 17/10/2026

Item 2 concluído como medição/perfil. Base `c3104a1`, produção GS intacta.
Detalhes e amostras em [MEDIDAS-POS-D.json](MEDIDAS-POS-D.json).
Perfil acima é anterior à publicação oficial e à correção posterior do transporte.
Oficial B47 concluída na janela acompanhada. As três continuações de sucesso
registraram 187 + 169 + 254 = 610 s no relógio interno; falhas iniciais,
correção/publicação e preparação via API ficam separadas em OFICIAL-B47.json.
Não é comparação controlada com os 821 s históricos nem tempo total da janela.
Exportação final oficial: 2.590.926 bytes, 66.242 fórmulas, 22 abas, zero erros.
Comparação integral aprovada contra referência nativa; nada foi importado.

## Tamanho e capacidade

| Medida | v9 histórica | A+B histórico | C+D atual |
|---|---:|---:|---:|
| Linhas declaradas de CONFIGURAÇÃO | 18.659 | 1.731 | 2.810 |
| Fórmulas de CONFIGURAÇÃO no modelo | 2.264 | 610 | 680 |
| Menus de CONFIGURAÇÃO no modelo | 5.156 | 495 | 815 |
| Notas de CONFIGURAÇÃO no modelo | 28.538 | 2.490 | 3.995 |
| Grupos de expansão de texto | 1.219 | 66 | 136 |
| Chaves de ANALISE | 18.948 | 7.356 | 8.190 |
| Arquivos GS | 23 | 20 | 35 |
| Soma de bytes GS | 9.543.357 | 5.682.399 | 7.068.792 |
| Maior GS, bytes | 843.661 | 816.380 | 840.243 |
| XLSX da calculadora local, bytes | 3.763.979 | 1.681.795 | 1.995.733 |

Histórico: `capacidade-b47/RELATORIO.md`, Linux, 16/10. Atual: modelo fresco
da retomada, hash registrado. C acrescentou os catálogos aprovados; os cinco
grupos de A mantêm 10/30/30/10/10 vagas. GS abaixo de 900.000 bytes.
Revisão/cópia nativa: 22 abas, 14.505 linhas de grade, 467.511 células
alocadas. CONFIGURAÇÃO aloca 2.812 linhas, incluindo a cauda de alturas.
Grade não equivale a células usadas.

Reutilizada a auditoria D: **66.242 fórmulas na exportação XLSX nativa**,
zero erros, 4.470 notas (`FOTO-REVISAO-POS-FUNDO.json`). Não refeita nem
chamada contagem atual de fórmulas CellData. Campo size do Drive: revisão
1.299.538 bytes; construção vazia 1.111.362. Arquivos/entradas diferentes:
esse campo não equivale ao XLSX exportado nem ao consumo de memória.

## Tempo nativo e interface

Cópia de teste `1_1oBYdoci0j-B5LSfYp6UPLpnQB5vNxEOJafx-FRHqw`, Codigo f77b39db
já publicado (`NATIVO-CODIGO-REVISAO-D.json`, publicacao_notas_copia).
Projeto descoberto pelo menu Extensões:
`11TDlkSZJd7yCn7Iqm1e6EJEXt-BvBcXpJ160R4l9qhoDHLjhqhxckitL`.
Nenhum código novo publicado nesta retomada.

| Operação | Duração | Definição |
|---|---:|---|
| Abrir aba até estado inicial disponível | 2,959 s | Automação/transporte incluídos; cache não controlado |
| onOpen | 7,767 s | Histórico Apps Script concluído |
| Colar/confirmar 2.464 caracteres | 0,317 s | Interface, antes de terminar o ajuste |
| onEdit texto em CONFIGURAÇÃO!B769 | 10,124 s | Gatilho completo; três alturas 25→140 px |
| onEdit limpeza | 7,908 s | Gatilho completo; alturas 21 px |
| Cinco seleções comuns | 3,913–6,109 s | Concluídas; sem expansão dirigida |
| Seleção AA207 da invocação | 10,011 s | Abriu linha/coluna recolhidas, conferidas por metadados |
| Construção já provada em D | 821 s | 177 + 190 + 141 + 313 s; não repetida |

Inícios exibidos: 20:22:11 / 20:22:55 / 20:24:02 / 20:24:52
(abertura/texto/limpeza/expansão). Amostra pequena, não benchmark estatístico.
O gatilho continua após a interface aceitar o texto. Salvamento concluído
observado e entrada relida; sem sondagem contínua para isolar sua duração.
O intervalo até a observação posterior não é latência de salvamento.
Construção D teve falha transitória de serviço de 44 s separada dos 821 s.
Maiores etapas: menus 143,6 s, CONFIGURAÇÃO 88,2 s, ANALISE 48,2 s.

Restaurados e relidos: valores/efetivos/notas/validações/formatos de B769:O771,
alturas originais de 25 px (limpar produz 21 px; por isso repostas explicitamente),
todos os grupos de INVOCAÇÕES iguais ao snapshot. Revisão preenchida e
oficial não receberam essas edições.

## VM e limite B84

Windows, Node 24.19.0, Python 3.12.14; execução em série. Cinco contextos:
576,877 / 420,638 / 375,727 / 460,796 / 637,015 ms, mediana **460,796 ms**.
Texto: 100 amostras após 20 de aquecimento, mediana **0,662 ms**, p95 0,805 ms;
quatro leituras dos limites do Range. CPU/compilação locais, sem Google.
A/B media 327,2 ms / 0,28 ms em outra máquina Linux: não é comparação
controlada de velocidade nativa.

Inicialização global ainda materializa ABAS/expande complementos em
juntarAbas_/juntarValores_. Guardas de geração, cópias idempotentes, quatro
limites lidos uma vez e retorno da paleta sem pendência já existem.
CPU local subsegundo contrasta com gatilhos nativos de vários segundos.
Serviços, inicialização Apps Script e rede são candidatos (**inferência**),
sem percentuais atribuídos sem instrumentação nativa por trecho.

B84, evitar integralmente preparar construção nas operações pequenas, fica
como **otimização futura delimitada**. Carregamento sob demanda não implementado.
Reescrever 35 módulos exigiria nova publicação/regressão; não faz parte do
item 2 de medidas desta retomada. O perfil não demonstra necessidade disso
para concluir a entrega atual.

Sete provas de Configuração: 31.646 ms de escrita + leitura API, com
conector/recibos; não mede onEdit. Calc não executado neste Windows; histórico
registra dois timeouts de 600 s no teste pessoal. Google foi operacionalmente
mais rápido nesta retomada, sem razão numérica comparável entre motores/máquinas.

Reprodução: `python acabamento-b47/medir-pos-d.py --modelo nuvem-b47/saidas/progressao-em-integracao.json --saida <pasta-privada>`.
Recibos/imagens: `D:/JJK - Project/B47/evidencias/2026-10-17/pos-d/perfil-*`.
Dados do personagem fora do Git. XLSX nunca importado no Google.
Próximo: oficial pelo roteiro com usuário presente/janela sem cópias.
Sol/Médio para publicação mecânica; aumentar esforço se surgir divergência.

