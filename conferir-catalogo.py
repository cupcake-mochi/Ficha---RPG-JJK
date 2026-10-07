# -*- coding: utf-8 -*-
"""O catálogo contra o livro: todo nome, número e frase do catalogo-projeto-m.json tem par no manual.txt.

Nasceu de um bug real (a tabela de Famílias tinha 'Area' e as Melhorias apontavam para 'Área'), e cresceu até
conferir o catálogo inteiro contra o livro. 04/10/2026: o livro passou a ser a candidata reconstruída, e o
manual.txt sai do LIVRO-COMPLETO.md (extrair-manual.py), com os títulos marcados e as tabelas uma fileira por linha.
As checagens foram reescritas para esse texto: o que antes tolerava a quebra do pdftotext agora compara tabela com
tabela e frase com frase, sem folga. O leitor de seção é o livro.py.

O catálogo é montado a partir do livro, e este validador lê o livro por outro caminho: conta títulos, lê as tabelas
pela primeira célula e procura cada frase inteira. Cada número tem a frase ou a tabela dele no manual.txt.
"""
import json, re, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import livro as Lv

CAT = json.load(open("catalogo-projeto-m.json", encoding="utf-8"))
MAN = " ".join(Lv.texto().split())
falhas = []


def _ok(nome, cond, detalhe=""):
    print(f"  [{'OK' if cond else 'FALHA'}] {nome}" + (f"  <- {detalhe}" if not cond and detalhe else ""))
    if not cond:
        falhas.append(nome)


def _norm(s):
    return " ".join(str(s).split())


def tem(frase):
    return _norm(frase) in MAN


def cap(t):
    S = Lv.secao(t)
    if not S:
        raise SystemExit(f"o manual.txt nao tem o capitulo {t!r}")
    return S


def sec(t, dentro, n=0):
    return Lv.secao(t, n, dentro=dentro)


def tab(S, primeira):
    return Lv.tabela(S, primeira)[1]


def titulos_de(S, nivel):
    return [l.lstrip("#").strip() for l in S if Lv.nivel(l) == nivel]


C2, C3, C4, C5 = cap("2. Regras gerais"), cap("3. Dano e recuperação"), cap("4. Criar um personagem"), cap("5. Origens e Legados")
C6, C7, C8, C9 = cap("6. Caminhos e Trilhas"), cap("7. Perícias e Ofícios"), cap("8. Equipamento"), cap("9. Progressão")
C10, C11 = cap("10. Fundamento"), cap("11. Catálogo de criação")
_EXT = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8,
        "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "catorze": 14, "quinze": 15}

print("INTEGRIDADE REFERENCIAL")
for nome, itens, campo, dono in (("toda Melhoria aponta para uma Família que existe", CAT["melhorias"], "familia", CAT["familias"]),
                                 ("toda Forma aponta para uma Família que existe", CAT["formas"], "familia", CAT["familias"]),
                                 ("toda perícia aponta para um atributo que existe", CAT["pericias"], "atributo", CAT["atributos"]["lista"])):
    orfas = sorted({v[campo] for v in itens.values() if v.get(campo) and v[campo] not in dono})
    _ok(nome, not orfas, str(orfas))
_ok("toda Trilha aponta para um Caminho que existe", set(CAT["trilhas"].values()) <= set(CAT["caminhos"]))

print("\nCONTAGENS DO LIVRO")
m = re.search(r"Elas se dividem em (\w+) Famílias\.", MAN)
_ok(f"Famílias: {len(CAT['familias'])}, e o livro diz {m.group(1) if m else None}", bool(m) and _EXT[m.group(1)] == len(CAT["familias"]))
m = re.search(r"As (\w+) condições classificadas", MAN)
_ok(f"condições: {len(CAT['condicoes'])}, e o livro diz {m.group(1) if m else None}", bool(m) and _EXT[m.group(1).lower()] == len(CAT["condicoes"]))
m = re.search(r"Escolha um dos (\w+) Caminhos e, no nível 2, uma de suas (\w+) Trilhas\.", MAN)
_ok(f"Caminhos: {len(CAT['caminhos'])}, e o livro diz {m.group(1) if m else None}", bool(m) and _EXT[m.group(1)] == len(CAT["caminhos"]))
_ok(f"Trilhas: {len(CAT['trilhas'])}, {m.group(2) if m else None} por Caminho",
    bool(m) and all(list(CAT["trilhas"].values()).count(c) == _EXT[m.group(2)] for c in CAT["caminhos"]))
_per_livro = [t.split(" · ")[0] for g in titulos_de(C7, 3) for t in titulos_de(sec(g, C7), 4)
              if g.startswith(("Perícias", "Investigação", "Ambiente", "Percepção"))]
_ok(f"perícias: as {len(CAT['pericias'])} do catálogo são os {len(_per_livro)} títulos de perícia do livro",
    sorted(_per_livro) == sorted(CAT["pericias"]), str(sorted(set(_per_livro) ^ set(CAT["pericias"]))))
