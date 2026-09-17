# -*- coding: utf-8 -*-
"""O indice que a FICHA publica na DADOS, com o endereco em FORMULA. E a limpeza 11.

Colunas BA e BB da DADOS: o nome do campo e a celula dele. O Codigo.gs, o regressao-kaori-na-ficha.py,
o conferir-ficha-xlsx.py e as limpezas do monta.py leem por ele, e nenhum deles guarda endereco.

Ate 16/09/2026 a celula era TEXTO ("D40"). Em 17/09/2026 o Mizuki inseriu linhas na FICHA pelo
Sheets, e texto nao anda: o indice inteiro ficou apontando para o lugar antigo -- a vida para D23
com ela em D26, a Defesa para D40 com ela em D43 --, e a caixinha de mais-ou-menos parou. Agora cada
endereco e `=ADDRESS(ROW(FICHA!D26),COLUMN(FICHA!D26),4)`, que devolve "D26" e anda sozinho quando
a planilha muda de forma.

Nenhum endereco esta escrito aqui: cada campo sai do rotulo impresso na FICHA. A mesma derivacao,
rodada no layout de antes das linhas novas, reproduz o indice de texto que ele tinha.
"""
import re, unicodedata

FORMULA = "=ADDRESS(ROW(FICHA!{c}),COLUMN(FICHA!{c}),4)"
_RX_FORMULA = re.compile(r"FICHA!\$?([A-Z]+)\$?(\d+)")


def endereco(valor):
    """"D26" de "D26" ou da formula ADDRESS; None se nao for nenhum dos dois"""
    if not isinstance(valor, str):
        return None
    if re.fullmatch(r"[A-Z]+\d+", valor):
        return valor
    m = _RX_FORMULA.search(valor) if valor.startswith("=") else None
    return m.group(1) + m.group(2) if m else None


def _norm(s):
    s = unicodedata.normalize("NFD", s.strip().lower())
    return " ".join("".join(ch for ch in s if unicodedata.category(ch) != "Mn").split())


def _col(letras):
    n = 0
    for ch in letras:
        n = n * 26 + ord(ch) - 64
    return n


