# PR92 revisada e Buff/Debuff textual reproduzido · 08/11/2026

## Revisão da PR92

A PR92 estava aberta e sem conflito no commit
`6c9128aad33d346f57a868b2daf2f60e63180dc9`, sobre a PR91 em
`b804d1a45bbdd83c04411b45b3ed30525ba8eb34`. Os workflows de
[pull request](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/42544395671)
e [push](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/42544375995)
passaram nesse commit.

O teste focal de atributos passou. O preparador comparou 280.056
posições em 26 abas e reproduziu o delta versionado byte a byte.
As 60 fórmulas em `DADOS_INVOC!DJ2:DN13` já correspondiam ao
delta nas duas QAs. A leitura simulou a instalação sem enviar
pedidos de alteração. A PR92 conta o dígito textual 0–6 nos
pontos de atributo e preserva as entradas e os menus. As 96
observações nativas de pontos pertencem à rodada de implementação.

## Ajustes de Buff/Debuff ignorados quando colados como texto

O ensaio usou a entidade 1 em cada QA, com Força, Destreza e
Constituição base 3 e sem Vigor treinado. O cenário inicial tinha
Constituição 3, PV máximo 8, Vigor 3 e nove pontos gastos. Em
`INVOCAÇÕES!O21`, digitei o ajuste com apóstrofo e sinal, copiei
com Ctrl+C e colei somente valores com Ctrl+Shift+V em Q21, R26 e
P31. Repeti com número armazenado como número. O Sheets manteve
o texto com sinal nos três destinos.

| Cópia | Ajuste colado | Ajustes relidos em DQ2, DZ2, EC2 | Constituição | PV máximo | Vigor | Pontos gastos |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Era | Texto `-2` | 0, 0, 0 | 3 | 8 | 3 | 9 |
| Era | Número `-2` | −2, −2, −2 | 1 | 4 | −1 | 9 |
| Ciclo | Texto `+2` | 0, 0, 0 | 3 | 8 | 3 | 9 |
| Ciclo | Número `2` | 2, 2, 2 | 5 | 12 | 7 | 9 |

As famílias `u`, `us` e `ut` em `ficha-v01/ficha_invocacoes.py`
usam `N()` para ler Buff/Debuff de atributos, estatísticas e
resistências. A nota do campo informa que a entrada soma ou
subtrai do valor acima. Nos três campos ensaiados, `N()` devolve
zero quando o ajuste fica armazenado como texto. O grupo usa
a mesma conversão nas 12 entidades. A reprodução nativa
cobre três campos na entidade 1 de cada cópia e dois inteiros
com sinal. Frações e formatos regionais ficaram fora do ensaio.

O achado é anterior à PR92. A correção deverá ficar em delta
separado e preservar entradas, ajustes numéricos existentes e
a distinção entre pontos base e ajustes.

## Preservação

Cada cópia teve 17 posições no cenário sintético, com nove
valores e quatro formatos repostos. A comparação final cobriu
86.596 posições por cópia, incluindo MONTAGENS inteira
`A1:I9543`. Os campos comparados e os metadados conferidos
voltaram ao estado inicial. As abas de teste foram fechadas.
O registro sanitizado da comparação final está em
`revisao_pr92_buffs_entidades_2026-11-08.json`. Snapshots e
capturas permanecem no diretório privado ignorado pelo Git.
As escritas Google da rodada se limitaram às descartáveis.