_of = [f[0] for f in tab(C7, "Ofício")]
_ok(f"ofícios: os {len(CAT['oficios'])} do catálogo são as {len(_of)} linhas da tabela Ofício", _of == list(CAT["oficios"]))

print("\nPERÍCIAS, OFÍCIOS E ATRIBUTOS")
_at = {}
for g in titulos_de(C7, 3):
    S = sec(g, C7)
    intro = re.search(r"As perícias desta seção usam (\w+)\.", " ".join(Lv.paragrafos(S, ate_subtitulo=True)))
    for t in titulos_de(S, 4):
        if " · " in t:
            _at[t.split(" · ")[0]] = t.split(" · ")[1]
        elif intro:
            _at[t] = intro.group(1)
_ok("o atributo de cada perícia é o do título dela, ou o da abertura da seção",
    all(_at.get(n) == v["atributo"] for n, v in CAT["pericias"].items()), str({n: (_at.get(n), v["atributo"]) for n, v in CAT["pericias"].items() if _at.get(n) != v["atributo"]}))
_ok("o atributo padrão de cada ofício é o da tabela", {f[0]: f[1] for f in tab(C7, "Ofício")} == CAT["oficios_atributo"])
a = CAT["atributos"]
m = re.search(r"Distribua (\d+) pontos entre " + ", ".join(a["lista"][:-1]) + f" e {a['lista'][-1]}\\. .{{0,80}}?Nenhum pode começar abaixo de (\\d) ou acima de (\\d)\\.", MAN)
mx = re.search(r"O máximo de cada atributo é (\d+);", MAN)
_ok("atributos: a lista, os pontos da criação, o teto da criação e a escala são os do livro",
    bool(m and mx) and int(m.group(1)) == a["criacao"]["pontos"] and int(m.group(3)) == a["criacao"]["teto_por_atributo"]
    and [int(m.group(2)), int(mx.group(1))] == a["escala"])
_ok("o número é o modificador: 'Força 3 fornece +3'", tem("Força 3 fornece +3, sem uma conversão adicional."))

print("\nCAMINHOS E TRILHAS")
_menu = [f[0] for f in tab(C4, "Caminho")]
_ok("os Caminhos do catálogo são os da tabela de Criar um personagem, na ordem", _menu == list(CAT["caminhos"]), str(_menu))
_fora_vi = CAT["fora_do_livro"].get("vida_inicial_da_vanguarda", {}).get("valor")
for c, d in CAT["caminhos"].items():
    S = Lv.secao(c, dentro=C6)
    txt = " ".join("\n".join(S).split())
    fil = {f[0]: f[1] for cab, fs in Lv.tabelas(S) for f in ([cab] if cab and cab[0] == "Vida inicial" else []) + fs if len(f) == 2}
    vi = next((v for k, v in fil.items() if k in ("Vida no nível 1", "Vida inicial")), None)
    vn = next((v for k, v in fil.items() if k.startswith("Vida") and k not in ("Vida no nível 1", "Vida inicial", "Vida máxima")), None)
    pe = next((v for k, v in fil.items() if k.startswith("PE")), None)
    vi_ok = (Lv.numero(vi) == d["vida_inicial"]) if vi else (d["vida_inicial"] == _fora_vi)
    _ok(f"{c}: vida {d['vida_inicial']} + {d['vida_por_nivel']} por nível, {d['pe_por_nivel']} PE por nível" +
        ("" if vi else " (a vida inicial vem de fora_do_livro: o livro não traz)"),
        vi_ok and Lv.numero(vn) == d["vida_por_nivel"] and Lv.numero(pe) == d["pe_por_nivel"], f"{vi} · {vn} · {pe}")
    _ok(f"{c}: as perícias fixas {d['pericias_fixas']} e os atributos naturais {d['atributos_naturais']} estão na tabela",
        all(p in txt for p in d["pericias_fixas"] + d["atributos_naturais"]))
    arma = next((v for k, v in fil.items() if k in ("Armas", "Treino de arma", "Armas treinadas")), "")
    _ok(f"{c}: treina {d['armas']}",
        bool(re.search(r"treze categorias|todas as categorias", arma, re.I)) == (d["armas"] == "todas")
        and (d["armas"] == "todas" or bool(re.search(r"Armas? de Fogo e Balestra", arma))), arma)
for t, c in CAT["trilhas"].items():
    i_t = [i for i in Lv.titulos(t) + Lv.titulos(t + ": Yumi")]
    i_c = Lv.titulos(c)[0]
    prox = min([Lv.titulos(x)[0] for x in CAT["caminhos"] if Lv.titulos(x)[0] > i_c] + [Lv.titulos("7. Perícias e Ofícios")[0]])
    _ok(f"a Trilha {t} é uma seção do {c}", any(i_c < i < prox for i in i_t))

print("\nTESTES DE RESISTÊNCIA")
trs = {f[0]: f[1] for f in tab(sec("Testes de Resistência", C2), "TR")}
_ok("os 4 TRs e os atributos deles são os da tabela",
    all(k in trs and all(x in trs[k] for x in v["atributo"]) for k, v in CAT["testes_de_resistencia"].items() if isinstance(v, dict)) and len(trs) == 4, str(trs))
