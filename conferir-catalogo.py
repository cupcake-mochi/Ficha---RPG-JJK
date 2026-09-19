# -*- coding: utf-8 -*-
"""Integridade referencial do catalogo: todo nome citado existe na tabela dona.
Nasceu de um bug real: a tabela de Familias tinha 'Area' e as Melhorias
apontavam para 'Area' com acento. Lição 9 do projeto, acontecendo dentro do
proprio arquivo que existe para evitar ela."""
import json, sys
CAT = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))
falhas = []

def checa(nome, itens, campo, dono):
    orfas = sorted({v[campo] for v in itens.values() if v.get(campo) and v[campo] not in dono})
    print(f"  [{'OK' if not orfas else 'FALHA'}] {nome}")
    if orfas:
        falhas.append(f"{nome}: {orfas}")
        for o in orfas: print(f"          '{o}' nao existe na tabela dona")

print("INTEGRIDADE REFERENCIAL")
checa("toda Melhoria aponta para uma Familia que existe", CAT["melhorias"], "familia", CAT["familias"])
checa("toda Forma aponta para uma Familia que existe",    CAT["formas"],    "familia", CAT["familias"])
checa("toda pericia aponta para um atributo que existe",  CAT["pericias"],  "atributo",
      {a.replace("Forca","Forca") for a in CAT["atributos"]["lista"]})

print("\nCONTAGENS DECLARADAS NO MANUAL")
# v0.239 do sistema: o numero e a pagina moravam aqui, e as duas coisas envelheceram -- o
# catalogo tinha catorze condicoes e o manual passou a dizer treze. Agora cada contagem sai da
# frase em que o proprio manual a declara, lida do manual.txt. Melhorias, Formas e Restricoes o
# manual nao conta por extenso, e por isso cada nome delas tem de aparecer nele.
import re
MAN = " ".join(open("manual.txt", encoding="utf-8").read().split())
_U = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
      "onze", "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
EXT = {p: n for n, p in enumerate(_U)}
EXT.update({"uma": 1, "duas": 2, "vinte": 20, "trinta": 30})
EXT.update({f"vinte e {p}": 20 + n for n, p in enumerate(_U[1:10], 1)})
EXT.update({"vinte e uma": 21, "vinte e duas": 22})
_NUM = "|".join(sorted(map(re.escape, EXT), key=len, reverse=True))

def declarado(rx):
    m = re.search(rx.replace("NUM", "(" + _NUM + ")"), MAN)
    return (EXT[m.group(1)], m.group(0)) if m else (None, None)

for nome, chave, rx in [("pericias", "pericias", r"\bNUM perícias"), ("oficios", "oficios", r"\bNUM ofícios"),
                        ("Familias", "familias", r"divididas em NUM Famílias"),
                        ("condicoes", "condicoes", r"\bas NUM condições")]:
    n = len(CAT[chave]); d, frase = declarado(rx)
    ok = d == n
    if not ok: falhas.append(f"{nome}: {n} != {d}")
    print(f"  [{'OK' if ok else 'FALHA'}] {nome:10} {n:3}   o manual declara {d}: '{frase}'")
mt = re.search(r"São (" + _NUM + r") Caminhos, (" + _NUM + r") Trilhas em cada um", MAN)
dc, dt = (EXT[mt.group(1)], EXT[mt.group(1)] * EXT[mt.group(2)]) if mt else (None, None)
for nome, chave, d in (("Caminhos", "caminhos", dc), ("Trilhas", "trilhas", dt)):
    n = len(CAT[chave]); ok = d == n
    if not ok: falhas.append(f"{nome}: {n} != {d}")
    print(f"  [{'OK' if ok else 'FALHA'}] {nome:10} {n:3}   o manual declara {d}: '{mt.group(0) if mt else None}'")

def no_manual(nome):
    """o pdftotext -layout parte a celula de tabela, e a coluna do lado entra no meio do nome"""
    rx = r"\b" + r"\b(?:\s+\S+){0,25}?\s+\b".join(re.escape(p) for p in nome.split()) + r"\b"   # "Abre ... Ferida" tem 16 no meio
    return re.search(rx, MAN) is not None

