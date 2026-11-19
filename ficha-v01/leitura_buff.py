"""Leitura única do Buff/Debuff, igual na ficha do jogador e nas invocações.

10/11/2026, decisão do Mizuki: decimal arredonda contra o dono. Segue a regra
da especificação ("custo sobe, ganho desce, e o que você ganha nunca fica
abaixo de 1"): +1,5 vale +1, +0,5 vale +1, -1,5 vale -2, -0,5 vale -1.

Texto colado só vale quando é um número simples, com sinal opcional e
vírgula ou ponto decimal; a conta não depende da região da planilha. Data,
fração ("1/2") e qualquer outro texto valem 0, como o vazio.
"""

NUMERO_TEXTUAL = "^[+-]?[0-9]+([.,][0-9]+)?$"


def buff(x):
    """Expressão (sem "=") que lê o Buff/Debuff da célula x."""
    inteiro = f'VALUE(REGEXEXTRACT({x},"[0-9]+"))'
    quebrado = f'N(REGEXMATCH({x},"[.,][0-9]*[1-9]"))'
    texto = (f'IF(REGEXMATCH({x},"{NUMERO_TEXTUAL}"),'
             f'IF(LEFT({x},1)="-",-{inteiro}-{quebrado},MAX({inteiro},{quebrado})),0)')
    numero = f'IF(N({x})>0,MAX(1,INT(N({x}))),INT(N({x})))'
    return f'IFERROR(IF(ISTEXT({x}),{texto},{numero}),0)'