_ok("o TR treinado soma a maestria", tem("TR treinado: d20 + atributo do TR + maestria.") and CAT["testes_de_resistencia"]["bonus_se_treinado"] == "maestria")
_ok("dois TRs treinados na criação, um da Origem e um do Caminho",
    tem("Você recebe um TR treinado pela Origem e outro pelo Caminho.") and CAT["testes_de_resistencia"]["treinados_na_criacao"] == 2)

print("\nFAMÍLIAS, FORMAS, MELHORIAS, CONDIÇÕES E RESTRIÇÕES")
_ok("as Famílias e o que cada uma faz são os da tabela", {f[0]: f[1].rstrip(".") for f in tab(sec("Famílias", C10), "Família")} == CAT["familias"])
_fa = {f[0]: f for f in tab(sec("Formas de ataque", C10), "Forma")}
_fb = {f[0]: f for f in tab(sec("Formas de amparo e Efeito", C10), "Forma")}
_peso = {"0": None, "Leve": "Leve", "Média": "Media", "Pesada": "Pesada"}
_ok("as Formas e o preço de cada uma são os das duas tabelas",
    set(_fa) | set(_fb) == set(CAT["formas"]) and all(_peso[{**_fa, **_fb}[n][1]] == f["custa"] for n, f in CAT["formas"].items()))
_ok("Fechar Área tira Explosão, Aura, Cone e Linha; fechar Amparo tira Cura, Apoio e Onda",
    tem("Fechar Área também impede Explosão, Aura, Cone e Linha. Fechar Amparo impede Cura, Apoio e Onda.")
    and all(CAT["formas"][n]["familia"] == "Área" for n in ("Explosão", "Aura", "Cone", "Linha"))
    and all(CAT["formas"][n]["familia"] == "Amparo" for n in ("Cura", "Apoio", "Onda"))
    and all(CAT["formas"][n]["familia"] is None for n in ("Projétil", "Toque", "Efeito")))
_ok("Toque e Aura trazem o Corpo a Corpo embutido", tem("As duas já incluem a Restrição Corpo a Corpo, que devolve o valor Médio.")
    and {n for n, f in CAT["formas"].items() if f.get("embutido")} == {"Toque", "Aura"})
# as Melhorias do livro: cada título de quarto nível do Catálogo de criação que abre com "Preço:" ou traz o peso no nome,
# até as Restrições
_mel_livro, fam = {}, None
_corte = Lv.titulos("Restrições de conjuração")[0]
_ini = Lv.titulos("11. Catálogo de criação")[0]
for i in range(_ini, _corte):
    l = Lv.linhas()[i]
    if Lv.nivel(l) == 3 and l.lstrip("#").strip() in CAT["familias"]:
        fam = l.lstrip("#").strip()
    if Lv.nivel(l) == 4:
        t = l.lstrip("#").strip()
        par = next((x for x in Lv.linhas()[i + 1:i + 4] if x.strip()), "")
        for n, p in re.findall(r"([^/]+?)\s+-\s+(Leve|Média|Pesada)", t):
            _mel_livro[n.strip()] = (fam, _peso[p])
        mp = re.match(r"Preço: (Leve|Média|Pesada|Nível da condição)\.", par)
        if mp:
            _mel_livro[t] = (fam, _peso.get(mp.group(1), "VARIAVEL"))
_mel_livro["Efeito Próprio"] = (None, "MESTRE")
_ok(f"as {len(CAT['melhorias'])} Melhorias do catálogo são as {len(_mel_livro)} do livro", set(_mel_livro) == set(CAT["melhorias"]),
    str(sorted(set(_mel_livro) ^ set(CAT["melhorias"]))))
_dif = {n: (_mel_livro.get(n), (m_["familia"], m_["peso"])) for n, m_ in CAT["melhorias"].items() if _mel_livro.get(n) != (m_["familia"], m_["peso"])}
_ok("a Família e o peso de cada Melhoria são os do livro", not _dif, str(_dif))
_cond = {}
for t, nv in (("Condições leves", "Leve"), ("Condições médias", "Media"), ("Condições pesadas", "Pesada")):
    for x in titulos_de(sec(t, C3), 4):
        if x not in ("Remoção", "Testes de saída"):
            _cond[x] = nv
_ok("as condições e o nível de cada uma são os do livro", _cond == CAT["condicoes"], str(set(_cond.items()) ^ set(CAT["condicoes"].items())))
_res_livro = {}
for i in range(_corte, Lv.titulos("Talentos de Categoria 1")[0]):
    l = Lv.linhas()[i]
    if Lv.nivel(l) == 4:
        par = next((x for x in Lv.linhas()[i + 1:i + 4] if x.strip()), "")
        md = re.match(r"Devolução: (Leve ou Média|Leve|Média)\.", par)
        if md:
            _res_livro[l.lstrip("#").strip()] = md.group(1).replace("Média", "Media")
