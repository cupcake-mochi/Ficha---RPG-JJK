# -*- coding: utf-8 -*-
"""Texto que abre frase ou título com a inicial minúscula, corrigido na saída.

A planilha viva é escrita à mão, e boa parte do texto curto da INVOCAÇÃO e do CATÁLOGO ("técnica",
"prende o alvo", "capítulo 16", "sobrou ponto") nasceu com a primeira letra minúscula mesmo abrindo
frase, título ou mensagem. 19/09/2026, pedido do Mizuki: "tem uns textinhos bem simples e curtos em
invocação e catálogo que estão em minúsculo a primeira letra, mesmo sendo início de frase ou título".

Dois casos, com a mesma regra por trás — a primeira letra do texto vira maiúscula:

  · texto digitado na célula: capitaliza a primeira letra que não é espaço, se ela for minúscula;
  · mensagem que uma FÓRMULA devolve ("estourou o total", "sobrou ponto", "ok", "cada um dos cinco rola
    isto"...): a fórmula é a mesma, só o texto entre aspas muda. Nenhuma fórmula da ficha compara contra
    esses textos — conferido — então trocar a inicial não muda conta nenhuma.

Fica de fora a notação de dado ("d20 +"), que se escreve minúscula em qualquer lugar.

Um terceiro caso, que não é de inicial: o texto que o livro mudou depois da exportação e a planilha viva
ainda tem com a frase velha (`_TROCAS_DO_LIVRO`). Hoje são duas frases, o Jorro do CATÁLOGO e a nota da CD na INVOCAÇÃO. O Jorro o capítulo 16
escreve "ataca e empurra em linha ou em área" desde a decisão do Mizuki na v0.246 do sistema (B13).

O comparar-ficha-01.py importa `corrige_valor` daqui pra saber que essa diferença é esperada, e o
conferir-ficha-xlsx.py confere que não sobrou texto minúsculo pra trás.
A ficha de invocação solta (ficha-invocacao/constroi.py) carrega este módulo por caminho e roda a mesma
`corrige_valor` no fim do `constroi()`, então os dois arquivos dizem as mesmas palavras.
"""
import re

ABAS_CORRIGIDAS = ("INVOCAÇÃO", "CATÁLOGO")

_DADO = re.compile(r"^\s*d\d")

# Frase que o livro mudou. A chave é a frase como a exportação a tem, com a primeira letra em minúscula (a
# inicial sobe depois, pela regra de cima); o valor é a frase como o livro a escreve. Chave por texto e não por
# endereço, porque o Mizuki insere linha pelo Sheets. O Remoto e a Montaria não entram: a Montaria já diz o
# que o livro diz, e o Remoto segue a peça 15 em vez do livro, que é decisão da revisão das invocações (B13).
_TROCAS_DO_LIVRO = {
    "CATÁLOGO": {"ataca em linha ou em área": "ataca e empurra em linha ou em área"},
    # v0.251 do sistema (B13): o capítulo 16 escreve a CD dos efeitos. A aba INVOCAÇÃO da ficha principal
    # ainda não tem os campos dela (a ficha solta tem), então a nota diz a conta em vez de dizer que ela não existe.
    "INVOCAÇÃO": {
        "a CD dos efeitos dela não tem fórmula em documento nenhum — nem o capítulo 16, ainda. Enquanto não existir, "
        "use a da ficha padrão do invocador.":
        "A CD dos efeitos dela é 8 + o atributo dela + a maestria do dono, mais o bônus da Voz ou do Preito, que "
        "não somam. Esta aba ainda não faz a conta: some à mão. A ficha da invocação solta já a calcula.",
    },
}

# Os trechos entre aspas que as fórmulas da INVOCAÇÃO devolvem como mensagem ou valor de caixa. O que vem
# depois da aspa de abertura é a inicial que sobe. A lista é explícita, e não uma regex geral sobre toda
# aspa de toda fórmula, porque fórmula também usa aspas pra nome de aba, de lista e de opção ("Matilha").
_MENSAGENS = [
    '"estourou o total"', '"estourou o teto de ', '"sobrou ponto"', '"ok"', '"estourou "&',
    '"cada um dos cinco rola isto"', '"o corpo em campo rola isto"', '("custa "&',
    '"a Ação Padrão, toda rodada"', '"a sua, e ela age logo depois de você"',
]


def _sobe(s):
    """A primeira letra que não é espaço, em maiúscula — e só se ela for minúscula."""
    for i, ch in enumerate(s):
        if ch.isspace():
            continue
        return s[:i] + ch.upper() + s[i + 1:] if (ch.isalpha() and ch.islower()) else s
    return s


def _sobe_no_token(token):
    """'"estourou ' -> '"Estourou ': a inicial que vem logo depois da aspa de abertura."""
    i = token.index('"') + 1
    return token[:i] + token[i].upper() + token[i + 1:]


def troca_do_livro(aba, valor):
    """A frase como o livro a escreve, se a célula tem a frase velha; senão None."""
    if not isinstance(valor, str) or not valor.strip():
        return None
    return _TROCAS_DO_LIVRO.get(aba, {}).get(valor[:1].lower() + valor[1:])


def corrige_valor(aba, valor):
    """O valor da célula como o gerador passa a escrevê-lo. Devolve o mesmo objeto se nada muda."""
    if aba not in ABAS_CORRIGIDAS or not isinstance(valor, str):
        return valor
    valor = troca_do_livro(aba, valor) or valor
    if valor.startswith("="):
        if aba != "INVOCAÇÃO":
            return valor
        for token in _MENSAGENS:
            valor = valor.replace(token, _sobe_no_token(token))
        return valor
    if _DADO.match(valor):
        return valor
    return _sobe(valor)


def aplica(layout):
    """Devolve quantas células mudaram de texto."""
    n = 0
    for aba in layout["abas"]:
        if aba["nome"] not in ABAS_CORRIGIDAS:
            continue
        for reg in aba["celulas"]:
            novo = corrige_valor(aba["nome"], reg[1])
            if novo != reg[1]:
                reg[1] = novo
                n += 1
    return n