for nome, chave in (("Melhorias", "melhorias"), ("Formas", "formas"), ("Restricoes", "restricoes")):
    faltam = [x for x in CAT[chave] if not no_manual(x)]
    if faltam: falhas.append(f"{nome} que o manual nao tem: {faltam}")
    print(f"  [{'OK' if not faltam else 'FALHA'}] as {len(CAT[chave])} {nome} do catalogo aparecem no manual"
          + (f"  <- faltam {faltam}" if faltam else ""))

print("\nTESTES DE RESISTENCIA CONTRA O MANUAL")
# v0.240 do sistema, o B14: o catalogo dizia `bonus_se_treinado: 2`, que e a regra do manual da
# v0.104, e a chave estava entre as nao conferidas contra o livro. O termo sai da formula do
# capitulo 1, a contagem sai da frase dos treinados, e o atributo de cada TR sai da tabela.
TRC = CAT["testes_de_resistencia"]
_trs = {t: v for t, v in TRC.items() if isinstance(v, dict)}
_mr = re.search(r"Teste de Resistência = d20 \+ atributo do TR \+ (\w+), e a (\w+) só entra "
                r"se você for treinado nele", MAN)
ok = bool(_mr) and _mr.group(1) == _mr.group(2) == TRC.get("bonus_se_treinado")
if not ok: falhas.append("o termo do TR treinado nao e o do manual")
print(f"  [{'OK' if ok else 'FALHA'}] o TR treinado soma '{TRC.get('bonus_se_treinado')}', "
      f"e o manual soma '{_mr.group(1) if _mr else None}'")
_mq = re.search(r"Você é treinado em (" + _NUM + r") dos (" + _NUM + r"):", MAN)
_dq = (EXT[_mq.group(1)], EXT[_mq.group(2)]) if _mq else (None, None)
ok = _dq == (TRC.get("treinados_na_criacao"), len(_trs))
if not ok: falhas.append(f"TRs: {TRC.get('treinados_na_criacao')} de {len(_trs)} != {_dq}")
print(f"  [{'OK' if ok else 'FALHA'}] treinados {TRC.get('treinados_na_criacao')} de {len(_trs)}, "
      f"e o manual declara {_dq[0]} de {_dq[1]}")
_mt = re.search(r"TESTE DE USA SERVE PARA RESISTÊNCIA (.*?) Só o TR Físico", MAN)
_tab = _mt.group(1) if _mt else ""
_linhas = [f"{t} {' ou '.join(v['atributo'])}" for t, v in _trs.items()]
faltam = [x for x in _linhas if x not in _tab]
if faltam or not _mt: falhas.append(f"TRs que a tabela do manual nao tem: {faltam or 'a tabela sumiu'}")
print(f"  [{'OK' if _mt and not faltam else 'FALHA'}] os {len(_trs)} TRs e os atributos deles estao na tabela"
      + (f"  <- faltam {faltam or 'a tabela'}" if faltam or not _mt else ""))

print("\nSUB-ORIGEM E ROTAS DE CRIACAO CONTRA O MANUAL")
# v0.240 do sistema. A `sub_origem` dizia que Sem Technica combinava com qualquer Origem, e as
# `rotas_de_criacao` davam tres rotas como "sendo escrita", da epoca em que o livro tinha a tabela
# `Rotas de criacao`. A tabela saiu na v0.147; cada rota sai da frase do capitulo que a monta.
def _nomes(txt):
    return [x.strip() for x in re.split(r",| e ", txt) if x.strip()]
_cinco = re.search(r"Cinco principais \(([^)]*)\)", MAN)
_alc = re.search(r"(\w+) Origens alcançam ela — ([^.]*)\.", MAN)
_so = CAT["sub_origem"].get("Sem Técnica", {})
if not isinstance(_so, dict):
    _so = {}          # o formato de antes da v0.240 era uma frase, sem a lista
ok = bool(_cinco and _alc) and _so.get("origens") == _nomes(_alc.group(2)) == _nomes(_cinco.group(1)) \
     and EXT.get(_alc.group(1).lower()) == len(_so.get("origens", [])) \
     and all(o in CAT["origens"] and not CAT["origens"][o].get("especial") for o in _so.get("origens", []))