def _letras(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _lc(coord):
    m = re.match(r"^([A-Z]+)(\d+)$", coord)
    return int(m.group(2)), _col(m.group(1))


def _aba(layout, nome):
    return next(a for a in layout["abas"] if a["nome"] == nome)


class _Ficha:
    def __init__(self, layout):
        a = _aba(layout, "FICHA")
        self.val = {r[0]: r[1] for r in a["celulas"] if r[1] is not None}
        self.merges = {}
        for m in a["mescladas"]:
            ini, fim = m.split(":")
            self.merges[ini] = fim
        self.exato, self.pos = {}, {}
        for c, v in self.val.items():
            if isinstance(v, str) and not v.startswith("="):
                self.exato.setdefault(v.strip(), []).append(c)
                self.pos.setdefault(_norm(v), []).append(c)

    def rotulos(self, texto):
        """o rotulo escrito igual; se nao houver, o mesmo sem acento e sem caixa -- e assim que
        "Péricias Dispóniveis" responde por "Perícias Disponíveis" """
        return sorted(self.exato.get(texto) or self.pos.get(_norm(texto), []), key=_lc)

    def abaixo(self, coord):
        """a primeira celula abaixo do fim da mesclagem do rotulo, na mesma coluna"""
        fim = self.merges.get(coord, coord)
        lin, col = _lc(fim)
        return f"{_letras(_lc(coord)[1])}{lin + 1}"

    def acima(self, coord):
        lin, col = _lc(coord)
        alvo = lin - 1
        for ini, fim in self.merges.items():
            li, ci = _lc(ini)
            lf, cf = _lc(fim)
            if li <= alvo <= lf and ci <= col <= cf:
                return ini
        return f"{_letras(col)}{alvo}"

    def unico(self, texto, filtro=None):
        cs = [c for c in self.rotulos(texto) if filtro is None or filtro(c)]
        if len(cs) != 1:
            raise SystemExit(f"o rotulo {texto!r} aparece {len(cs)} vez(es) na FICHA: {cs}")
        return cs[0]

    def formula_com(self, trecho):
        cs = sorted((c for c, v in self.val.items() if isinstance(v, str) and v.startswith("=") and trecho in v),
                    key=_lc)
        if len(cs) != 1:
            raise SystemExit(f"esperava uma formula com {trecho!r} na FICHA, achei {cs}")
        return cs[0]


ATRS = [("Força", "FOR", "FOR"), ("Destreza", "DES", "DEX"), ("Constituição", "CON", "CON"),
        ("Inteligência", "INT", "INT"), ("Essência", "ESS", "ESS")]


def enderecos(layout):
    """{campo: celula} de todo campo que a FICHA tem, na ordem em que o indice publica"""
    f = _Ficha(layout)
    out = {}
    out["nome"] = min((c for c, v in f.val.items() if isinstance(v, str) and "CARTEIRA!" in v and _lc(c)[0] <= 5),
                      key=_lc)
    for campo, rot in (("caminho", "CAMINHO"), ("trilha", "TRILHA"), ("origem", "ORIGEM"),
                       ("nivel", "NÍVEL"), ("xp", "XP")):
        out[campo] = f.abaixo(f.unico(rot))
    lin_des = _lc(f.unico("DES"))[0]                                   # a linha dos cinco atributos
    tem_corpo = bool(f.rotulos("DEX"))
    for nome, rot, rot_corpo in ATRS:
        r = f.unico(rot, lambda c: _lc(c)[0] == lin_des)
        out["atr_" + nome] = f.abaixo(r)
    for nome, rot, rot_corpo in ATRS:
        if tem_corpo:
            grande = out["atr_" + nome]
            out["atr_base_" + nome] = f.abaixo(grande)
    for tipo, rot in (("vida", "VIDA - Atual/Máxima"), ("energia", "ENERGIA - Atual/Máxima"),
                      ("integridade", "INTEGRIDADE - Atual/Máxima")):
        r = f.unico(rot)
        lin = _lc(r)[0]
        atual = f.abaixo(r)
        la, ca = _lc(atual)
        maxima = min((c for c, v in f.val.items() if _lc(c)[0] == la and _lc(c)[1] > ca
                      and isinstance(v, str) and v.startswith("=") and "SPARKLINE" not in v), key=_lc)
        out[tipo] = atual
        out[tipo + "_max"] = maxima
        out[tipo + "_temp"] = f.abaixo(f.unico("TEMPORÁRIO", lambda c: _lc(c)[0] == lin))
        out[tipo + "_delta"] = f.abaixo(f.unico("± PERDA &/ou GANHO", lambda c: _lc(c)[0] == lin))
    out["estagio_alma"] = f.formula_com("Estágio 4")
    for campo, rot in (("defesa", "DEFESA"), ("proteção", "PROTEÇÃO"), ("equipamento", "EQUIPAMENTO"),
                       ("iniciativa", "INICIATIVA"), ("cd de feitiço", "CD DE FEITIÇO"),
                       ("conjuração", "CONJURAÇÃO"), ("corpo a corpo", "CORPO A CORPO"),
                       ("à distância", "À DISTÂNCIA"), ("maestria", "MAESTRIA"),
                       ("deslocamento", "DESLOCAMENTO"), ("espaços de feitiço", "ESPAÇOS DE FEITIÇO"),
                       ("refino de graça", "REFINO DE GRAÇA"), ("classe máxima", "CLASSE MÁXIMA"),
                       ("classe 0 grátis", "CLASSE 0")):
        out[campo] = f.abaixo(f.unico(rot))
    # o que entrou em 16 e 17/09/2026; em layout mais velho, cada um so entra se o rotulo existir
    if f.rotulos("REFINO ESCOLHIDO"):
        out["refino escolhido"] = f.abaixo(f.unico("REFINO ESCOLHIDO"))
    if f.rotulos("Marco Escolhido"):
        lin = _lc(f.unico("Marco Escolhido"))[0]
        na_linha = lambda c: _lc(c)[0] == lin
        # 17/09/2026: Atributo e Feitiço viraram Corpo e Leque, que e o nome do livro
        out["refino escolhido"] = f.abaixo(f.unico("Refino", na_linha))
        out["marco corpo"] = f.abaixo(f.unico("Corpo" if [c for c in f.rotulos("Corpo") if na_linha(c)] else "Atributo", na_linha))
        out["marco leque"] = f.abaixo(f.unico("Leque" if [c for c in f.rotulos("Leque") if na_linha(c)] else "Feitiço", na_linha))
        out["marcos escolhidos"] = f.abaixo(f.unico("Marco Escolhido"))
    # cada Buff/Debuff e da caixa que fica logo a esquerda dele, na mesma linha
    buffs = f.rotulos("Buff/Debuff")
    if len(buffs) == 1 and not f.rotulos("DEFESA") == []:
        out["buff de defesa"] = f.abaixo(buffs[0])
    elif buffs:
        for b in buffs:
            lb, cb = _lc(b)
            dono = max((c for c, v in f.val.items() if _lc(c)[0] == lb and _lc(c)[1] < cb and isinstance(v, str)
                        and not v.startswith("=") and v.strip() and v.strip() != "Buff/Debuff"), key=lambda c: _lc(c)[1])
            out["buff de " + f.val[dono].strip().lower()] = f.abaixo(b)
    if tem_corpo:
        lin_dex = _lc(f.unico("DEX"))[0]
        for nome, rot, rot_corpo in ATRS:
            out["corpo_" + nome] = f.acima(f.unico(rot_corpo, lambda c: _lc(c)[0] == lin_dex))
        # o cabecalho e texto na planilha desenhada, e formula depois que a limpeza 12 escreve a conta nele
        cab = [c for c, v in f.val.items() if isinstance(v, str) and _norm(v.lstrip('="')).startswith("pontos de marco de corpo")]
        out["pontos de corpo"] = cab[0]
        out["pontos disponíveis"] = f.abaixo(f.unico("Pontos Disponíveis"))
    for campo, rot in (("perícias disponíveis", "Perícias Disponíveis"), ("ofícios disponíveis", "Ofícios Disponíveis"),
                       ("testes disponíveis", "Testes de Resistência Disponíveis")):
        if f.rotulos(rot):
            out[campo] = f.abaixo(f.unico(rot))
    # a caixa que apresenta as escolhas de perícia e ofício: o texto que o Mizuki deixou nela, ou a formula
    # que a limpeza 12 escreve, que sempre termina em "Tudo escolhido"
    esc = [c for c, v in f.val.items() if isinstance(v, str) and
           (_norm(v).startswith("escolha uma pericia") or (v.startswith("=") and '"Tudo escolhido"' in v))]
    if len(esc) == 1:
        out["escolhas de perícia"] = esc[0]
    cabecalhos = [("feitiços disponíveis", "Feitiços - Disponível"), ("passivas", '"Passivas - Regras"')]
    for campo, trecho in cabecalhos:
        cs = [c for c, v in f.val.items() if isinstance(v, str) and v.startswith("=") and trecho in v]
        if len(cs) == 1:
            out[campo] = cs[0]
    # as duas primeiras linhas da lista de aptidões, que vem com as de graça
    apt = [c for c, v in f.val.items() if isinstance(v, str) and v.startswith("=") and ("Refino Atual" in v)]
    if len(apt) == 1:
        la, ca = _lc(apt[0])
        abaixo = sorted(_lc(m)[0] for m in f.merges if _lc(m)[1] == ca and _lc(m)[0] > la + 1)
        if len(abaixo) >= 2:
            out["aptidão de graça 1"] = f"{_letras(ca)}{abaixo[0]}"
            out["aptidão de graça 2"] = f"{_letras(ca)}{abaixo[1]}"
    return out


def trocas(layout, textos_corrigidos=None):
    """{"DADOS": {celula: (valor, celula_do_estilo)}}: o indice inteiro reescrito em formula, na ordem de
    enderecos(), a partir da linha do cabecalho `campo`."""
    dados = _aba(layout, "DADOS")
    dcel = {r[0]: r for r in dados["celulas"]}
    cab = next(r[0] for r in dados["celulas"] if r[0].startswith("BA") and r[1] == "campo")
    lin0 = _lc(cab)[0]
    velho_fim = max(_lc(r[0])[0] for r in dados["celulas"] if r[0].startswith("BA") and r[1])
    end = enderecos(layout)
    cel = {}
    for i, (campo, coord) in enumerate(end.items(), start=1):
        cel[f"BA{lin0 + i}"] = (campo, f"BA{lin0 + 1}")
        cel[f"BB{lin0 + i}"] = (FORMULA.format(c=coord), f"BB{lin0 + 1}")
    for lin in range(lin0 + len(end) + 1, velho_fim + 1):              # linha que sobrou de indice menor
        cel[f"BA{lin}"] = (None, f"BA{velho_fim + 1}")
        cel[f"BB{lin}"] = (None, f"BB{velho_fim + 1}")
    return {"DADOS": cel}


def aplica(layout, tr):
    n = 0
    for nome, cels in tr.items():
        aba = _aba(layout, nome)
        por = {r[0]: r for r in aba["celulas"]}
        for coord, (valor, ref) in cels.items():
            estilo = por[ref][2] if ref in por else None
            if coord in por:
                reg = por[coord]
                if reg[1] != valor or reg[2] != estilo:
                    reg[1], reg[2] = valor, estilo
                    n += 1
            else:
                aba["celulas"].append([coord, valor, estilo])
                n += 1
    return n


def indice(layout):
    """{campo: celula} lido das colunas BA e BB da DADOS do layout, com texto ou formula"""
    cel = {reg[0]: reg[1] for reg in _aba(layout, "DADOS")["celulas"]}
    out = {}
    for k, v in cel.items():
        if k.startswith("BA") and k[2:].isdigit() and v and v != "campo":
            e = endereco(cel.get("BB" + k[2:]))
            if e:
                out[v] = e
    return out