_ok(f"as {len(CAT['restricoes'])} Restrições e a devolução de cada uma são as do livro",
    _res_livro == {n: r["devolve"] for n, r in CAT["restricoes"].items()}, str(set(_res_livro.items()) ^ {(n, r["devolve"]) for n, r in CAT["restricoes"].items()}))

print("\nFUNDAMENTO")
F = CAT["fundamento"]
from math import ceil
_pp = tab(sec("Pontos e preços", C10), "Classe")
_conta = [[str(c), str(3 * c), str(ceil(c / 2)), str(c), str(ceil(c * 1.5))] for c in range(1, 8)]
_ok("os pontos e os preços Leve, Média e Pesada de cada Classe reproduzem a tabela Pontos e preços",
    [[f[0], f[2], f[3], f[4], f[5]] for f in _pp if len(f) == 6] == _conta)
_q = {f[0]: (Lv.numero(f[1]), Lv.numero(f[2]), f[3]) for f in tab(sec("Quantidade de peças", C10), "Classe")}
_ok("as Melhorias por Classe, as duas Restrições e a devolução de 2 × Classe são as da tabela Quantidade de peças",
    {k: v[0] for k, v in _q.items()} == F["melhorias_por_classe"] and all(v[1] == F["restricoes_por_feitico"] and v[2] == "2 × Classe" for v in _q.values())
    and F["restricao_teto_devolucao"] == "2 x Classe")
for chave, frase in (("pontos_por_feitico", "Os pontos e o PE são 3 × Classe."),
                     ("ponto_nao_gasto", "Num feitiço de dano, cada ponto do saldo vira 1d8."),
                     ("desconto_familia_livre", "Uma Melhoria de Família Livre recebe desconto igual à metade da Classe, arredondada para cima. Seu preço final nunca fica abaixo de 1 ponto."),
                     ("formas_sem_desconto", "Formas não recebem desconto de Família Livre."),
                     ("restricao_paga", "Restrição paga peças, incluindo a Forma."),
                     ("acrescentam_dano_e_contam_no_teto", "Salto, Queima e Estilhaço acrescentam os dados que suas entradas indicam."),
                     ("dividem_os_dados", "Rajada e Mais Um dividem a quantidade de dados disponível."),
                     ("teto_de_dados", "o total não pode passar de 4 × Classe em d8"),
                     ("liberacao", "acrescente +Classe em d8 ao dano da montagem"),
                     ("arredondamento", "Arredonde os preços para cima.")):
    _ok(f"fundamento.{chave} tem a frase dele no livro", chave in F and tem(frase), frase)
_ok("duas Famílias Livres e três Fechadas", tem("Escolha duas Livres e três Fechadas para o Fundamento.") and (F["familias_livres"], F["familias_fechadas"]) == (2, 3))
_ok("Restrição nunca devolve Pesada: as devoluções usam o preço Leve ou Médio",
    tem("As devoluções abaixo usam o preço Leve ou Médio da Classe do feitiço.") and F["restricao_nunca_devolve"] == "Pesada")
_ok("no nível 2: Classe 1, três espaços conhecidos e dois feitiços de Classe 0",
    tem("No nível 2, você tem três espaços conhecidos, além de dois feitiços de Classe 0.") and F["nivel_2"] == {"classe": 1, "feiticos_classe_0_gratis": 2, "feiticos_conhecidos": 3})
_ok("as Melhorias que acrescentam ou dividem dados existem no catálogo",
    all(x in CAT["melhorias"] for x in F["acrescentam_dano_e_contam_no_teto"] + F["dividem_os_dados"]))

print("\nORIGENS, SEM TÉCNICA, ROTAS E LEGADOS")
_or = {f[0]: f for f in tab(C5, "Origem")}
_ok("as Origens, a frase de cada uma e a criação de capacidades são as da tabela",
    list(_or) == list(CAT["origens"]) and all(_or[o][1] == v["em_uma_linha"] and _or[o][2].rstrip(".") == v["criacao"] for o, v in CAT["origens"].items()))
_ok("Corpo Amaldiçoado e Restrição Celestial são as de seleção própria",
    tem("O Corpo Amaldiçoado e os ramos da Restrição Celestial têm condições próprias de seleção.")
    and {o for o, v in CAT["origens"].items() if v.get("especial")} == {"Corpo Amaldiçoado", "Restrição Celestial"})
for o, v in CAT["origens"].items():
    m = re.search(r"Perícia da Origem: escolha (.+?)\.", " ".join(Lv.paragrafos(Lv.secao(o, dentro=C5))))
    _ok(f"{o}: as perícias da Origem são as da entrada", bool(m) and [p.strip() for p in re.split(r", | ou ", m.group(1))] == v.get("pericias"))
_ok("Sem Técnica vale nas cinco primeiras Origens e ocupa um Legado",
    tem("Sem Técnica é uma opção para as cinco primeiras Origens. Ela ocupa um Legado") and CAT["sub_origem"]["Sem Técnica"]["origens"] == list(CAT["origens"])[:5])