if not ok: falhas.append("as Origens que alcancam Sem Tecnica nao sao as do manual")
print(f"  [{'OK' if ok else 'FALHA'}] Sem Técnica alcança {_so.get('origens')}, "
      f"e o manual diz {_alc.group(2) if _alc else None}")

_ROT = CAT["rotas_de_criacao"]
def _linhas(rota):
    return [r for r in _ROT if r["rota"] == rota]
_mm = re.search(r"(\w+) rotas? de criação montam? o poder aqui em vez de montar no Fundamento: "
                r"o ([^.]*?) e a ([^.]*)\.", MAN)
_ms = re.search(r"(\w+) rota de criação monta o poder aqui em vez de montar no Fundamento: "
                r"a sub-origem (Sem Técnica)", MAN)
def _no_texto(origem, txt):
    base, _, ramo = origem.partition(" · ")
    return base in txt and (not ramo or ramo in txt)
_tm = _linhas("Técnica Marcial")
ok = bool(_mm) and EXT.get(_mm.group(1).lower()) == len(_tm) and all(_no_texto(r["origem"], _mm.group(0)) for r in _tm)
if not ok: falhas.append("as rotas pela Tecnica Marcial nao sao as do manual")
print(f"  [{'OK' if ok else 'FALHA'}] Técnica Marcial: {[r['origem'] for r in _tm]}")
_st = _linhas("Sem Técnica")
ok = bool(_ms) and EXT.get(_ms.group(1).lower()) == len(_st) and all(_ms.group(2) in r["origem"] for r in _st)
if not ok: falhas.append("a rota do Sem Tecnica nao e a do manual")
print(f"  [{'OK' if ok else 'FALHA'}] Sem Técnica: {[r['origem'] for r in _st]}")
_fu = _linhas("Fundamento")
_principais = _nomes(_cinco.group(1)) if _cinco else []
_padrao = len(re.findall(r"Fundamento, do jeito padrão", MAN))
_rc = [r for r in _fu if r["origem"] not in _principais]
ok = sorted(r["origem"] for r in _fu if r["origem"] in _principais) == sorted(_principais) == sorted(_principais[:_padrao]) \
     and len(_principais) == _padrao \
     and len(_rc) == 1 and _rc[0]["origem"].startswith("Restrição Celestial · corpo pela técnica") \
     and "Fundamento normal, corpo com limitação" in MAN
if not ok: falhas.append("as rotas pelo Fundamento nao sao as do manual")
print(f"  [{'OK' if ok else 'FALHA'}] Fundamento: as {_padrao} principais do jeito padrão, e {[r['origem'] for r in _rc]}")
_sobra = [r for r in _ROT if r not in _tm + _st + _fu]
if _sobra: falhas.append(f"rotas que nenhuma frase do manual cobre: {_sobra}")
print(f"  [{'OK' if not _sobra else 'FALHA'}] as {len(_ROT)} rotas estão todas cobertas por uma frase do manual")

print("\nAS SEIS CHAVES QUE FALTAVAM, CONTRA O MANUAL")
# v0.240 do sistema, 15/09/2026. Atributos, Fundamento, Origens, Legados, formatos de Legado e
# progressao nunca tinham sido conferidos contra o livro. Os Legados estavam catorze entradas atras
# -- um `Sem Patente` e um `Nunca Estive La` que o livro nao tem, sete Desliga faltando --, a entrega
# de dezoito niveis estava cortada, e so duas Origens tinham a frase de abertura. Tudo aqui sai do
# manual.txt, e nenhum nome ou numero esta escrito nesta secao.
import math

def _norm(s):
    s = " ".join(s.split())
    s = s.replace("‐ ", "")                      # a hifenizacao de fim de linha do pdftotext
    return re.sub(r" ([,.;:)])", r"\1", s)            # e o espaco antes da pontuacao, depois de codigo
MANN = _norm(open("manual.txt", encoding="utf-8").read())

def _ok(nome, cond, det=""):
    if not cond: falhas.append(nome)
    print(f"  [{'OK' if cond else 'FALHA'}] {nome}" + (f"  <- {det}" if det and not cond else ""))

def _num(p):
    return int(p) if p.isdigit() else EXT.get(p.lower())

