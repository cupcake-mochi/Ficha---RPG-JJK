# Revisão da PR87 e contagem de especiais normais · 07/11/2026

## Revisão da PR87

Revisado o head `0554071051697790d9c807f2478f6c5816018aa1` sobre a PR86
`6568838badd1a92b130dd46058527fa089da655f`. A PR87 está aberta, fora de
rascunho, sem conflitos e com dois checks `smoke` concluídos em SUCCESS
nesse mesmo commit. Nenhum bloqueio novo confirmado no escopo do repertório
extra das Trilhas. Não houve alteração do ramo da PR87 nesta revisão.

Foram relidos o gerador, o seletor independente, a preparação estrita,
guardas do caminho leve, recuperação de mesclas/blocos mistos e moldes
legados de Prática, além do empacotamento e das evidências sanitizadas.
As fórmulas nativas de contagem dos extras continuam com critério `<>`
nas duas QAs. As tabelas e o seletor permanecem instalados.

Repetidos com sucesso:

- `node r53/testes/repertorio_trilha.js <Código-PR86> <partes-Android-antigas>`:
  102 alvos, 14 notas, duas localidades, reversão e recuperação focal/mista;
  modelo antigo sem DADOS_R53/ANALISE e preservação dos moldes legados.
- `node r53/testes/repertorio_trilha_modelo.js <fontes-PR86>`: 280.056
  posições, 26 abas, equivalência incremental/integral, idempotência e
  recusa de base divergente antes de mutações do retrato.

A matriz nativa de 234 casos e 16 ações reais da implementação não foi
repetida integralmente sem motivo. O relatório da correção e o hash do
código salvo continuam em `CORRECAO-REPERTORIO-TRILHA-2026-11-07.md`.
As limitações declaradas da revisão manual de talentos, definição da
entidade e quantidade efetivamente ativa da Principal permanecem válidas.

## N01 · nomes não textuais desaparecem do orçamento normal

O pente-fino seguinte confirmou **um defeito na contagem das especiais
normais**. A fórmula consolidada de `ficha-v01/expansao_domada.py` usa:

```text
COUNTIFS(DADOS_R53!$A$2:$A$253,"entidade."&$DD2&".esp.*",
         DADOS_R53!$B$2:$B$253,"?*")
```

O critério `?*` conta somente texto não vazio. Nomes numéricos, booleanos
ou fórmulas que devolvem número ficam registrados no cartão e no registro
DADOS_R53, mas não entram no consumo apresentado em `DADOS_INVOC!IE2:IE13`
nem no requisito conjunto em `JJ2:JJ13`. O campo de nome é livre, sem uma
validação que o restrinja a texto. Não foi necessário remover validações
nem alterar a fórmula para reproduzir o defeito.

**Exemplo nativo, nas duas cópias e nas 12 entidades:** nível próprio 14,
capacidade 4, domínio Completo de custo 3 e duas especiais normais com nomes
numéricos 7/8. O consumo correto é **2+3 de 4**, exigindo aviso de **5/4**.
A ficha mostra **0+3 de 4**, e o aviso de espaços excedidos não aparece.
Renomear as duas para texto restaura a contagem e o aviso.

| Entrada nos dois nomes | Contagem esperada | Obtida | Aviso de excesso |
| --- | --- | --- | --- |
| Texto comum | 2 | 2 | Sim |
| Números 7 e 8 | 2 | 0 | Não |
| Números 0 e 1 | 2 | 0 | Não |
| Booleanos FALSE e TRUE | 2 | 0 | Não |
| Textos "0" e "1" | 2 | 2 | Sim |
| Fórmulas `=7` e `=8` | 2 | 0 | Não |
| Texto comum e número 8 | 2 | 1 | Não |
| Fórmula `=""` e vazio | 0 | 0 | Não, corretamente |
| Fórmulas `="7"` e `="8"` | 2 | 2 | Sim |
| Textos literais "=7" e "=8" | 2 | 2 | Sim |

É uma falha de contagem/aviso, não prova de que uma montagem individual
ou aquisição mecânica esteja aprovada em todos os demais requisitos.
Nenhuma restrição legítima de tipo, refino ou especialização foi removida
para produzir o resultado. Esses avisos foram mantidos e separados do
teste específico de espaços excedidos.

O critério pertence à consolidação entregue pela PR86 e não foi alterado
pela PR87. Não é regressão da recuperação nem da concessão dos extras da
PR87, que já trata nomes numéricos. A pendência deve ser corrigida
separadamente antes de considerar encerrada a integração dos orçamentos.

## Ensaios e preservação

Somente as mesmas descartáveis Era e Ciclo receberam entradas sintéticas.
Foram **dez configurações × 12 entidades = 120 casos por cópia**, total 240:
60 reproduções e 60 controles por cópia. As 120 reproduções totais são
variações de N01, não 120 defeitos diferentes.

O invocador ficou no nível 30 e cada entidade no nível próprio 14, com
tipo/aquisição Maldição domada e domínio Completo. Foram limpos os oito
nomes normais de cada entidade durante a preparação de cada cenário;
somente os dois primeiros receberam os tipos de entrada da tabela.
A Classe e as compras dos cartões não foram modificadas. A contagem
de aquisição, por contrato, independe da Classe e das versões preparadas.

A API nativa do Sheets executou os cálculos. Ela não dispara onEdit;
esta rodada não acrescenta testes de eventos ou de recuperação de fórmula.
Não houve instalação de código, edição de fórmulas, correção mecânica,
acionadores novos ou alteração de acesso.

Foram restauradas **158 entradas por cópia**, com as mesmas fórmulas e
tipos anteriores. Snapshot/releitura cobriram **33.458 posições por cópia**,
incluindo **31.968 de MONTAGENS** dos 96 contextos normais. A resposta nativa
contém 17.786 posições com metadados explícitos, das quais 16.320 em
MONTAGENS; caudas omitidas nas faixas foram tratadas como vazias nas duas
leituras. Zero diferenças e zero erros nos intervalos conferidos.
Comparados valores digitados/calculados, fórmulas, tipos, notas e validações;
formatação não foi escrita ou incluída nessa comparação delimitada.

Os cabeçalhos e o estado restaurado foram conferidos visualmente no Google
Sheets das duas cópias. As auxiliares permaneceram ocultas. Nenhuma montagem
salva foi alterada ou recuperada por substituição do pacote integral.

Evidência sanitizada: `repertorio_normal_resultados_2026-11-07.json`.
Snapshots, metadados e capturas somente na pasta privada ignorada
`nuvem-b47/saidas/auditoria-repertorio-normal/`. Ramo separado
`codex/auditoria-repertorio-normal-20261107`, sobre a PR87.

Não houve merge nem alterações nas oficiais, jogador ou PR31, que permanece
aberta em `765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`.
O pente-fino geral não está encerrado por essa amostra. Outros `COUNTIF`
com `?*` não foram automaticamente classificados como defeitos: alguns
contam seleções de catálogo já convertidas em texto. Exigem exame próprio.

Próxima correção proposta: contabilizar todos os nomes não vazios no
orçamento normal, preservando tipos, identidades, montagens e as duas
fórmulas por entidade. Incluir novo delta incremental e moldes de
recuperação; ensaiar número/texto/vazio e recuperação real nas duas QAs.
Não aplicar substituição global de `?*` nem de coordenadas.

Modelo/esforço: **Sol/Medium** para revisão do diagnóstico e **Sol/High**
para implementação e ensaio da correção. Nenhuma configuração foi alterada.