_rot = {r["origem"]: r["rota"] for r in CAT["rotas_de_criacao"]}
_ramos = titulos_de(Lv.secao("Restrição Celestial", dentro=C5), 4)
_ok("as rotas: Fundamento nas cinco e no ramo Corpo pela Técnica; Técnica Marcial no Corpo Amaldiçoado e no ramo Sem Energia",
    all(_rot.get(o) == "Fundamento" for o in list(CAT["origens"])[:5]) and _ramos[:2] == ["Corpo pela Técnica", "Sem Energia"]
    and _rot.get("Restrição Celestial · corpo pela técnica") == "Fundamento" and _rot.get("Restrição Celestial · sem energia") == "Técnica Marcial"
    and _rot.get("Corpo Amaldiçoado") == "Técnica Marcial" and _or["Corpo Amaldiçoado"][2].startswith("Técnica Marcial"))
_ok("as rotas pela Técnica Marcial são as da tabela de Rotas de criação",
    tem("Técnica Marcial | Corpo Amaldiçoado. | Katas.") and tem("Técnica Marcial | Restrição Celestial sem energia. | Katas.") and tem("Sem Técnica | Personagem com essa sub-origem. | Manejos."))
_ok("os três tipos de Legado e a frase de cada um são os da tabela",
    {f[0].replace("Legado ", "").replace("de ", ""): [f[1]] for f in tab(sec("Legados", C5), "Tipo")} == CAT["legados_formatos"])
# o trecho de cada Origem: do título dela até o título da próxima Origem (ou de Criar um Legado)
_i_or = [(o, next(i for i in Lv.titulos(o) if Lv.linhas()[i].startswith("### "))) for o in CAT["origens"]] + [("fim", Lv.titulos("Criar um Legado")[0])]
_trecho_or = {o: "\n".join(Lv.linhas()[i:_i_or[k + 1][1]]) for k, (o, i) in enumerate(_i_or[:-1])}
_leg_mal = [(o, t, n) for o, ts in CAT["legados"].items() for t, ns in ts.items() for n in ns
            if not re.search(r"(?:^|\n)" + re.escape(n) + r"\. ", _trecho_or[o])]
_ok(f"os {sum(len(ns) for ts in CAT['legados'].values() for ns in ts.values())} Legados abrem um parágrafo da Origem deles", not _leg_mal, str(_leg_mal[:5]))
_ok("toda Origem tem Legado narrativo e de rolagem", all({"narrativo", "rolagem"} <= set(ts) for ts in CAT["legados"].values()))

print("\nPROGRESSÃO")
PR = CAT["progressao"]
_tab = [f for t in ("Progressão dos níveis 1 a 15", "Progressão dos níveis 16 a 30") for f in tab(sec(t, C9), "Nível")]
_col = ["maestria", "espacos", "refino", "classe", "passiva", "classe0"]
_ruim = [f[0] for f in _tab if [PR["tabela_impressa"].get(f[0], {}).get(c) for c in _col] != [int(x) for x in f[1:7]]]
_ok("progressão: as 30 linhas das duas tabelas, coluna a coluna", len(_tab) == 30 and not _ruim and len(PR["tabela_impressa"]) == 30, str(_ruim))
_xp = {}
for faixa, v in tab(sec("Recompensas e custos", C9), "Nível atual"):
    ns = [int(x) for x in re.findall(r"\d+", faixa)]
    for n in range(ns[0], (ns[1] if len(ns) > 1 else ns[0]) + 1):
        _xp[str(n)] = str(Lv.numero(v)) if Lv.numero(v) else "—"
_ok("o XP para sair de cada nível é o da tabela", all(PR["tabela_impressa"][n]["xp"] == _xp.get(n, "—") for n in PR["tabela_impressa"] if int(n) >= 2),
    str({n: (PR["tabela_impressa"][n]["xp"], _xp.get(n)) for n in PR["tabela_impressa"] if int(n) >= 2 and PR["tabela_impressa"][n]["xp"] != _xp.get(n, "—")}))
m = re.search(r"Nos níveis ((?:\d+, )+\d+ e \d+), receba \+1 ponto de atributo, \+1 de Refino e \+1 espaço de repertório\.", MAN)
_ok("os marcos e o que todo marco dá são os do livro",
    bool(m) and [int(x) for x in re.findall(r"\d+", m.group(1))] == PR["marcos"] and PR["marco_entrega"] == "+1 ponto de atributo, +1 de Refino e +1 espaço de repertório")