# --- atributos
A = CAT["atributos"]
_ma = re.search(r"((?:[A-ZÁÉÍÓÚ]\w+ · ){4}[A-ZÁÉÍÓÚ]\w+) O número é o modificador, numa escala de (\d+) a (\d+)\.", MANN)
_mc = re.search(r"(\w+) pontos entre os (\w+) atributos\. Nenhum acima de (\d+)\.", MANN)
_ok("atributos: a lista, a escala e a criação são as do livro",
    bool(_ma and _mc) and A["lista"] == _ma.group(1).split(" · ") and A["escala"] == [int(_ma.group(2)), int(_ma.group(3))]
    and A["criacao"] == {"pontos": _num(_mc.group(1)), "teto_por_atributo": int(_mc.group(3))} and _num(_mc.group(2)) == len(A["lista"])
    and "pagina" not in A, f"{A} · {_ma.group(0) if _ma else None} · {_mc.group(0) if _mc else None}")

# --- origens
_mo = re.search(r"São (\w+) Origens\. (\w+) principais \(([^)]*)\) e (\w+) especiais, ([^.]+)\.", MANN)
_nomes = lambda s: [x.strip() for x in re.split(r",| e ", s) if x.strip()]
if _mo:
    _pr, _es = _nomes(_mo.group(3)), _nomes(_mo.group(5))
    _ok("origens: as sete do livro, e as especiais marcadas",
        list(CAT["origens"]) == _pr + _es and _num(_mo.group(1)) == 7 == len(_pr) + len(_es)
        and all(bool(CAT["origens"][o].get("especial")) == (o in _es) for o in CAT["origens"]), _mo.group(0))
else:
    _ok("origens: as sete do livro, e as especiais marcadas", False, "a frase das Origens sumiu")
_sem = [o for o, v in list(CAT["origens"].items()) + list(CAT["sub_origem"].items()) if _norm(v.get("em_uma_linha", "")) not in MANN or not v.get("em_uma_linha")]
_ok("origens: a frase de abertura de cada uma está no livro", not _sem, str(_sem))

# --- legados, lidos do manual.txt
def _relogio(txt):
    m = re.search(r"[Uu]ma vez por (cena|dia|descanso curto|descanso longo)", txt)
    return "por " + m.group(1) if m else "sem relógio"
_CAB = {"Legados da Latente": "Latente", "Legados do Receptáculo": "Receptáculo", "Legados do Descendente": "Descendente",
        "Legados do Reencarnado": "Reencarnado", "Legados do Feto": "Feto", "Legado de Sem Técnica": "Sem Técnica",
        "Legados do Corpo Amaldiçoado": "Corpo Amaldiçoado", "Legados: Corpo pela Técnica": "RC:Corpo pela Técnica",
        "Legados: Sem Energia": "RC:Sem Energia", "Legados: Desliga": "RC:Desliga", "Criar o seu Legado": None}
_lido, _st = {}, {"atual": None, "fmt": None, "nome": None, "texto": []}
def _fecha():
    e = _st
    if e["atual"] and e["nome"]:
        o, ramo = (e["atual"].split(":", 1) if e["atual"].startswith("RC:") else (e["atual"], None))
        o = next((x for x in CAT["origens"] if x.startswith("Restrição")), o) if ramo else o
        f = "Desliga" if ramo == "Desliga" else (e["fmt"] or "Destranca")
        v = {"relogio": _relogio(" ".join(e["texto"]))}
        if ramo: v["ramo"] = "os dois" if ramo == "Desliga" else ramo
        _lido.setdefault(o, {}).setdefault(f, {})[e["nome"]] = v
    e["nome"], e["texto"] = None, []
for _raw in open("manual.txt", encoding="utf-8").read().split("\n"):
    s = re.sub(r"^\d{1,2}\s{2,}", "", _raw.strip())          # o numero da margem gruda no comeco da linha
    if ". . ." in s: continue
    if s in _CAB:
        _fecha(); _st["atual"], _st["fmt"] = _CAB[s], None
        if _CAB[s] is None and _lido: break
        continue
    if _st["atual"] is None: continue
    if s and s.upper() == s and s.replace(" ", "") in ("DESTRANCA", "AJUSTA", "DESLIGA"):
        _fecha(); _st["fmt"] = s.replace(" ", "").capitalize(); continue
    _me = re.match(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^—:.]{0,38}?) — (.*)", s)
    if _me and not s.startswith(("Na mesa", "Exemplo")):
        _fecha(); _st["nome"], _st["texto"] = _me.group(1).strip(), [_me.group(2)]; continue
    if s.startswith("Na mesa"): _fecha(); continue
    if _st["nome"]: _st["texto"].append(s)
