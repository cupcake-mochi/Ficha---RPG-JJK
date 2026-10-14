# -*- coding: utf-8 -*-
"""O painel retrátil da Origem, à direita da FICHA (14/10/2026, B46).

O Mizuki, depois do estudo das Origens (mockup/origens-estudo.html): "acredito que por no 'Ficha', uma aba retratil a
direita com tudo que a origem tá oferecendo, tbm seria ideal, os legados mesmo"; e, na segunda rodada, a forma B "mas n
vejo o porque mostrar tudo, só mostrar as escolhas que o jogador fez mesmo, n? dos legados e habilidades menores e
maiores". O painel mostra o que está escrito no dossiê da FICHA PESSOAL: a marcante (com o Talento de Categoria de Efeito
4, na Restrição corporal), as duas menores e os Legados de história, cada uma com o nome, a frequência e o texto.

O desenho: três colunas depois da AU, num grupo que nasce fechado (o + fica em cima da coluna AU, como o painel de XP da
FICHA PESSOAL): uma de respiro, a do painel e a margem. A faixa de título e, embaixo, uma caixa só, mesclada até a linha
antes do primeiro grupo de linhas da FICHA (as Habilidades), com o texto inteiro numa fórmula. Uma caixa só, e não uma
por capacidade, porque as linhas da FICHA são as da folha inteira: o painel não pode esticar uma linha sem esticar a
FICHA junto, e o espaço tem de caber no pior caso do livro, que muda de Origem para Origem (a marcante mais comprida é a
da Sem Energia, a menor mais comprida é do Corpo Amaldiçoado). A conta do pior caso é feita aqui, com a medida das
cartas de Habilidades, e a montagem para se não couber.

O cabeçalho da FICHA continua por cima do painel, como na FICHA PESSOAL. As cores são as de fábrica (a troca de paleta
acha o papel de cada célula pela cor).
"""
import json, os
import indice_ficha as ix
import cabecalho as cab
import ficha_pessoal as fp

ABA = "FICHA"
PX_RESPIRO, PX_PAINEL, PX_MARGEM = 14, 720, 14
LINHA_DO_TITULO = 9
TITULO = "SUA ORIGEM · O QUE VOCÊ ESCOLHEU"
NOTA = ("O que está escrito no dossiê da FICHA PESSOAL: a marcante, as duas menores e os Legados de história. Para "
        "mudar, mexa lá. Abra e feche o painel pelo + em cima da coluna da margem.")
CE4 = "Talento de Categoria de Efeito 4"


def _estilo(layout, nome):
    novo = json.loads(json.dumps(fp.ESTILOS[nome]))
    chave = json.dumps(novo, ensure_ascii=False, sort_keys=True)
    for i, e in enumerate(layout["estilos"]):
        if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave:
            return i
    layout["estilos"].append(novo)
    return len(layout["estilos"]) - 1


def pior_caso(OL=None):
    """o texto mais comprido que o painel pode ter com as capacidades do livro: em cada Origem, a marcante mais comprida
    e as duas menores mais compridas dela"""
    OL = OL or json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "origens-do-livro.json"), encoding="utf-8"))
    out = ""
    for o in OL["origens"]:
        m = max(o["marcantes"], key=lambda c: len(c["texto"]))
        n = sorted(o["menores"], key=lambda c: -len(c["texto"]))[:2]
        t = "\n\n".join(f"MARCANTE · {c['nome']} · {c['freq']}\n{c['texto']}" for c in [m] + n)
        if len(t) > len(out):
            out = t
    return out