_ok("a Liberação Máxima nos níveis 10, 20 e 30", tem("Você recebe uma no nível 10, outra no 20 e outra no 30.") and list(PR["liberacao_maxima"]) == ["10", "20", "30"])
_ok("a Integridade é a do livro", tem("Integridade máxima do personagem = 20 + (Essência + 5) × (nível − 1).") and PR["formulas"]["integridade"].startswith("20 + (Essência + 5) * (nivel - 1)"))
_ok("a maestria sobe nos níveis 10, 18 e 26", tem("A maestria sobe nos níveis 10, 18 e 26.") and "(10,18,26)" in PR["formulas"]["maestria"])
_ok("os espaços são 2 + metade do nível + marcos", tem("Espaços = 2 + metade do nível, arredondada para baixo + marcos alcançados.") and PR["formulas"]["espacos"].startswith("2 + (nivel // 2) + marcos"))
_ok("a ficha começa no nível 2 e vai ao 30", tem("Uma ficha nova começa no nível 2.") and tem("O nível 30 encerra esta progressão.")
    and (CAT["_meta"]["nivel_inicial"], CAT["_meta"]["nivel_maximo"]) == (2, 30) and PR["faixa_jogavel"] == [2, 30])
_ok("Caminho nos níveis 2, 7, 15, 23 e 30; Trilha nos 2, 11, 19 e 27",
    tem("Você recebe habilidades de Caminho nos níveis 2, 7 e 15 e de Trilha nos níveis 2 e 11.") and tem("Receba habilidades de Caminho no 23 e no 30, e de Trilha no 19 e no 27.")
    and PR["caminho_nos_niveis"] == [2, 7, 15, 23, 30] and PR["trilha_nos_niveis"] == [2, 11, 19, 27])
_ok("o limiar do feito é o 20", tem(PR["limiar_do_feito"]["regra"]) and PR["limiar_do_feito"]["nivel"] == 20)

print("\nEQUIPAMENTO")
ED, EQ = CAT["equipamento_defesa"], CAT["equipamento"]
_n = lambda s: None if s in ("Nenhuma", "Sem teto", "—") else Lv.numero(s)
for nome, fil, pref in (("Traje", tab(sec("Trajes", C8), "Degrau"), "Traje "), ("Revestimento", tab(sec("Revestimentos e escudos", C8), "Degrau"), "Revestimento "),
                        ("escudo", tab(sec("Revestimentos e escudos", C8), "Escudo"), "")):
    livro = {pref + f[0]: {"protecao": _n(f[1]), "teto_de_destreza": _n(f[2]), "requer_forca": _n(f[3])} for f in fil}
    cat = {k: v for k, v in {**ED["uniformes"], **ED["escudos"]}.items() if k in livro}
    vol = {pref + f[0]: _n(f[4]) for f in fil}
    _ok(f"equipamento: os {len(livro)} degraus de {nome} (proteção, teto, Força e Volume) são os do livro",
        livro == cat and all(EQ["volume"]["de_uniforme_e_escudo"][k] == v for k, v in vol.items()), f"{livro} · {cat}")
_ok("a Defesa, o uniforme que substitui a proteção passiva, o escudo que soma e os dois tetos têm a frase no livro",
    tem("Defesa = 10 + Destreza permitida + proteção.") and tem("Enquanto usar um uniforme, a proteção dele substitui a proteção passiva da sua rota.")
    and tem("Some a proteção de um escudo empunhado à proteção que já utiliza") and tem("Se duas peças tiverem tetos diferentes, use o menor."))
# 07/10/2026: a arma sem a Força segue a decisão do Mizuki (desvantagem no ataque e metade do deslocamento, sem mexer na
# Defesa), que mora no fora_do_livro enquanto o livro traz a frase antiga. No dia em que o livro mudar, a frase antiga
# some, esta checagem acende e a regra sai do fora_do_livro
_asf = CAT["fora_do_livro"].get("arma_sem_a_forca", {})
_ok("sem a Força: uniforme e escudo não dão proteção (livro); a arma dá desvantagem e metade do deslocamento (fora do livro, que ainda diz a frase antiga)",
    tem("Sem o valor exigido, você não pode prepará-la nem receber sua proteção ou seus benefícios de uso.")
    and tem(_asf.get("o_livro_diz", "?")) and "desvantagem nos ataques" in _asf.get("regra", "")
    and "metade" in _asf.get("regra", "") and "continua somando" in _asf.get("regra", ""))
_armas_livro = {}
for g in titulos_de(C8, 3):
    for cat_ in titulos_de(sec(g, C8), 4):
        for cab, fil in Lv.tabelas(sec(cat_, C8)):
            if cab[:2] == ["Arma", "Mãos"]:
                for f in fil:
                    _armas_livro[re.sub(r"\s*\(.*\)$", "", f[0])] = (cat_, f)
_mal = []
for n, a_ in EQ["armas"].items():
    if n not in _armas_livro:
        _mal.append(n); continue
    cat_, f = _armas_livro[n]
    props = [("Alcance" if p.startswith("Alcance") else "Longo Alcance" if p.startswith("Longo Alcance") else p) for p in f[3].split(" · ")]
    la = re.search(r"Longo Alcance (\d+)/(\d+) m", f[3])
    if (cat_, int(f[1]), f[2].split(" ")[0], props, _n(f[4]), _n(f[5]), Lv.numero(f[6].split(" / ")[-1]), [int(la.group(1)), int(la.group(2))] if la else None) != \
       (a_["categoria"], a_["mao"], a_["dado"], a_["propriedades"], a_["requer_forca"], a_["volume"], a_["preco"], a_["longo_alcance"]):
        _mal.append(n)
