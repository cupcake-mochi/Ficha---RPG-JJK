# Revisão da PR89 e auditoria das entradas de nível · 08/11/2026

Retomada Linux após as atualizações no Windows. Revisado o head
`e2b03307ebfaa3df67b494704508c10f3bd523b6` da
[PR89](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/89), sobre
`ab05bcf9cc5f831dfe460544f935546e40296ea8` da PR88.
Nenhum merge ou alteração nas oficiais, jogador ou PR31.

## Parecer sobre a atualização do Windows

Não apareceu novo defeito no delta da PR89 para níveis inteiros válidos.
AQ01 foi corrigido: Criação conserva o nível fabricado registrado, limitado
pelo invocador. Vazio mantém deliberadamente a prévia histórica no nível
do invocador. A descoberta AQ02 abaixo é uma lacuna anterior de validação,
também presente em Maldição domada; não é regressão introduzida pela PR89.

Conferências repetidas nesta retomada:

- Leitura das instruções e evidências sanitizadas do Windows, diff do gerador,
  reconciliação focal R66, incremento, recuperação e testes.
- Teste focal de preparação/transporte/recuperação com os insumos Android
  privados disponíveis: 13 valores/fórmulas, três notas, duas localidades.
- Teste de equivalência do modelo integral/incremental: 280.056 posições,
  26 abas; somente 13 valores e três notas previstos.
- Preparação sobre a base privada 36ca73ef… reproduziu exatamente o código
  esperado SHA-256 `ffd349c9299342d735917697355d3f278f526ff74b9e009706ce61a8b0784352`.
- Releitura nativa dos 13 valores/fórmulas e das três notas nas duas QAs,
  comparados com os planos atuais em pt_BR: conformes.
- PR89 aberta, sem conflitos e com os dois jobs smoke concluídos em sucesso:
  [42519708587](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/42519708587)
  e [42519688627](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/42519688627).
  PR88 continua em ab05bcf; PR31 em 765e3b2.

Os 312 casos, 26 controles de débito, dez edições reais finais e o smoke
integral de 123 verificações são a evidência registrada no Windows; não
foram repetidos nesta revisão. Seus snapshots privados não estão neste
computador. Não houve nova releitura integral do código instalado nesta
rodada: o hash acima foi reproduzido localmente, e o readback integral
nativo consta do relatório anterior. O pacote integral segue não instalado.

## AQ02 [P2] · Nível obtido aceita tipos inválidos e frações

**Confirmado nas duas descartáveis, sem correção instalada.**
A caixa “Obtida no nível” não tem validação de dados nas 12 entidades.
O gerador usa `N(entrada)` em DADOS_INVOC!DH2:DH13. Isso transforma texto
e FALSE em zero, que a fórmula FO interpreta como nível não preenchido.
Frações permanecem numéricas e atravessam MAX/MIN. TRUE vira nível 1.

Reprodução nativa, com invocador 30 e atributos/bônus originais da QA:

| Entrada armazenada | Nível efetivo | PV do primeiro Shikigami |
| --- | ---: | ---: |
| Número 7 | 7 | 23 |
| Fórmula =7 | 7 | 23 |
| Texto 7 | 30 | 92 |
| Texto Nível 7 | 30 | 92 |
| Fórmula que devolve texto 7 | 30 | 92 |
| Número 7,5 | 7,5 | 24,5 |
| Vazio | 30 | 92 |
| Número zero | 30 | 92 |
| FALSE | 30 | 92 |
| TRUE | 1 | 5 |

O caso vazio é o controle de compatibilidade esperado, não um erro.
Texto numérico aqui significa string efetivamente armazenada, por exemplo
com apóstrofo ou retornada por fórmula; digitar 7 normalmente pode ser
convertido pelo Sheets para número e corresponde ao controle correto.
O resultado é o mesmo em Criação e Maldição domada. Na primeira entidade,
texto 7 também elevou o orçamento de dois para oito espaços; os mesmos
níveis incorretos apareceram na entidade 12.

São 40 configurações nativas, 80 observações de entidade: dez variantes,
duas aquisições, entidades 1/12 e duas cópias. Há uma causa de validação,
não 56 defeitos independentes. Os 24 controles inteiro/fórmula numérica/vazio
foram conformes; 56 observações descrevem as sete variantes sem validação.
Nenhuma fórmula de produção foi substituída para fabricar a reprodução.

### Localização e tratamento recomendado

- `ficha-v01/ficha_invocacoes.py`: definição de nfixo com N; cálculo de
  fixo/nível; caixa nivel_fixo criada sem menu/validação.
- O mesmo N e o mesmo cálculo fixo já existem na base ab05bcf. O caminho de
  Criação passa a usá-los na PR89; Maldição domada já os utilizava.
- Corrigir em trabalho separado: validar nível inteiro, distinguir ausência
  real de entrada inválida e evitar promoção silenciosa para o invocador.
  Texto numérico deve ser interpretado de forma explícita ou sinalizado;
  texto livre, booleanos e frações precisam de revisão visível.
- Preservar o comportamento documentado do campo vazio, o limite pelo
  invocador e as montagens existentes. Não arredondar nem reescrever entradas
  silenciosamente. Considerar vazio por fórmula e entradas históricas no ensaio.
- Validação de interface sozinha não cobre valores antigos nem qualquer
  colagem/API; conferir também a fórmula e os moldes de restauração.

A revisão por código não encontrou saneamento do nível pelo onEdit atual.
A matriz desta rodada usou a API nativa do Sheets: ela verifica tipos e
recálculo, mas não dispara onEdit. Não houve novo ensaio de evento real,
instalação incremental, menu ou autorização Google nesta etapa.

## Preservação e limites

Snapshots novos, válidos e persistidos antes das gravações; escopo de escrita
restrito a nove entradas por cópia. As nove foram restauradas em cada QA.
Comparação pós-restauração de **11.371 posições por cópia**, incluindo
**11.322 posições de MONTAGENS em 34 contextos** das entidades 1/12:
zero diferenças de valores, fórmulas, tipos, notas ou validações lidas.
Metadados, com o mesmo escopo de leitura anterior, idênticos; auxiliares
continuam ocultas. Formatação condicional não fazia parte do snapshot
anterior desta rodada; não se declara comparação dela.

Visual restaurado conferido no navegador nas duas QAs. A conferência desta
rodada não equivale à comparação de MONTAGENS inteira realizada no Windows,
nem certifica todas as mecânicas, colagens arbitrárias ou latência Android.
Nenhuma geração pesada, acionador, ampliação de acesso ou código Google novo.

Evidências privadas somente em
`nuvem-b47/saidas/auditoria-nivel-obtido-20261108/`, ignorado:
snapshots, matriz bruta, comparação e capturas. O JSON sanitizado adjacente
contém os resultados sintéticos sem snapshots ou dados de personagem.

## Continuação

Ramo separado `codex/revisao-pr89-entradas-20261108`; PR89 permanece e2b0330,
sem incorporar este diagnóstico automaticamente na PR. Próxima ação:
corrigir AQ02 em ramo próprio sobre o estado revisado, com snapshots frescos,
delta mínimo e ensaio nas duas descartáveis; preservar PR88, suportes de
recuperação da PR89 e o escape da ANALISE. Nenhuma promoção autorizada aqui.

Recomendação: Sol/High para implementar/ensaiar AQ02; Sol/Medium para revisar
este parecer. Não alterar configurações nem abrir agentes.

