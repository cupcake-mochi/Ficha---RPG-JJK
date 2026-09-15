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