_fecha()
_n_leg = sum(len(v) for o in _lido.values() for v in o.values())
_dif = [(o, f) for o in set(_lido) | set(CAT["legados"]) for f in ("Destranca", "Ajusta", "Desliga")
        if _lido.get(o, {}).get(f, {}) != CAT["legados"].get(o, {}).get(f, {})]
_ok(f"legados: os {_n_leg} do livro, com formato, relógio e ramo", _n_leg > 0 and not _dif and list(_lido) == list(CAT["legados"]), str(_dif[:3]))
_fr = [f for f, frases in CAT["legados_formatos"].items() for x in frases if _norm(x) not in MANN]
_ok("legados: a frase de cada formato está no livro", set(CAT["legados_formatos"]) == {"Destranca", "Ajusta", "Desliga"} and not _fr, str(_fr))

# --- progressao
PR = CAT["progressao"]
_TAB, _LIN = {}, open("manual.txt", encoding="utf-8").read().split("\n")
_cap = next((i for i, l in enumerate(_LIN) if " ".join(l.split()) == "PROGRESSÃO POR NÍVEL"), len(_LIN))
for _raw in _LIN[_cap:]:
    s = re.sub(r"\s+", " ", _raw.strip())
    # o numero da margem pode vir grudado antes do nivel: foi assim que o 23 sumiu na v0.240
    m = re.match(r"^(?:\d{1,2} )?(\d{1,2}) ([\d.]+|—) (\d) (\d{1,2}) (\d) (\d) (\d) (\d)(?: (.*))?$", s)
    if m and 1 <= int(m.group(1)) <= 30 and int(m.group(1)) not in _TAB:
        _TAB[int(m.group(1))] = (m.group(2), [int(m.group(i)) for i in range(3, 9)], _norm(m.group(9) or "—"))
    if len(_TAB) == 30:
        break
_col = ("maestria", "espacos", "refino", "classe", "passiva", "classe0")
_pr_ruim = [n for n, (xp, nums, ent) in _TAB.items()
            if PR["tabela_impressa"].get(str(n), {}).get("xp") != xp
            or [PR["tabela_impressa"][str(n)][c] for c in _col] != nums
            or not (_norm(PR["tabela_impressa"][str(n)]["entrega"]).startswith(ent)
                    or _norm(PR["tabela_impressa"][str(n)]["entrega"]).startswith(re.sub(r" \d{1,3}$", "", ent)))]
_ok("progressão: as 30 linhas da tabela, com XP e o começo da entrega de cada uma",
    sorted(_TAB) == list(range(1, 31)) and len(PR["tabela_impressa"]) == 30 and not _pr_ruim, str(_pr_ruim[:5]))
_mm = re.search(r"chega a um marco: os níveis ((?:\d+, )+\d+ e \d+)\.", MANN)
_ok("progressão: os marcos são os do livro", bool(_mm) and PR["marcos"] == [int(x) for x in re.findall(r"\d+", _mm.group(1))],
    _mm.group(0) if _mm else None)
_ok("progressão: o que todo marco dá de graça", "De graça, em todo marco: " + PR["marco_entrega"] + "." in MANN)
_ml = re.search(r"rompe o limite de dano num alvo só\. Nos níveis ((?:\d+, )*\d+ e \d+)\.", MANN)
_ok("progressão: a Liberação Máxima nos níveis do livro",
    bool(_ml) and sorted(int(k) for k in PR["liberacao_maxima"]) == [int(x) for x in re.findall(r"\d+", _ml.group(1))])
_mi = re.search(r"Integridade = ([^.]+)\.", MANN)
_ok("progressão: a Integridade é a do livro", bool(_mi) and PR["formulas"]["integridade"].split("#")[0].strip()
    == _mi.group(1).replace("×", "*").replace("−", "-").replace("nível", "nivel"), _mi.group(0) if _mi else None)