def trocas(layout, fp_tr):
    ficha = ix._aba(layout, ABA)
    idx = ix.indice(layout)
    G = fp_tr["G"]
    c0 = ficha["colunas"] + 1                       # o respiro; o painel é a seguinte, e a margem a outra
    cp, cm = c0 + 1, c0 + 2
    grupos_l = (ficha.get("grupos") or {}).get("linhas", [])
    limite = (min(g[0] for g in grupos_l) if grupos_l else ficha["linhas"]) - 2
    alturas = {l: h for l, h in ficha["linhas_alt"]}
    px = lambda l: (alturas.get(l) or ficha.get("altura_padrao") or 15.75) * 4 / 3
    # o pior caso do livro tem de caber na caixa: a medida das cartas de Habilidades, na largura do painel
    import habilidades as hb
    M = dict(hb.medida(), largura=PX_PAINEL - hb.RESPIRO_PX)
    pede = hb.linhas_na_carta(pior_caso(), M) * M["linha"] + M["respiro"]
    tem = sum(px(l) for l in range(LINHA_DO_TITULO + 1, limite + 1))
    if pede > tem:
        raise SystemExit(f"painel_origem: o texto mais comprido do livro pede {pede} px, e a caixa tem {tem:.0f}")
    cel = {}
    # o cabeçalho da FICHA continua por cima do painel (a faixa de tinta e a divisória), como na FICHA PESSOAL
    fcel = {r[0]: r for r in ficha["celulas"]}
    meio = ix._lc("AD1")[1]
    for lin in range(1, cab.ULTIMA_LINHA + 1):
        molde = fcel.get(f"{ix._letras(meio)}{lin}")
        for col in (c0, cp, cm):
            cel[f"{ix._letras(col)}{lin}"] = [None, molde[2] if molde else None]
    P = ix._letras(cp)
    cel[f"{P}{LINHA_DO_TITULO}"] = [TITULO, _estilo(layout, "faixa")]
    E_txt = _estilo(layout, "txt")
    for lin in range(LINHA_DO_TITULO + 1, limite + 1):
        cel[f"{P}{lin}"] = [None, E_txt]

    # o texto: cada capacidade com o rótulo, o nome e a frequência (os do espelho embaixo das barras) e o texto do dossiê
    partes = []
    for k, (campo, rot, _) in enumerate(fp.CAPS):
        l_, c_ = ix._lc(idx[campo])
        txt = fp._A(G["cap_texto"][k], fp.FP)
        bloco = (f'"{rot} · "&${ix._letras(c_)}${l_}&IF(${ix._letras(c_)}${l_ + 1}="",""," · "&${ix._letras(c_)}${l_ + 1})&CHAR(10)&'
                 f'IF({txt}="","(o texto é escrito na FICHA PESSOAL)",{txt})')
        if campo == "marcante":
            ce4 = fp._A(G["ce4"], fp.FP)
            bloco += f'&IF({ce4}="","",CHAR(10)&CHAR(10)&"{CE4}: "&{ce4})'
        partes.append(bloco)
    leg = fp._A(G["legados"], fp.FP)
    partes.append(f'"LEGADOS DE HISTÓRIA"&CHAR(10)&IF({leg}="","(nenhum escrito)",{leg})')
    cel[f"{P}{LINHA_DO_TITULO + 1}"][0] = "=" + "&CHAR(10)&CHAR(10)&".join(partes)
    return {"celulas": cel, "mescla": f"{P}{LINHA_DO_TITULO + 1}:{P}{limite}", "colunas": (c0, cp, cm),
            "limite": limite, "pede": pede, "tem": tem, "nota": {f"{P}{LINHA_DO_TITULO}": NOTA}}


def aplica(layout, tr):
    ficha = ix._aba(layout, ABA)
    por = {c[0]: c for c in ficha["celulas"]}
    n = 0
    for coord, (valor, estilo) in tr["celulas"].items():
        if coord in por:
            por[coord][1], por[coord][2] = valor, estilo
        else:
            ficha["celulas"].append([coord, valor, estilo])
        n += 1
    ficha["mescladas"].append(tr["mescla"])
    c0, cp, cm = tr["colunas"]
    ficha["colunas"] = cm
    ficha["colunas_larg"] = ficha["colunas_larg"] + [[c0, c0, (PX_RESPIRO + 1) / 8], [cp, cp, (PX_PAINEL + 1) / 8],
                                                     [cm, cm, (PX_MARGEM + 1) / 8]]
    g = ficha.setdefault("grupos", {})
    g.setdefault("linhas", [])
    g["colunas"] = g.get("colunas", []) + [[c0, cm, True]]
    ficha["notas"] = dict(ficha.get("notas") or {}, **tr["nota"])
    return n
