# -*- coding: utf-8 -*-
"""Compara a ficha que o ficha-v01/monta.py gera com o .xlsx que o Mizuki mandou.

Celula por celula: valor, formula, fonte, preenchimento, borda, alinhamento e
formato de numero. Mais as mesclagens, as larguras, as alturas, os menus, a
condicional, as imagens e a ordem das abas.

As diferencas ESPERADAS sao as tres limpezas declaradas no layout.json, e so
elas. Qualquer outra e defeito do gerador.
"""
import json, os, re, sys
from collections import Counter
from openpyxl import load_workbook
from openpyxl.worksheet.formula import ArrayFormula

AQUI = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(AQUI, "ficha-v01", "original.xlsx")
B = os.path.join(AQUI, "ficha-v01", "ficha-projeto-m-0.1.xlsx")
LAY = json.load(open(os.path.join(AQUI, "ficha-v01", "layout.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(AQUI, "ficha-v01"))
import dados_catalogo
DADOS_CAT = dados_catalogo.valores()
# as limpezas leem o indice da DADOS, e desde 17/09/2026 ele e reescrito em formula antes delas (limpeza
# 11). O comparador refaz a mesma ordem numa copia do layout, para ler o que o monta.py leu.
import copy, indice_ficha, ficha_layout, correcoes_texto
LAY_FL = copy.deepcopy(LAY)
FL = ficha_layout.trocas(LAY_FL)
ficha_layout.aplica(LAY_FL, FL)
# a testemunha de cada estilo: uma celula que tem aquele estilo e que nenhuma limpeza de desenho mexeu
_MEXIDAS = {(n, c) for n, cs in FL["celulas"].items() for c in cs}
TESTEMUNHA = {}
for _a in LAY["abas"]:
    for _r in _a["celulas"]:
        if _r[2] is not None and (_a["nome"], _r[0]) not in _MEXIDAS:
            TESTEMUNHA.setdefault(_r[2], (_a["nome"], _r[0]))
IX = indice_ficha.trocas(LAY_FL)
LAY_IX = copy.deepcopy(LAY_FL)
indice_ficha.aplica(LAY_IX, IX)
import tr_treinado
TR_NOVAS = tr_treinado.trocas(LAY_IX)
import defesa_equipamento
DE = defesa_equipamento.trocas(LAY_IX)
LAY_DE = copy.deepcopy(LAY_IX)
defesa_equipamento.aplica(LAY_DE, DE)
import ficha_automatica
FA = ficha_automatica.trocas(LAY_DE)
# 19/09/2026: as celulas onde o gerador poe a divisoria entre a moldura e o miolo. Precisa do layout depois de
# TODAS as limpezas de cima (a ficha automatica mexe nas linhas da FICHA), como o monta.py o tem na hora.
import correcoes_borda
LAY_FA2 = copy.deepcopy(LAY_DE)
ficha_automatica.aplica(LAY_FA2, FA)
DIVISORIA = correcoes_borda.celulas_da_divisoria(LAY_FA2)
DIVISORIA_TRACO = ["medium", "FF8A7EC4"]

for f in (A, B):
    if not os.path.exists(f):
        sys.exit(f"falta {f}. Rode extrair.py e monta.py primeiro.")

wa, wb_ = load_workbook(A), load_workbook(B)
BARRAS = LAY["_meta"].get("barras_cheias", {})
VAZIO = LAY["_meta"].get("estado_vazio", {})
ARIAL = LAY["_meta"].get("arial_vira_corpo")
CARIMBO = LAY["_meta"].get("carimbo_texto", {})
difs, esperadas = [], Counter()
# A Origem que a personagem exportada tinha. O molde nasce com "Latente" (o desenho da mesa, ficha_layout.py).
# A celula sai do rotulo ORIGEM da FICHA (o valor mora logo embaixo), e nao de um endereco escrito aqui: em
# 17/09/2026 o Mizuki inseriu linhas pelo Sheets, e um endereco fixo teria apontado para o lugar antigo.
def _origem_da_ficha(wb):
    achadas = [c for linha in wb["FICHA"].iter_rows() for c in linha
               if isinstance(c.value, str) and c.value.strip().upper() == "ORIGEM"]
    if len(achadas) != 1:
        sys.exit(f"o rotulo ORIGEM devia aparecer uma vez na FICHA de {os.path.basename(A)}, e aparece {len(achadas)}.")
    return achadas[0].offset(row=1).coordinate

ESTADO_DA_PERSONAGEM = {("FICHA", _origem_da_ficha(wa))}

def cor(c):
    if c is None or getattr(c, "rgb", None) in (None, "00000000"):
        return None
    return c.rgb if isinstance(c.rgb, str) else None

def valor_de(cel):
    """O valor comparavel da celula.

    ⚠ Formula MATRICIAL nao se compara direto: o openpyxl devolve um objeto
    ArrayFormula sem __eq__, entao duas identicas saem como diferentes -- e o
    comparador acusava as cinco da aba INVOCACAO como divergencia nao
    explicada, imprimindo dois enderecos de memoria como se fossem valores.
    O que identifica uma matricial e o par (faixa, texto)."""
    v = cel.value
    if isinstance(v, ArrayFormula):
        return ("matricial", v.ref, v.text)
    return v

def perfil(cel):
    f, p, b, al = cel.font, cel.fill, cel.border, cel.alignment
    return {
        "valor": valor_de(cel),
        "fonte": [f.name, f.sz, cor(f.color), bool(f.b), bool(f.i)] if f else None,
        "fundo": cor(p.start_color) if (p and p.fill_type == "solid") else None,
        "borda": {l: [getattr(b, l).style, cor(getattr(b, l).color)]
                  for l in ("top", "bottom", "left", "right")
                  if getattr(b, l) and getattr(b, l).style} if b else {},
        "alinha": [al.horizontal, al.vertical, bool(al.wrap_text),
                   al.text_rotation or 0] if al else None,
        "fmt": cel.number_format,
    }

ESTILO_PADRAO = ("Roboto", 12.0, "F4F1F7")      # a fonte de corpo que o script poe em toda celula
ALINHA_PADRAO = ["left", "center", False, 0]
TINTA = "FF0A0810"

def rgb6(c):
    return c[-6:] if isinstance(c, str) else None

def base_da_aba(s):
    """o fundo que a aba mais usa: o mesmo criterio do emissor pra escolher o fundo de base, que o
    script pinta antes de qualquer coisa e que o gerador, por isso, nao escreve celula a celula."""
    cont = Counter(cor(c.fill.start_color) for linha in s.iter_rows() for c in linha
                   if c.fill and c.fill.fill_type == "solid")
    return cont.most_common(1)[0][0] if cont else None

def eh_vazia_padrao(p, base, gerada):
    """celula vazia, sem borda, na fonte e no alinhamento de corpo, sem fundo ou com o fundo de base.
    A original (exportada do Sheets) escreve isso explicitamente em toda celula da aba; o gerador nao
    escreve, e o script pinta a aba inteira assim antes de tudo -- as duas dizem a mesma coisa."""
    if p["valor"] not in (None, "") or p["borda"] or p["fundo"] not in (None, base):
        return False
    f, a = p["fonte"], p["alinha"]
    if not f or (f[0], f[1], rgb6(f[2])) != ESTILO_PADRAO or f[3] or f[4]:
        return False
    if gerada:                                       # o gerador deixa None onde nao diz nada
        return a in (ALINHA_PADRAO, [None, None, False, 0]) and p["fmt"] == "General"
    return a == ALINHA_PADRAO and p["fmt"] == "General"

def eh_ruido_de_fabrica(pa, pb):
    """a limpeza 1: Arial 10 preto em celula VAZIA, e so isso."""
    if pa["valor"] is not None or pb["valor"] is not None:
        return False
    fa, fb = pa["fonte"], pb["fonte"]
    if not fa or fa[0] != "Arial" or fa[1] != 10.0:
        return False
    # o resto tem de ser igual
    return all(pa[k] == pb[k] for k in ("fundo", "borda", "alinha", "fmt"))

print("=" * 74)
print("AS ABAS")
print("=" * 74)
print(f"  original: {wa.sheetnames}")
print(f"  gerada:   {wb_.sheetnames}")
# 17/09/2026: o GLOSSARIO nasce so no gerador, sem planilha viva por tras -- nao tem original pra
# comparar, entao ele sai da lista antes de cobrar igualdade, e so se confere que nao sumiu.
_abas_novas = ["GLOSSÁRIO"]
_gerada_sem_novas = [n for n in wb_.sheetnames if n not in _abas_novas]
# O original que o Mizuki exporta já traz o GLOSSARIO -- ele monta o construir() e exporta a planilha
# pronta --, mas o desenho dela nao vem dali: vem do glossario.py. Comparar a aba dele com a gerada
# compara o gerador com o proprio gerador, e foi o que deixou este comparador vermelho (338 celulas
# de fonte, 338 de alinhamento, 224 de fundo, 39 de valor) desde o commit que criou o GLOSSARIO.
_original_sem_novas = [n for n in wa.sheetnames if n not in _abas_novas]
if _original_sem_novas != _gerada_sem_novas:
    difs.append(f"ordem/nome das abas: {_original_sem_novas} != {_gerada_sem_novas} (fora as novas {_abas_novas})")
for nova in _abas_novas:
    if nova not in wb_.sheetnames:
        difs.append(f"a aba nova {nova!r} sumiu da geracao")
for n in wa.sheetnames:
    if n in wb_.sheetnames and wa[n].sheet_state != wb_[n].sheet_state:
        difs.append(f"{n}: estado {wa[n].sheet_state} != {wb_[n].sheet_state}")
print(f"  estados: " + ", ".join(f"{n}={wa[n].sheet_state}" for n in wa.sheetnames))

for n in wa.sheetnames:
    if n not in wb_.sheetnames or n in _abas_novas:
        continue
    sa, sb = wa[n], wb_[n]
    print()
    print("=" * 74)
    print(f"A ABA {n}")
    print("=" * 74)

    lin = max(sa.max_row, sb.max_row)
    col = max(sa.max_column, sb.max_column)
    print(f"  extensao: original {sa.max_row}x{sa.max_column} · "
          f"gerada {sb.max_row}x{sb.max_column}")

    BASE = base_da_aba(sa)
    iguais = ruido = 0
    for r in range(1, lin + 1):
        for c in range(1, col + 1):
            pa, pb = perfil(sa.cell(row=r, column=c)), perfil(sb.cell(row=r, column=c))
            # limpeza 21: a divisoria entre a moldura (cabecalho e lombada, em tinta) e o miolo, na cor da regua
            # (correcoes_borda.py). Tira do gerado o lado que so ele tem, e o resto da celula segue as outras
            # regras — uma celula da lombada estendida e uma da divisoria ao mesmo tempo, por exemplo.
            _lados_div = DIVISORIA.get((n, sb.cell(row=r, column=c).coordinate), ())
            for _lado in _lados_div:
                if pb["borda"].get(_lado) == DIVISORIA_TRACO and pa["borda"].get(_lado) != DIVISORIA_TRACO:
                    pb = {**pb, "borda": {k: v for k, v in pb["borda"].items() if k != _lado}}
                    esperadas["divisória entre a moldura e o miolo"] += 1
            if pa == pb:
                iguais += 1
                continue
            if eh_ruido_de_fabrica(pa, pb):
                ruido += 1
                esperadas["Arial 10 de fábrica em célula vazia"] += 1
                continue
            coord = sa.cell(row=r, column=c).coordinate
            # limpeza 4: a barra "agora" do original vem com o numero do
            # personagem que o Mizuki estava jogando, e o molde tem de nascer
            # cheio. A lista mora no layout.json, nunca aqui.
            _cheia = BARRAS.get(n, {}).get(coord)
            # (so o VALOR pode diferir: ate 19/09/2026 esta regra engolia qualquer outra diferenca da celula)
            if (_cheia is not None and pb["valor"] == _cheia
                    and all(pa[k] == pb[k] for k in pa if k != "valor")):
                esperadas["barra 'agora' reposta para nascer cheia"] += 1
                continue
            # limpeza 5: o estado de mesa volta vazio, e so o VALOR pode diferir
            if coord in VAZIO.get(n, []) and pb["valor"] is None and all(pa[k] == pb[k] for k in pa if k != "valor"):
                esperadas["estado de mesa que volta vazio"] += 1
                continue
            # limpeza 6: o Arial vira a fonte de corpo, e so o NOME da fonte muda
            if (ARIAL and pa["fonte"] and pb["fonte"] and pa["fonte"][0] == ARIAL
                    and pb["fonte"][0] != ARIAL and pb["fonte"][1:] == pa["fonte"][1:]
                    and all(pa[k] == pb[k] for k in pa if k != "fonte")):
                esperadas["Arial que vira a fonte de corpo"] += 1
                continue
            # limpeza 7: o carimbo que o Sheets leu como numero volta a ser texto
            if (coord in CARIMBO.get(n, []) and isinstance(pa["valor"], (int, float))
                    and isinstance(pb["valor"], str)
                    and all(pa[k] == pb[k] for k in pa if k != "valor")):
                esperadas["carimbo de versão que volta a ser texto"] += 1
                continue
            # limpeza 8: a aba DADOS sai do catalogo, e nao da exportacao (v0.239 do
            # sistema). So o VALOR pode diferir, e ele tem de ser o que o catalogo manda.
            # as doze listas moram de A a L, numa letra so: ate 15/09/2026 a coluna AB passava por lista
            if (n == "DADOS" and (coord in DADOS_CAT or dados_catalogo.e_da_lista(coord))
                    and re.fullmatch(r"[A-L]\d+", coord)
                    and pb["valor"] == DADOS_CAT.get(coord)
                    and all(pa[k] == pb[k] for k in pa if k != "valor")):
                esperadas["célula da DADOS que sai do catálogo"] += 1
                continue
            # limpeza 9: o TR treinado soma a maestria, e nao 2 (v0.240 do sistema, o B14). So o
            # VALOR pode diferir, e ele tem de ser a formula que o tr_treinado.py monta.
            if (n == "FICHA" and coord in TR_NOVAS and pb["valor"] == TR_NOVAS[coord]
                    and all(pa[k] == pb[k] for k in pa if k != "valor")):
                esperadas["fórmula de TR que passa a somar a maestria"] += 1
                continue
            # limpeza 13: o desenho da mesa (17/09/2026). O VALOR tem de ser o que o ficha_layout.py monta, e o
            # estilo tem de ser o de uma testemunha com o mesmo estilo no layout.
            _fl = FL["celulas"].get(n, {}).get(coord)
            if _fl is not None and pb["valor"] == _fl[0]:
                _t = TESTEMUNHA.get(_fl[1])
                if _fl[1] is None or _t is None or all(pb[k] == perfil(wb_[_t[0]][_t[1]])[k] for k in pb if k != "valor"):
                    esperadas["célula do desenho da mesa"] += 1
                    continue
            if pb["valor"] is None and pa["valor"] in (None, "") and any(
                    indice_ficha._lc(m.split(":")[0]) != (r, c) and
                    indice_ficha._lc(m.split(":")[0])[0] <= r <= indice_ficha._lc(m.split(":")[1])[0] and
                    indice_ficha._lc(m.split(":")[0])[1] <= c <= indice_ficha._lc(m.split(":")[1])[1]
                    for m in FL["mescladas"].get(n, [])):
                esperadas["célula de dentro de caixa mesclada nova, que perde o estilo próprio"] += 1
                continue
            if coord in FL["celulas_sai"].get(n, []) and pb["valor"] is None:
                esperadas["célula pintada depois da margem, que sai"] += 1
                continue
            # limpeza 11: o indice da DADOS em formula, derivado dos rotulos da FICHA (17/09/2026)
            _ix = IX.get(n, {}).get(coord)
            if _ix is not None:
                _molde = perfil(sb[_ix[1]])
                if pb["valor"] == _ix[0] and all(pb[k] == _molde[k] for k in pb if k != "valor"):
                    esperadas["célula do índice da DADOS em fórmula"] += 1
                    continue
            # limpeza 12: a ficha automatica (17/09/2026)
            _fa = FA["celulas"].get(n, {}).get(coord)
            if _fa is not None:
                _molde = perfil(sb[_fa[1]])
                if pb["valor"] == _fa[0] and all(pb[k] == _molde[k] for k in pb if k != "valor"):
                    esperadas["célula da ficha automática"] += 1
                    continue
            # limpeza 10: a Defesa com uniforme, escudo e refino escolhido (v0.246 do sistema, o B3). O
            # VALOR tem de ser o que o defesa_equipamento.py monta, e o ESTILO tem de ser o da celula que
            # ele declara como molde, na ficha gerada.
            _de = DE["celulas"].get(n, {}).get(coord)
            if _de is not None:
                _molde = perfil(sb[_de[1]])
                if pb["valor"] == _de[0] and all(pb[k] == _molde[k] for k in pb if k != "valor"):
                    esperadas["célula da Defesa com equipamento e refino escolhido"] += 1
                    continue
            # limpeza 14: a celula vazia que so tem o formato de corpo (ver eh_vazia_padrao). Cobre as
            # duas linhas de folga que o emissor poe embaixo de cada aba (max_r + 2) e o fundo de base
            # da DADOS_INV, que a exportacao escreve celula a celula.
            if eh_vazia_padrao(pa, BASE, False) and eh_vazia_padrao(pb, BASE, True):
                esperadas["célula vazia só com o formato de corpo (a exportação escreve, o script pinta antes)"] += 1
                continue
            # ... e a celula COM valor ou formato proprio cujo unico desvio e o fundo ser o de base: o
            # script pinta a aba com ele antes de escrever qualquer celula.
            if (pa["fundo"] == BASE and pb["fundo"] is None
                    and all(pa[k] == pb[k] for k in pa if k != "fundo")):
                esperadas["célula com o fundo de base, que o gerador não escreve"] += 1
                continue
            # limpeza 15: a caixa ORIGEM da CARTEIRA nasceu com borda branca fina em tres lados, engano de
            # formatacao manual; o ficha-v01/correcoes_borda.py da a ela, celula a celula, a borda da CAMINHO
            # (as duas tem dez colunas: AK:AT e O:X).
            if n == "CARTEIRA" and r == 17 and 37 <= c <= 46:
                _irma = perfil(sb.cell(row=17, column=c - 22))
                if pb["borda"] == _irma["borda"] and all(
                        pa[k] == pb[k] for k in pa if k not in ("borda", "fonte")) and (
                        pa["fonte"] == pb["fonte"] or eh_ruido_de_fabrica({**pa, "borda": {}}, {**pb, "borda": {}})):
                    esperadas["caixa ORIGEM com a borda da CAMINHO"] += 1
                    continue
            # limpeza 16: a lombada (fundo tinta, colunas A e B) vai ate a ultima linha da FICHA e da
            # INVOCACAO; a planilha viva parava de pintar ela antes (correcoes_borda.py).
            if (n in ("FICHA", "INVOCAÇÃO") and c <= 2 and pb["fundo"] == TINTA and pb["valor"] is None
                    and pa["valor"] in (None, "") and pa["fundo"] in (None, BASE) and not pa["borda"]
                    and not pb["borda"]):
                esperadas["lombada até a última linha"] += 1
                continue
            # limpeza 21: o texto que o livro mudou depois da exportacao (o Jorro do CATALOGO, que o capitulo 16
            # escreve "ataca e empurra"), em correcoes_texto._TROCAS_DO_LIVRO. So essa frase muda.
            if (n in correcoes_texto.ABAS_CORRIGIDAS and pa["valor"] != pb["valor"]
                    and correcoes_texto.troca_do_livro(n, pa["valor"]) is not None
                    and correcoes_texto.corrige_valor(n, pa["valor"]) == pb["valor"]
                    and all(pa[k] == pb[k] for k in pa if k != "valor")):
                esperadas["frase que o livro mudou depois da exportação (o Jorro ataca e empurra)"] += 1
                continue
            # limpeza 20: o texto curto que abria frase, titulo ou mensagem com a inicial minuscula, na
            # INVOCACAO e no CATALOGO (correcoes_texto.py). So a inicial muda, e o resto da celula e igual.
            if (n in correcoes_texto.ABAS_CORRIGIDAS and pa["valor"] != pb["valor"]
                    and correcoes_texto.corrige_valor(n, pa["valor"]) == pb["valor"]
                    and all(pa[k] == pb[k] for k in pa if k != "valor")):
                esperadas["texto que abria frase ou título em minúscula"] += 1
                continue
            # limpeza 17: a exportacao do Sheets traz o estado da personagem que o Mizuki estava jogando (a
            # Origem escolhida, as caixas de selecao marcadas pelo Caminho), e o molde nasce limpo.
            if (n, coord) in ESTADO_DA_PERSONAGEM and all(pa[k] == pb[k] for k in pa if k != "valor"):
                esperadas["escolha da personagem exportada (a Origem), que o molde nasce sem"] += 1
                continue
            if (pa["valor"] is True and pb["valor"] is False
                    and all(pa[k] == pb[k] for k in pa if k != "valor")):
                esperadas["caixa de seleção marcada na exportação, que o molde deixa vazia"] += 1
                continue
            # limpeza 18: o Sheets exporta o que uma formula MATRICIAL despeja como celula solta com
            # COMPUTED_VALUE; o gerador leva so a formula da ancora, e as outras ficam vazias.
            if (isinstance(pa["valor"], str) and 'DUMMYFUNCTION("""COMPUTED_VALUE"""' in pa["valor"]
                    and pb["valor"] is None and all(pa[k] == pb[k] for k in pa if k != "valor")):
                esperadas["resultado de fórmula matricial que a exportação escreve solto"] += 1
                continue
            # limpeza 19: a formula que o Sheets exporta embrulhada em IFERROR(__xludf.DUMMYFUNCTION("...")),
            # porque o Excel nao a conhece. O gerador leva a de dentro (o conferir-ficha-xlsx.py confere).
            if isinstance(pa["valor"], str) and isinstance(pb["valor"], str):
                _emb = re.match(r'^=IFERROR\(__xludf\.DUMMYFUNCTION\("(.*)"\),(.*)\)$', pa["valor"], re.S)
                if (_emb and "=" + _emb.group(1).replace('""', '"').strip() == pb["valor"]
                        and all(pa[k] == pb[k] for k in pa if k != "valor")):
                    esperadas["fórmula que a exportação embrulha em DUMMYFUNCTION"] += 1
                    continue
                # o embrulho tambem infla a cauda de aspas a cada ida e volta pelo Sheets (`&""""` a mais no
                # INVOCACAO!O62 da exportacao nova, contra o layout mais velho): a formula de dentro e a mesma
                _cauda = lambda v: re.sub(r'\}\),[&"]+\)"\),""\)$', "})," + "<aspas>)", v)
                if (pa["valor"].startswith("=IFERROR(__xludf.DUMMYFUNCTION(") and _cauda(pa["valor"]) == _cauda(pb["valor"])
                        and all(pa[k] == pb[k] for k in pa if k != "valor")):
                    esperadas["cauda de aspas que a exportação infla a cada ida e volta"] += 1
                    continue
            for k in pa:
                if pa[k] != pb[k]:
                    difs.append(f"{n}!{coord} {k}: {pa[k]!r} != {pb[k]!r}")
    print(f"  células idênticas: {iguais}")
    print(f"  células que só diferem pelo Arial de fábrica: {ruido}")

    ma, mb = {str(x) for x in sa.merged_cells.ranges}, {str(x) for x in sb.merged_cells.ranges}
    print(f"  mesclagens: {len(ma)} original · {len(mb)} gerada")
    for x in sorted(ma - mb):
        if x in FL["mescladas_sai"].get(n, []):      # limpeza 13: as caixas refeitas e a foto
            esperadas["mesclagem do desenho da mesa"] += 1
        elif x in FA["mescladas_sai"].get(n, []):    # limpeza 12: o cabecalho das Passivas dividido
            esperadas["mesclagem das Passivas refeita"] += 1
        else:
            difs.append(f"{n}: mesclagem {x} faltou")
    for x in sorted(mb - ma):
        if x in FL["mescladas"].get(n, []):          # limpeza 13: as caixas refeitas e a foto
            esperadas["mesclagem do desenho da mesa"] += 1
        elif x in DE["mescladas"].get(n, []):        # limpeza 10: a caixa do refino escolhido
            esperadas["mesclagem da caixa do refino escolhido"] += 1
        elif x in FA["mescladas"].get(n, []):        # limpeza 12: as Passivas divididas e as linhas novas
            esperadas["mesclagem das Passivas refeita"] += 1
        else:
            difs.append(f"{n}: mesclagem {x} sobrou")

    def largs(s):
        d = {}
        for k, v in s.column_dimensions.items():
            if v.width:
                for c in range(v.min, v.max + 1):
                    d[c] = round(v.width, 2)
        return d
    la, lb = largs(sa), largs(sb)
    trocadas = 0
    for c in set(la) | set(lb):
        va, vb = la.get(c), lb.get(c)
        if va == vb:
            continue
        if n in FL["larguras"] and ((va is None and c == FL["larguras"][n]) or (vb is None and c > FL["larguras"][n])):
            esperadas["coluna da margem da direita"] += 1
            continue
        if va and vb and abs(va - 3.63) < 0.01 and abs(vb - 4.0) < 0.01:
            trocadas += 1
            esperadas["largura 3,63 -> 4,0"] += 1
            continue
        difs.append(f"{n}: largura da coluna {c}: {va} != {vb}")
    print(f"  larguras: {len(la)} original · {len(lb)} gerada · "
          f"{trocadas} trocadas de 3,63 para 4,0")

    ha = {int(k): v.height for k, v in sa.row_dimensions.items() if v.height}
    hb = {int(k): v.height for k, v in sb.row_dimensions.items() if v.height}
    for k in set(ha) | set(hb):
        if ha.get(k) != hb.get(k):
            difs.append(f"{n}: altura da linha {k}: {ha.get(k)} != {hb.get(k)}")
    print(f"  alturas de linha: {len(ha)} original · {len(hb)} gerada")

    va = {(str(v.sqref), v.type, v.formula1) for v in sa.data_validations.dataValidation}
    vbs = {(str(v.sqref), v.type, v.formula1) for v in sb.data_validations.dataValidation}
    print(f"  menus suspensos: {len(va)} original · {len(vbs)} gerada")
    for x in sorted(va - vbs): difs.append(f"{n}: menu {x} faltou")
    _menus_de = {(m["onde"], m["tipo"], m["formula"]) for m in DE["menus"].get(n, [])}
    _troca_fa = FA["menus_troca"].get(n, {})
    _form_fa = FA.get("menus_formula", {}).get(n, {})
    _novos_fa = {(m["onde"], m["tipo"], m["formula"]) for m in FA.get("menus_novos", {}).get(n, [])}
    for x in sorted(va - vbs):                       # limpeza 12: Caminho, Trilha e Origem com lista nova
        if x[0] in _form_fa and (x[0], x[1], _form_fa[x[0]]) in vbs:
            esperadas["menu de Caminho, Trilha ou Origem com a lista nova"] += 1
            difs.remove(f"{n}: menu {x} faltou")
            difs.remove(f"{n}: menu {(x[0], x[1], _form_fa[x[0]])} sobrou") if f"{n}: menu {(x[0], x[1], _form_fa[x[0]])} sobrou" in difs else None
    for x in sorted(va - vbs):
        if x[0] in _troca_fa and (_troca_fa[x[0]], x[1], x[2]) in vbs:   # limpeza 12: o menu das Passivas
            esperadas["menu das Passivas estendido"] += 1
            difs.remove(f"{n}: menu {x} faltou")
    for x in sorted(vbs - va):
        if x[0] in _troca_fa.values() and any(k for k, v in _troca_fa.items() if v == x[0]):
            continue
        if x[0] in _form_fa and x[2] == _form_fa[x[0]]:
            continue
        if x in _menus_de:                           # limpeza 10: o menu do equipamento e o do refino
            esperadas["menu do equipamento e do refino escolhido"] += 1
        elif x in _novos_fa:                         # 17/09/2026: o menu da troca de pericia por arma
            esperadas["menu de Treinamento em Armas, novo"] += 1
        else:
            difs.append(f"{n}: menu {x} sobrou")

    def regras(s):
        out = []
        for faixa in s.conditional_formatting:
            for r in faixa.rules:
                fc = cor(r.dxf.font.color) if (r.dxf and r.dxf.font and r.dxf.font.color) else None
                fb = cor(r.dxf.fill.bgColor) if (r.dxf and r.dxf.fill and r.dxf.fill.bgColor) else None
                out.append((str(faixa.sqref), r.type, fc, fb))
        return out
    ra, rb = regras(sa), regras(sb)
    de_fabrica = [x for x in ra if x[3] == "FFB7E1CD"]
    esperadas["condicional verde de fábrica"] += len(de_fabrica)
    ra_limpa = [x for x in ra if x[3] != "FFB7E1CD"]
    # O construir() troca TODA a condicional da FICHA (corDeEstado_, no Codigo.gs), entao a do layout so
    # existe pra a planilha .xlsx e nunca chega ao Sheets. As regras de aviso vermelho ("passou de", "a mais")
    # seguem os enderecos das caixas, que mudam a cada linha inserida -- e o layout.json e a exportacao
    # foram tirados em momentos diferentes (a exportacao nao tem o AK76 que o layout tem).
    if n == "FICHA":
        _aviso = lambda x: x[1] == "containsText" and x[2] == "FFC2334D"
        esperadas["condicional de aviso vermelho da FICHA, que o construir() refaz"] += len([x for x in ra_limpa if _aviso(x)])
        ra_limpa = [x for x in ra_limpa if not _aviso(x)]
        rb = [x for x in rb if not _aviso(x)]
    print(f"  condicional: {len(ra)} original ({len(de_fabrica)} de fábrica) · "
          f"{len(rb)} gerada")
    # a formula nao entra na comparacao: o Sheets exporta com aspas extras, e
    # tirar elas e o que faz a regra valer de novo
    for x in ra_limpa:
        if x not in rb: difs.append(f"{n}: condicional {x} faltou")
    for x in rb:
        if x not in ra_limpa: difs.append(f"{n}: condicional {x} sobrou")

    ia = [(round(i.width), round(i.height)) for i in getattr(sa, "_images", [])]
    ib = [(round(i.width), round(i.height)) for i in getattr(sb, "_images", [])]
    print(f"  imagens: {len(ia)} original · {len(ib)} gerada")
    if sorted(ia) != sorted(ib) and n in LAY["_meta"].get("imagens_mantidas", {}) \
            and len(ia) == len(ib) == LAY["_meta"]["imagens_mantidas"][n]:
        # a exportacao trouxe a imagem de dentro da celula, e o extrator manteve a do layout anterior
        esperadas["imagem de dentro da célula, mantida do layout anterior"] += len(ia)
    elif sorted(ia) != sorted(ib):
        difs.append(f"{n}: tamanhos de imagem {sorted(ia)} != {sorted(ib)}")

print()
print("=" * 74)
print(f"AS DIFERENÇAS ESPERADAS — as {len(LAY['_meta']['limpezas'])} limpezas declaradas no layout.json")
print("=" * 74)
for k, v in esperadas.items():
    print(f"  {v:>6}  {k}")
for lim in LAY["_meta"]["limpezas"]:
    print(f"    · {lim}")

print()
print("=" * 74)
if difs:
    print(f">>> {len(difs)} DIFERENÇA(S) NÃO EXPLICADA(S):")
    for d in difs[:40]:
        print(f"    · {d}")
    if len(difs) > 40:
        print(f"    ... e mais {len(difs) - 40}")
    sys.exit(1)
print(f">>> IGUAIS — fora as {len(LAY['_meta']['limpezas'])} limpezas declaradas, o gerador reproduz o")
print("    arquivo do Mizuki célula por célula.")
print("=" * 74)
