# -*- coding: utf-8 -*-
"""O Teste de Resistencia treinado soma a maestria, e nao 2. E o B14.

A planilha viva somava `IF(<caixa>=TRUE,2,0)` nos quatro TRs, que e a regra do manual da v0.104.
O capitulo 1 do manual soma a maestria desde a v0.117 do sistema, e a regra desta pasta e que o
manual vence. A planilha viva continua dona do DESENHO da FICHA; esta limpeza troca so o termo
somado no treino das quatro formulas.

O monta.py aplica, e o comparar-ficha-01.py le a mesma funcao para contar a limpeza. Uma funcao,
dois leitores: e a licao no 9, do mesmo jeito que o dados_catalogo.py.

Nenhum endereco esta escrito aqui. A linha de cada TR sai do rotulo com o nome que o catalogo da,
a caixa sai da propria formula, o termo sai do `bonus_se_treinado` do catalogo, e a celula dele
sai do indice que a ficha publica na DADOS.
"""
import json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TREINO = re.compile(r"IF\((\$?[A-Z]+\$?(\d+))=TRUE,([^,()]+),0\)")


def _linha_col(coord):
    m = re.match(r"^([A-Z]+)(\d+)$", coord)
    col = 0
    for ch in m.group(1):
        col = col * 26 + ord(ch) - 64
    return int(m.group(2)), col


def _aba(layout, nome):
    return next(a for a in layout["abas"] if a["nome"] == nome)


def indice(layout):
    """o indice que a ficha publica na DADOS: a coluna BA e o campo, a BB e a celula. Desde 17/09/2026
    a celula e formula, e quem sabe ler as duas formas e o indice_ficha.py."""
    import indice_ficha
    return indice_ficha.indice(layout)


def trocas(layout, CAT=None):
    """{celula da FICHA: formula nova} das formulas de TR cujo treino soma outra coisa que o
    termo do catalogo. Sai vazio quando a planilha viva ja soma o termo certo."""
    if CAT is None:
        CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    tr = CAT["testes_de_resistencia"]
    nomes = {t for t in tr if isinstance(tr[t], dict)}
    termo = tr["bonus_se_treinado"]
    alvo = indice(layout).get(termo)
    if not alvo:
        raise SystemExit(f"o catalogo manda somar '{termo}' no TR treinado, e o indice da DADOS "
                         f"nao publica essa celula")
    ref = "$" + re.sub(r"(\d+)$", r"$\1", alvo)

    ficha = _aba(layout, "FICHA")
    rotulos = {}
    for reg in ficha["celulas"]:
        if isinstance(reg[1], str) and reg[1].strip() in nomes:
            lin, col = _linha_col(reg[0])
            rotulos[lin] = (col, reg[1].strip())
    novas, achados = {}, set()
    for reg in ficha["celulas"]:
        v = reg[1]
        if not (isinstance(v, str) and v.startswith("=")):
            continue
        lin, col = _linha_col(reg[0])
        if lin not in rotulos or col <= rotulos[lin][0]:
            continue
        m = _TREINO.search(v)
        if not m or int(m.group(2)) != lin:
            continue
        achados.add(rotulos[lin][1])
        if m.group(3) != ref:
            novas[reg[0]] = v[:m.start(3)] + ref + v[m.end(3):]
    if achados != nomes:
        raise SystemExit(f"nao achei a formula de treino dos TRs {sorted(nomes - achados)} na FICHA")
    return novas


def aplica(layout, novas):
    """poe as formulas novas na FICHA do layout. Devolve quantas mudaram."""
    n = 0
    for reg in _aba(layout, "FICHA")["celulas"]:
        if reg[0] in novas and reg[1] != novas[reg[0]]:
            reg[1] = novas[reg[0]]
            n += 1
    return n