_ok(f"armas: as {len(_armas_livro)} das tabelas do livro são as {len(EQ['armas'])} do catálogo, coluna a coluna",
    not _mal and set(_armas_livro) == set(EQ["armas"]), str(_mal[:6]))
_listas = {f[0]: [x.strip() for x in re.split(r", | e ", f[1].rstrip("."))] for f in tab(sec("Armas", C8), "Lista")}
_ok("treino: as três listas e as treze categorias são as do livro, e cada arma cai na lista da categoria dela",
    _listas == EQ["treino"]["listas"] and sum(len(v) for v in _listas.values()) == 13
    and all(a_["treino"] == next(l for l, cs in _listas.items() if a_["categoria"] in cs) for a_ in EQ["armas"].values()))
_ok("o conjurador treina Arma de Fogo e Balestra, e as duas são categorias",
    EQ["treino"]["conjurador_treina"] == ["Arma de Fogo", "Balestra"] and all(c in sum(_listas.values(), []) for c in EQ["treino"]["conjurador_treina"]))
_fp = EQ["faixa_de_projetil"]
_ok("as faixas de tiro e de arremesso são as do Longo Alcance de cada arma",
    all(EQ["armas"][n]["longo_alcance"] == v for n, v in _fp["tiro"].items())
    and all(EQ["armas"][n]["longo_alcance"] == _fp["arremesso"]["faixa"] for n in _fp["arremesso"]["armas"])
    and {n for n, a_ in EQ["armas"].items() if a_["longo_alcance"]} == set(_fp["tiro"]) | set(_fp["arremesso"]["armas"]))
_mun = {f[0].split(":")[0]: int(f[1]) for f in tab(sec("Munição", C8), "Arma e carga correspondente")}
_ok("munição: os ataques por carga são os da tabela, as bestas recarregam a cada disparo, e são as armas com Munição",
    all(EQ["municao"][k] == v for k, v in _mun.items()) and tem("Cada besta comporta um virote e precisa ser recarregada depois de cada disparo.")
    and {n for n, a_ in EQ["armas"].items() if "Munição" in a_["propriedades"]} == set(EQ["municao"]))
m = re.search(r"O dado desarmado é (d\d+) com maestria 1, (d\d+) com maestria 2, (d\d+) com maestria 3 e (d\d+) com maestria 4\.", MAN)
_ok("soco: o dado por maestria é o do livro", bool(m) and [EQ["soco_por_maestria"][str(i)] for i in range(1, 5)] == list(m.groups()))
_ok("carga: 5 + Força, sem arredondar, item leve 0,1, e acima do limite não anda",
    tem("Seu limite de carga é 5 + Força, medido em Volume.") and tem("Use o valor da tabela de cada item e some sem arredondar.")
    and tem("Se uma regra indicar apenas “item leve”, use 0,1 Volume") and tem("Acima do limite, você não pode se deslocar com a carga.")
    and EQ["volume"]["limite"] == "5 + Força" and EQ["volume"]["leve"] == 0.1)
_sit = [c for f in tab(sec("Trajes", C8), "Situações") for c in f]
_ok("as oito situações do Traje são as do livro", _sit == EQ["situacoes_do_traje"], str(_sit))
_ac = {f[0]: f[1] for f in tab(sec("Dinheiro e acesso", C8), "Equipamento")}
_ok("o acesso: Revestimento 2 pede Grau 3, o 3 pede Grau 2, e arma de fogo Grau 2",
    all(_ac[k].startswith(v) for k, v in (("Revestimento 2", EQ["grau_minimo"]["Revestimento 2"]), ("Revestimento 3", EQ["grau_minimo"]["Revestimento 3"]),
                                          ("Armas de fogo e sua munição", EQ["grau_minimo"]["Arma de Fogo"]))))
_pp = {f[0]: Lv.numero(f[1]) for f in tab(sec("Preços de proteção", C8), "Peça")}
_ok("os preços de proteção são os da tabela", _pp == EQ["precos_de_protecao"])
_sal = {("Grau " + g if g != "Especial" else g): Lv.numero(v) for g, v in tab(sec("Recompensas da guilda", C9), "Grau")}
_ok("salário: as cinco patentes e o valor por mês são os do livro, e a ficha começa no Grau 4",
    _sal == CAT["patentes"]["salario_por_mes"] and list(_sal)[0] == f"Grau {CAT['_meta']['grau_inicial']}")
_tam = {f[0].lower(): Lv.numero(f[1]) for f in tab(sec("Recompensas e custos", C9), "Missão")}
_des = {f[0]: f[1] for f in tab(sec("Experiência semanal", C9), "Missão na semana") if f[0] != "Seguintes"}
MIS = CAT["missoes"]
_ok("missões: os quatro tamanhos, o desconto da semana, a falha e o arredondamento são os do livro",
    _tam == MIS["tamanho"] and _des == MIS["desconto_da_semana"] and tem("Na falha, o mestre concede metade ou nada")
    and tem("Faça a conta com a fração inteira e arredonde para baixo somente o XP final.") and tem("Quando o resultado for positivo e menor que 1, receba 1 XP."))