_ok("progressão: a ficha começa no nível 2 e vai ao 30", "A ficha começa no nível " + str(PR["faixa_jogavel"][0]) in MANN
    and PR["faixa_jogavel"][1] == max(_TAB))

# --- fundamento
FU = CAT["fundamento"]
_NM = []
for _raw in open("manual.txt", encoding="utf-8").read().split("\n"):
    s = re.sub(r"\s+", " ", _raw.strip())
    m = re.match(r"^([1-7]) (\d{1,2}) (\d{1,2}) (\d) (\d) (\d{1,2}) (\d{1,2}) \+(\d) (\d{1,2}) \d+d8 = \d+ \d+d8 = \d+(?: \d{1,3})?$", s)
    if m and int(m.group(1)) == len(_NM) + 1:
        _NM.append([int(x) for x in m.groups()])
def _conta(expr, c):
    return math.ceil(eval(expr.replace(" x ", " * ").replace("Classe", str(c))))
_mt = re.search(r"teto (\d+) x Classe", FU["teto_e_liberacao"])
_marcos_cl = [int(x) for x in re.search(r"\(([\d,]+)\)", PR["formulas"]["classe"]).group(1).split(",")]
_nm_ruim = [r for r in _NM if [r[2], r[3], r[4], r[5], r[6], r[7], r[8]] != [
    _conta(FU["pontos_por_feitico"], r[0]), _conta(FU["preco_melhoria"]["Leve"], r[0]), _conta(FU["preco_melhoria"]["Media"], r[0]),
    _conta(FU["preco_melhoria"]["Pesada"], r[0]), _conta(FU["restricao_teto_devolucao"], r[0]), r[0],
    int(_mt.group(1)) * r[0] if _mt else -1] or r[1] != _marcos_cl[r[0] - 1]]
_ok("fundamento: pontos, preços de Melhoria, devolução, Liberação e teto reproduzem a tabela Números da montagem",
    len(_NM) == 7 and not _nm_ruim and FU["custo_em_pe"] == FU["pontos_por_feitico"], f"{len(_NM)} linhas · {_nm_ruim[:2]}")
_frases_fu = {
    "custo_em_pe": "Custo em PE = 3 × Classe (o mesmo número dos pontos)",
    "ponto_nao_gasto": "Cada ponto que você não gastar em mais nada " + FU["ponto_nao_gasto"],
    "arredondamento": "O que você paga sobe. O que você ganha desce. E o que você ganha nunca fica abaixo de 1.",
    "desconto_familia_livre": "as Melhorias delas custam metade da Classe a menos, com mínimo de 1 ponto",
    "restricao_so_paga_melhoria": "A devolução das Restrições nunca passa do que você gastou em Melhoria",
    "limite_contra_um_alvo": "Só a Liberação Máxima passa dos pontos da Classe em dano contra um alvo só",
    "teto_e_liberacao": "Teto de dano = " + (_mt.group(1) if _mt else "?") + " × Classe em dados",
}
_fal_fu = [k for k, fr in _frases_fu.items() if _norm(fr) not in MANN or k not in FU]
_ok("fundamento: cada regra tem a frase dela no livro", not _fal_fu, str(_fal_fu))
_mf = re.search(r"(\w+) Livres e (\w+) Fechadas", MANN)
_mr = re.search(r"Uma Restrição devolve Leve ou Média, nunca (\w+)", MANN)
_n2 = PR["tabela_impressa"]["2"]
_ok("fundamento: as Famílias, a Restrição que nunca devolve e o nível 2",
    bool(_mf and _mr) and [_num(_mf.group(1)), _num(_mf.group(2))] == [FU["familias_livres"], FU["familias_fechadas"]]
    and FU["restricao_nunca_devolve"] == _mr.group(1)
    and FU["nivel_2"] == {"classe": _n2["classe"], "feiticos_classe_0_gratis": _n2["classe0"], "feiticos_conhecidos": _n2["espacos"]})
_ok("fundamento: as Melhorias que espalham dano existem no manual",
    all(m in CAT["melhorias"] for m in FU["espalham_dano_e_contam_no_teto"]) and len(FU["espalham_dano_e_contam_no_teto"]) > 0)
