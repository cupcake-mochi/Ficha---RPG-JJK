# -*- coding: utf-8 -*-
"""Abre linhas no meio da FICHA (08/10/2026, o B41).

As seções 1 a 6 da FICHA vêm da planilha exportada (o layout.json), e tudo o que as limpezas acrescentaram até aqui
entrou no fim da aba (as Habilidades, o menu rápido) ou em lugar que já existia. O B41 pede caixas novas EMBAIXO DAS
BARRAS de vida, energia e integridade, que é o meio da aba: as linhas de baixo têm de descer.

Este módulo faz isso antes de qualquer limpeza, logo depois de o layout.json ser lido: abre `N_LINHAS` linhas depois
da linha em branco que vem embaixo da faixa do estágio de Integridade, e desloca tudo o que aponta para baixo dali:

  · as células, as mesclagens, os menus, as regras de cor, as alturas de linha e a âncora das imagens da FICHA;
  · as fórmulas da própria FICHA e as das outras abas que citam a FICHA (a CARTEIRA e o índice da DADOS);
  · as coordenadas da FICHA guardadas no `_meta` (as barras cheias, o estado vazio).

Depois disso a planilha é, para as limpezas, uma exportação que já tinha as linhas: elas acham as caixas pelo rótulo
e pelo índice da DADOS, e não por endereço escrito. As linhas novas nascem em branco, com o estilo da linha em branco
de cima (a moldura e o miolo continuam), e quem as preenche é o `estado_do_personagem.py`.

O `comparar-ficha-01.py` usa o mesmo mapa (`linha_nova`, `desloca_formula`) para comparar a exportação com a ficha
gerada: a linha 39 da exportação é a 50 da gerada.
"""
import re

ABA = "FICHA"
N_LINHAS = 11                # as linhas que abrem: ver estado_do_personagem.py (eram 8 até o descanso, B43)
MARCA_DO_ESTAGIO = "Estágio 4"

_REF = re.compile(r"(?P<aba>(?:'[^']+'|[A-Za-zÀ-ÿ_][\wÀ-ÿ.]*)!)?(?<![A-Za-zÀ-ÿ_\d.$])(?P<c1>\$?[A-Z]{1,3})(?P<l1>\$?)(?P<r1>\d+)"
                  r"(?::(?P<c2>\$?[A-Z]{1,3})(?P<l2>\$?)(?P<r2>\d+))?(?![\w(])")
_COORD = re.compile(r"^(\$?)([A-Z]{1,3})(\$?)(\d+)$")


def depois_de(layout):
    """a linha depois da qual as novas abrem: a linha em branco embaixo da faixa do estágio de Integridade"""
    aba = next(a for a in layout["abas"] if a["nome"] == ABA)
    achadas = [c[0] for c in aba["celulas"] if isinstance(c[1], str) and c[1].startswith("=") and MARCA_DO_ESTAGIO in c[1]]
    if len(achadas) != 1:
        raise SystemExit(f"linhas_novas: a faixa do estagio de Integridade devia ser uma celula so, e achei {achadas}")
    lin = int(_COORD.match(achadas[0]).group(4)) + 1
    ocupada = [c[0] for c in aba["celulas"] if int(_COORD.match(c[0]).group(4)) == lin and c[1] not in (None, "")]
    if ocupada:
        raise SystemExit(f"linhas_novas: a linha {lin} da FICHA devia estar em branco, e tem {ocupada}")
    return lin


def linha_nova(lin, depois, n=N_LINHAS):
    """para onde vai a linha `lin` da exportação"""
    return lin + n if lin > depois else lin


def _coord(c, depois, n):
    m = _COORD.match(c)
    return f"{m.group(1)}{m.group(2)}{m.group(3)}{linha_nova(int(m.group(4)), depois, n)}"


def _faixa(f, depois, n):
    """uma faixa (A1 ou A1:B2): a ponta que fica abaixo desce; a faixa que atravessa a linha estica"""
    return ":".join(_coord(p, depois, n) for p in f.split(":"))


def desloca_formula(f, na_propria_aba, depois, n=N_LINHAS):
    """a fórmula com as referências à FICHA levadas para baixo. O que está entre aspas duplas fica como está."""
    if not isinstance(f, str) or not f.startswith("="):
        return f

    def troca(m):
        aba = m.group("aba")
        if aba is None:
            if not na_propria_aba:
                return m.group(0)
        elif aba.strip("!").strip("'") != ABA:
            return m.group(0)
        out = (aba or "") + m.group("c1") + m.group("l1") + str(linha_nova(int(m.group("r1")), depois, n))
        if m.group("c2"):
            out += ":" + m.group("c2") + m.group("l2") + str(linha_nova(int(m.group("r2")), depois, n))
        return out

    pedacos = re.split(r'("(?:[^"]|"")*")', f)
    return "".join(p if i % 2 else _REF.sub(troca, p) for i, p in enumerate(pedacos))


def insere(layout, n=N_LINHAS):
    """abre as linhas no layout, no lugar. Devolve {"depois": a linha de cima, "n": quantas, "linhas": as que abriram}"""
    depois = depois_de(layout)
    for aba in layout["abas"]:
        propria = aba["nome"] == ABA
        if propria:
            molde = [c for c in aba["celulas"] if int(_COORD.match(c[0]).group(4)) == depois]
            for c in aba["celulas"]:
                c[0] = _coord(c[0], depois, n)
            for k in range(1, n + 1):
                for c in molde:
                    m = _COORD.match(c[0])
                    aba["celulas"].append([f"{m.group(2)}{depois + k}", None, c[2]])
            aba["mescladas"] = [_faixa(x, depois, n) for x in aba["mescladas"]]
            aba["linhas_alt"] = [[linha_nova(l, depois, n), h] for l, h in aba["linhas_alt"]]
            for im in aba.get("imagens") or []:
                im["lin"] = linha_nova(im["lin"], depois, n)
            aba["linhas"] += n
        for c in aba["celulas"]:
            c[1] = desloca_formula(c[1], propria, depois, n)
        for mn in aba.get("menus") or []:
            if propria:
                mn["onde"] = " ".join(_faixa(x, depois, n) for x in mn["onde"].split())
            if isinstance(mn.get("formula"), str):
                mn["formula"] = desloca_formula("=" + mn["formula"], propria, depois, n)[1:] if not mn["formula"].startswith('"') else mn["formula"]
        for rc in aba.get("condicional") or []:
            if propria:
                rc["onde"] = " ".join(_faixa(x, depois, n) for x in rc["onde"].split())
            rc["formula"] = [desloca_formula("=" + x, propria, depois, n)[1:] if isinstance(x, str) else x for x in rc.get("formula") or []]
    for chave, v in layout.get("_meta", {}).items():
        if isinstance(v, dict) and isinstance(v.get(ABA), dict):
            v[ABA] = {(_coord(k, depois, n) if _COORD.match(k) else k): x for k, x in v[ABA].items()}
    return {"depois": depois, "n": n, "linhas": list(range(depois + 1, depois + n + 1))}


def carrega(caminho=None):
    """o layout.json como o monta.py o usa daqui para a frente: com as linhas abertas e as caixas do estado do
    personagem nelas. Para quem lê a exportação por conta própria (os validadores) e precisa dos mesmos endereços."""
    import json, os
    import estado_do_personagem
    caminho = caminho or os.path.join(os.path.dirname(os.path.abspath(__file__)), "layout.json")
    layout = json.load(open(caminho, encoding="utf-8"))
    estado_do_personagem.aplica(layout, estado_do_personagem.trocas(layout, insere(layout)))
    return layout
