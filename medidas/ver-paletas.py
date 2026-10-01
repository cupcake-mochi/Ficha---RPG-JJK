# -*- coding: utf-8 -*-
"""Folha de contato das paletas: o topo da CARTEIRA, da FICHA e da FICHA PESSOAL em cada tema, lado a lado.

A troca de paleta só roda no Sheets. O medidas/pintar-paletas.js roda o mesmo convergirPaleta_ num Sheets de mentira
e grava a cor que cada célula, cada imagem e cada barra ficou; este script desenha isso, cinco temas por página, para
alguém olhar tema por tema antes de o Mizuki testar. Nasceu em 01/10/2026, do pedido dele de revisar as 122.

    node medidas/pintar-paletas.js /tmp/p.json
    python3 medidas/ver-paletas.py /tmp/p.json /tmp/paletas            # /tmp/paletas/pagina-01.html ...
    python3 medidas/ver-paletas.py /tmp/p.json /tmp/um "Alfazema · Claro" --zoom 1

Cada página vira imagem com o Firefox sem tela:
    firefox --headless --no-remote --profile <pasta> --window-size L,A --screenshot pagina-01.png file://.../pagina-01.html
"""
import argparse, html, importlib.util, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("ver_aba", os.path.join(AQUI, "ver-aba.py"))
va = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(va)
ix, fp = va.ix, va.fp

# o que entra de cada aba: até que linha, e com os grupos de coluna abertos até que profundidade
RECORTE = [("CARTEIRA", 32, 0), ("FICHA", 38, 0), (fp.NOME, 22, 0)]
# a caixa da paleta nasce no configurarPaleta_ (Codigo.gs), e não está no ABAS: [linha, coluna, última linha, última coluna]
CAIXA = [(26, 3, 26, 9, "PALETA", ["Oswald", 9.0, None, False, "center", "middle", 0, False, False]),
         (27, 3, 28, 13, None, ["Castoro", 15.0, None, False, "center", "middle", 0, False, False]),
         (29, 3, 29, 13, "O tema leva uns 20 segundos. O que faltar termina enquanto você usa a ficha.",
          ["Oswald", 7.0, None, False, "center", "middle", 0, False, False])]


def com_a_caixa(spec, nome):
    spec = json.loads(json.dumps(spec))
    for l1, c1, l2, c2, texto, estilo in CAIXA:
        spec["estilos"].append(estilo)
        spec["vals"] = [t for t in spec["vals"] if not (l1 <= t[0] <= l2 and c1 <= t[1] <= c2)]
        spec["vals"].append([l1, c1, texto or nome, len(spec["estilos"]) - 1])
        spec["merges"].append([l1, c1, l2, c2])
        for lado in ("top", "bottom", "left", "right"):
            spec["bordas"].append([lado, "medium", "#8A7EC4", [f"{ix._letras(c1)}{l1}:{ix._letras(c2)}{l2}"]])
    return spec