_ok("as chaves conferidas cobrem o catálogo inteiro", not CAT["_meta"]["nao_conferido_contra_o_livro"],
    str(CAT["_meta"]["nao_conferido_contra_o_livro"]))

print("\nO EQUIPAMENTO QUE ENTRA NA DEFESA, CONTRA O MANUAL")
# v0.246 do sistema, o B3: a ficha digital passou a ter um menu de uniforme e escudo, e a tabela dele
# sai desta chave. As tres tabelas e as tres frases de regra saem do manual.txt, e nenhum numero
# esta escrito aqui.
EQ = CAT.get("equipamento_defesa", {})
_LIN = open("manual.txt", encoding="utf-8").read().splitlines()
_TRACO = lambda s: None if s == "—" else int(s)

def _tabela(titulo, rx, n_campos):
    """as linhas de dados logo depois do titulo em caixa alta da tabela"""
    for _i, _l in enumerate(_LIN):
        if _l.strip() == titulo:
            _rows = []
            for _m in _LIN[_i + 1:_i + 16]:
                _mm = re.match(rx, _m)
                if _mm:
                    _rows.append(_mm.groups())
            return _rows
    return []

_num3 = r"^\s*(\d)\s+(\d+)\s+(—|\d+)\s+(—|\d+)\s*$"
_ok_eq = True
for _tit, _nome in (("TRAJE", "Traje"), ("REVESTIMENTO", "Revestimento")):
    _rows = _tabela(_tit, _num3, 4)
    _livro = {f"{_nome} {g}": {"protecao": int(p), "teto_de_destreza": _TRACO(t), "requer_forca": _TRACO(f)}
              for g, p, t, f in _rows}
    _cat = {k: v for k, v in EQ.get("uniformes", {}).items() if k.startswith(_nome + " ")}
    _ok(f"equipamento: os {len(_livro)} degraus de {_nome} são os do livro",
        len(_livro) == 3 and _livro == _cat, f"livro {_livro} · catálogo {_cat}")
_rows = _tabela("ESCUDO", r"^\s*(\d)\s+(\S+)\s+(\d+)\s+(—|\d+)\s+(—|\d+)\s*$", 5)
_livro = {n: {"protecao": int(p), "teto_de_destreza": _TRACO(t), "requer_forca": _TRACO(f)} for g, n, p, t, f in _rows}
_ok(f"equipamento: os {len(_livro)} escudos são os do livro",
    len(_livro) == 3 and _livro == EQ.get("escudos"), f"livro {_livro} · catálogo {EQ.get('escudos')}")
_ok("equipamento: a Defesa, o uniforme que desliga, o escudo que soma e os dois tetos têm a frase no livro",
    EQ.get("formula") and _norm(EQ["formula"]) in MANN
    and EQ.get("uniforme_desliga_a_protecao_de_energia") is True
    and "Traje e Revestimento desligam a sua proteção passiva de energia amaldiçoada" in MANN
    and EQ.get("escudo_soma_por_cima") is True and "Escudo soma por cima, sempre" in MANN
    and EQ.get("dois_tetos") == "vale o menor" and "com teto de Destreza diferente, vale o menor dos dois" in MANN,
    str({k: EQ.get(k) for k in ("formula", "uniforme_desliga_a_protecao_de_energia", "escudo_soma_por_cima", "dois_tetos")}))

print("\nO TEXTO DO CATÁLOGO, CONTRA O LIVRO")
# B21, achado na v0.246 do sistema: com o texto velho do Rápido no catálogo, tudo saía verde, porque o
# catálogo só conferia nome e contagem. Aqui cada frase que o catálogo diz ter tirado do livro tem de
# estar no livro. O `pdftotext -layout` intromete no meio da frase o nome da coluna vizinha, o número da
# página e às vezes uma palavra dentro de outra ("deslocaPróprio mesmento"), então a comparação não é por
# igualdade: todo caractere da frase do catálogo tem de aparecer, na ordem, numa janela do livro, e a
# intromissão tem três tetos, medidos nas 14 frases reais que o PDF parte (no máximo 3 cortes, 11 caracteres
# num corte, 22 no total) e folgados para 4, 20 e 30. Sem os tetos, uma palavra trocada passa: as letras
# dela se espalham pelo texto que vem depois (a mutação "próximo turno" -> "turno seguinte" dava 10 cortes
# e 86 caracteres). Frase do catálogo que difere do livro em uma palavra deixa caractere sem par e reprova.
import difflib
_MAX_CORTES, _MAX_CORTE, _MAX_TOTAL = 4, 20, 30

