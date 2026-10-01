# -*- coding: utf-8 -*-
"""A limpeza 24: a ficha sai sem a INVOCAÇÃO, o CATÁLOGO e a DADOS_INV.

Decisão do Mizuki em 01/10/2026, quando o construir() estourou os seis minutos do Apps Script: "Pode tirar o catalogo
e invocação, isso vai ganhar tempo e reduzir o codigo, depois implementamos dnv diferente com a att". As três abas
continuam na planilha viva e no layout.json, que é a cópia fiel dela; o que muda é a saída. Elas saem por último,
depois de todas as outras limpezas, porque o GLOSSÁRIO nasce na posição da INVOCAÇÃO e reaproveita os estilos do
CATÁLOGO.

O que NÃO muda: a ficha de invocação separada (ficha-invocacao/, o invocacao.json e os três validadores dela) não
passa por aqui, e segue como estava.
"""
import re

ABAS_FORA = ("INVOCAÇÃO", "CATÁLOGO", "DADOS_INV")


def cita(texto):
    """as abas de ABAS_FORA que uma fórmula ou um menu cita, fora do que está entre aspas"""
    if not isinstance(texto, str):
        return []
    limpo = re.sub(r'"[^"]*"', '""', texto)
    return [n for n in ABAS_FORA if re.search(r"(?:'%s'|(?<![\wÀ-ÿ])%s)!" % (re.escape(n), re.escape(n)), limpo)]


def aplica(layout):
    """tira as três abas do layout e devolve os nomes das que saíram; para se alguma aba que fica ainda citar uma"""
    saem = [a["nome"] for a in layout["abas"] if a["nome"] in ABAS_FORA]
    layout["abas"] = [a for a in layout["abas"] if a["nome"] not in ABAS_FORA]
    orfas = []
    for a in layout["abas"]:
        for cel in a["celulas"]:
            if cel[1] is not None and isinstance(cel[1], str) and cel[1].startswith("=") and cita(cel[1]):
                orfas.append(f"{a['nome']}!{cel[0]} cita {cita(cel[1])}")
        for menu in a.get("menus", []):
            if cita("=" + str(menu.get("formula", ""))):
                orfas.append(f"{a['nome']}!{menu.get('onde')}: o menu cita {cita('=' + str(menu.get('formula', '')))}")
    if orfas:
        raise SystemExit("a ficha ainda depende de uma aba que saiu: " + "; ".join(orfas[:5]))
    return saem