def barras_de(aba, valores, crus, G, cheia):
    """a SPARKLINE não existe fora do Sheets: a barra é desenhada pela conta dela. `cheia` é a cor da barra cheia."""
    b = {}
    if aba == fp.NOME:
        m = re.match(r"([\d.,]+) de (\d+)", str(valores.get(ix._lc(G["carga"]), "")))
        if m:
            carga, limite = float(m.group(1).replace(",", ".")), float(m.group(2))
            b[ix._lc(G["carga_barra"])] = (min(100, round(100 * carga / limite)), "#C2334D" if carga > limite else cheia)
    else:
        n = 0
        for (r, c), v in sorted(crus.items()):
            if isinstance(v, str) and "SPARKLINE" in v:
                b[(r, c)] = ((100, 72, 100)[n % 3], cheia)
                n += 1
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pintura")
    ap.add_argument("saida")
    ap.add_argument("nomes", nargs="*")
    ap.add_argument("--zoom", type=float, default=0.4)
    ap.add_argument("--por-pagina", type=int, default=5)
    ap.add_argument("--colunas", type=int, default=1, help="quantos temas por fila da página")
    ap.add_argument("--barra", help="desenha a barra cheia noutra cor, para comparar: um papel do tema (bloco, texto...) ou um hex")
    ap.add_argument("--rotulo", default="", help="texto a mais no título de cada tema")
    ap.add_argument("--recorte", help='o que entra de cada aba, e até que linha: "CARTEIRA:32,FICHA:38"')
    a = ap.parse_args()
    tudo = json.load(open(a.pintura, encoding="utf-8"))
    recorte = [(x.split(":")[0], int(x.split(":")[1]), 0) for x in a.recorte.split(",")] if a.recorte else RECORTE
    nomes = a.nomes or list(tudo)
    CAT = json.load(open(os.path.join(va.RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    R = fp.regras(CAT); G = fp.geometria(R)
    lido, cru = va.recalculada(lambda wb: va.exemplo(wb, R, G))
    specs = {s["nome"]: s for s in va.abas_do_script()}
    arte = va.arte_do_script()
    dados = {}
    for aba, _, _ in recorte:
        dados[aba] = ({(c.row, c.column): c.value for l in lido[aba].iter_rows() for c in l if c.value is not None},
                      {(c.row, c.column): c.value for l in cru[aba].iter_rows() for c in l if c.value is not None})
    os.makedirs(a.saida, exist_ok=True)
    z = a.zoom
    paginas = [nomes[i:i + a.por_pagina] for i in range(0, len(nomes), a.por_pagina)]
    for n, grupo in enumerate(paginas, 1):
        corpo, alts, larg_total = [], [], 0
        for nome in grupo:
            p = tudo[nome]
            cheia = (p["abas"].get("DADOS", {}).get("valores") or {}).get("barra") or "#E8DCD4"
            if a.barra:
                cheia = a.barra if a.barra.startswith("#") else p["papeis"][a.barra]
            paineis, alt, larg = [], 0, 0
            for aba, linhas, aberto in recorte:
                spec = com_a_caixa(specs[aba], nome) if aba == "CARTEIRA" else specs[aba]
                valores, crus = dados[aba]
                if aba == "CARTEIRA":
                    valores = dict(valores)
                    valores.update({(l1, c1): texto or nome for l1, c1, _, _, texto, _ in CAIXA})
                g = va.grade(spec, valores, crus, aberto, barras_de(aba, valores, crus, G, cheia), p["abas"][aba], linhas, arte)
                w = int(re.search(r";width:(\d+)px", g).group(1))
                h = sum(int(spec["alturas"].get(str(r), 21)) for r in range(1, linhas + 1))
                paineis.append(f'<div style="width:{w * z:.0f}px;height:{h * z:.0f}px;overflow:hidden">'
                               f'<div style="transform:scale({z});transform-origin:0 0;width:{w}px">{g}</div></div>')
                alt, larg = max(alt, h * z), larg + w * z + 8
            pp = p["papeis"]
            amostra = "".join(f'<i title="{k}" style="background:{pp[k]}"></i>' for k in
                              ("fundo", "painel", "painel_alto", "menu_grande", "regua", "acento", "bloco", "linha", "texto_fraco", "texto", "tinta"))
            corpo.append(f'<section><h2>{html.escape(nome + a.rotulo)} <span class="am">{amostra}</span></h2><div class="fila">{"".join(paineis)}</div></section>')
            alts.append(alt + 34)
            larg_total = max(larg_total, larg)
        filas = [alts[i:i + a.colunas] for i in range(0, len(alts), a.colunas)]
        alt_total = sum(max(f) for f in filas)
        larg_total = larg_total * a.colunas
        css = ("<style>body{background:#777;font:13px sans-serif;display:flex;flex-wrap:wrap;align-content:flex-start}section{margin:0 0 6px}h2{margin:0;padding:3px 6px;font:bold 15px sans-serif;"
               "color:#fff;background:#222;height:22px}.fila{display:flex;gap:8px;background:#777}"
               ".am i{display:inline-block;width:22px;height:14px;border:1px solid #fff;margin-left:2px}</style>")
        arq = os.path.join(a.saida, f"pagina-{n:02d}.html")
        open(arq, "w", encoding="utf-8").write(va.pagina(css + "".join(corpo), f"paletas {n}", "#777"))
        print(f"{arq}\t{int(larg_total) + 4}\t{int(alt_total) + 8}\t{' | '.join(grupo)}")


if __name__ == "__main__":
    main()