def _frase_no_livro(txt):
    v = _norm(txt)
    if v in MANN:
        return True, "igual ao livro"
    pos = []
    for tam in (24, 14):
        pos = [m.start() for m in re.finditer(re.escape(v[:tam]), MANN)]
        if pos:
            break
    if not pos:
        return False, "a frase não começa em lugar nenhum do livro"
    pior = None
    for i in pos:
        jan = MANN[i:i + len(v) + _MAX_TOTAL + 30]
        blocos = [b for b in difflib.SequenceMatcher(None, v, jan, autojunk=False).get_matching_blocks() if b.size]
        soltos = len(v) - sum(b.size for b in blocos)
        cortes = [g for g in (blocos[k + 1].b - blocos[k].b - blocos[k].size for k in range(len(blocos) - 1)) if g > 0]
        if (soltos == 0 and len(cortes) <= _MAX_CORTES and max(cortes, default=0) <= _MAX_CORTE
                and sum(cortes) <= _MAX_TOTAL):
            return True, f"{len(cortes)} corte(s) do PDF, {sum(cortes)} caractere(s)"
        if pior is None or soltos < pior[0]:
            pior = (soltos, len(cortes), sum(cortes))
    return False, f"{pior[0]} caractere(s) da frase sem par no livro, {pior[1]} corte(s) e {pior[2]} caractere(s) do livro no meio"

# Só entram os campos que são frase do livro. Os outros textos do catálogo (`embutido`, `alcance`, `nota`
# das Formas, o `excecao` das Melhorias) são anotação nossa, escrita sem acento, e não têm par no livro.
for _tab, _campo in (("melhorias", "efeito"), ("restricoes", "o_que_muda"), ("pericias", "descricao"),
                     ("origens", "em_uma_linha"), ("caminhos", "em_uma_linha")):
    _res = {n: _frase_no_livro(e[_campo]) for n, e in CAT[_tab].items()
            if isinstance(e, dict) and isinstance(e.get(_campo), str)}
    _mal = {n: d for n, (o, d) in _res.items() if not o}
    _ok(f"as {len(_res)} frases de {_tab}.{_campo} estão no livro", not _mal,
        "; ".join(f"{n}: {d}" for n, d in _mal.items()))

# controles: o conferidor tem de aceitar a intromissão do PDF e reprovar uma palavra trocada
_abre = CAT["melhorias"]["Abre Ferida"]["efeito"]
_ok("controle: aceita a frase que o PDF partiu (Abre Ferida) mesmo ela não sendo igual ao livro",
    _norm(_abre) not in MANN and _frase_no_livro(_abre)[0])
_ok("controle: reprova o −2 trocado por −3", not _frase_no_livro(_abre.replace("−2", "−3"))[0])
_ok("controle: reprova uma palavra trocada no meio da frase",
    not _frase_no_livro(CAT["restricoes"]["Sem Volta"]["o_que_muda"].replace("próximo turno", "turno seguinte"))[0])

print("\nTRAVAS DE ESTRUTURA")
sem_pericia = [a for a in CAT["atributos"]["lista"]
               if not any(v["atributo"] == a for v in CAT["pericias"].values())]
ok = sem_pericia == ["Constituição"]
if not ok: falhas.append("Constituição deveria ser o unico atributo sem pericia")
print(f"  [{'OK' if ok else 'FALHA'}] Constituição e o unico atributo sem pericia (achei: {sem_pericia})")
tr = [t for t in CAT["trilhas"].values()]
ok = all(tr.count(c) == 3 for c in CAT["caminhos"])
if not ok: falhas.append("nem todo Caminho tem 3 Trilhas")
print(f"  [{'OK' if ok else 'FALHA'}] cada um dos 5 Caminhos tem exatamente 3 Trilhas")

print(f"\n{'TUDO VERDE' if not falhas else str(len(falhas)) + ' FALHA(S): ' + '; '.join(falhas)}")
sys.exit(1 if falhas else 0)