print("\nO QUE FICA FORA DO LIVRO")
_conferidas = set(CAT["_meta"]["conferido_contra_o_livro"])
_fora = set(CAT["_meta"].get("fora_do_livro", []))
_soltas = [k for k in CAT if not k.startswith("_") and k not in _conferidas and k not in _fora]
_ok("toda chave do catálogo é conferida contra o livro ou declarada fora dele", not _soltas and _fora <= set(CAT), str(_soltas))
_FL = CAT["fora_do_livro"]
_ok("fora do livro: as missões solo e os multiplicadores têm nome e número, e nenhum repete um tamanho do livro",
    all(isinstance(v, (int, float)) and v > 0 for k in ("missoes_solo", "xp_adicional") for v in _FL[k].values())
    and len(_FL["missoes_solo"]) == 2 and not set(_FL["missoes_solo"]) & {t[0].upper() + t[1:] for t in MIS["tamanho"]})
_ok("fora do livro: a vida inicial da Vanguarda continua fora porque o livro não a traz",
    not any(f[0] in ("Vida inicial", "Vida no nível 1") for _, fs in Lv.tabelas(Lv.secao("Vanguarda", dentro=C6)) for f in fs)
    and CAT["caminhos"]["Vanguarda"]["vida_inicial"] == _FL["vida_inicial_da_vanguarda"]["valor"])
# a regra que o Mizuki decidiu em 04/10/2026 ("Toda vida inicial é a máxima do dado"): o ganho por nível é a média do dado
# para cima, máximo ÷ 2 + 1, então o máximo é 2 × (ganho − 1). Os cinco que o livro numera têm de obedecer, senão a regra
# não é a do livro; e a Vanguarda sai da mesma conta
_dado = {c: 2 * (d["vida_por_nivel"] - 1) for c, d in CAT["caminhos"].items()}
_ok("fora do livro: toda vida inicial é o máximo do dado (12/7 é d12, 8/5 é d8, 6/4 é d6), e a da Vanguarda sai dessa conta",
    all(d["vida_inicial"] == _dado[c] for c, d in CAT["caminhos"].items()) and _dado["Vanguarda"] in (6, 8, 10, 12)
    and _FL["vida_inicial_da_vanguarda"]["valor"] == _dado["Vanguarda"]
    and "máximo do dado" in _FL["vida_inicial_da_vanguarda"]["regra"],
    str({c: (d["vida_inicial"], _dado[c]) for c, d in CAT["caminhos"].items()}))
_ok("nada do fora do livro foi para o livro: o desconto e o arredondamento antigos saíram",
    not {"desconto", "arredondamento_do_xp", "sem_o_requisito_de_forca", "carga_acima_do_limite"} & set(_FL))

print("\nO TEXTO DO CATÁLOGO, CONTRA O LIVRO")
# o manual.txt é texto limpo: cada frase que o catálogo diz ter tirado do livro tem de estar nele, inteira
for _tab_, _campo in (("melhorias", "efeito"), ("restricoes", "o_que_muda"), ("pericias", "descricao"), ("origens", "em_uma_linha")):
    _mal = [n for n, e in CAT[_tab_].items() if isinstance(e, dict) and isinstance(e.get(_campo), str) and not tem(e[_campo])]
    _ok(f"as frases de {_tab_}.{_campo} estão no livro", not _mal, str(_mal[:6]))
_mal = [n for n, t in CAT["oficios"].items() if not tem(t.rstrip("."))]
_ok("as aplicações de cada ofício estão no livro", not _mal, str(_mal))
# controles: a comparação reprova uma palavra trocada e um número trocado
_abre = CAT["melhorias"]["Abre Ferida"]["efeito"]
_ok("controle: aceita a frase de Abre Ferida como está no catálogo", tem(_abre))
_ok("controle: reprova o −2 trocado por −3", not tem(_abre.replace("-2", "-3").replace("−2", "−3")))
_ok("controle: reprova uma palavra trocada no meio da frase", not tem(CAT["restricoes"]["Sangra"]["o_que_muda"].replace("Classe", "Nível", 1)))

print("\nTRAVAS DE ESTRUTURA")
sem_pericia = [a_ for a_ in CAT["atributos"]["lista"] if not any(v["atributo"] == a_ for v in CAT["pericias"].values())]
_ok(f"Constituição é o único atributo sem perícia (achei: {sem_pericia})", sem_pericia == ["Constituição"])
_ok(f"cada um dos {len(CAT['caminhos'])} Caminhos tem exatamente 3 Trilhas", all(list(CAT["trilhas"].values()).count(c) == 3 for c in CAT["caminhos"]))

print(f"\n{'TUDO VERDE' if not falhas else str(len(falhas)) + ' FALHA(S): ' + '; '.join(falhas)}")
sys.exit(1 if falhas else 0)
