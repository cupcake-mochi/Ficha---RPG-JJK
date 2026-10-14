# -*- coding: utf-8 -*-
"""Lê do livro o capítulo 5, Origens, e grava em ficha-v01/origens-do-livro.json.

    python3 ficha-v01/extrair_origens.py            # lê o manual.txt e regrava o arquivo
    python3 ficha-v01/extrair_origens.py --confere  # só compara o arquivo com o manual.txt, sem gravar

Por que este arquivo existe (14/10/2026, B46): o livro R45 refez as Origens (item 193 da revisão de regras). Cada uma dá
a base de treinos, uma capacidade marcante e duas menores do catálogo dela; os dois Legados com tipo saíram, e o Legado
de história não tem efeito na ficha. A FICHA PESSOAL ganhou, no dossiê, o menu da marcante e das duas menores com o texto
do livro embaixo, e o painel retrátil da FICHA mostra as três escolhidas. O gerador (ficha_pessoal.py) nunca lê o livro:
lê só este arquivo, que mora no repositório.

O que é cada entrada de `origens` (na ordem do menu de Origem):
  · `menu`: o nome como o menu de Origem da FICHA o escreve (a Restrição Celestial abre nos dois ramos);
  · `pericias`: as quatro da "Perícia da Origem"; `rota`: a frase da criação;
  · `marcantes`: a capacidade central, ou as modalidades (Receptáculo: Coexistência ou Conflito; Descendente: o clã;
    Restrição corporal: o corpo). Cada uma com `texto` (a seção inteira, com os componentes) e `freq`;
  · `menores`: o catálogo, com `exige` quando a entrada diz "Exclusiva <clã>" ou "Requisito: <modalidade>" (o menu filtra
    por ela) e `historia` quando depende de uma história (as duas de Manutenção, que o menu mostra sempre);
  · `legados`: as sugestões de Legado de história da entrada; `oficio` e `ce4`, as caixas que só aquela Origem usa.

Nenhum texto é digitado aqui: cada parágrafo vem do manual palavra por palavra. O que é decisão deste arquivo, e não do
livro, é só a `freq` (a frequência que o espelho da FICHA mostra), tirada da primeira frase que a diz, e a soma 67 das
menores, que o livro dá (8 + 8 + 10 + 7 + 8 + 8 + 2 + 8 + 8) e a extração confere.
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import livro as Lv

SAIDA = os.path.join(AQUI, "origens-do-livro.json")
CAPITULO = "5. Origens"
TOTAL_DE_MENORES = 67
CRIADA = "✎ Criada com o mestre"


def _texto(L):
    """as linhas de um trecho como texto: parágrafos separados por linha em branco, fileiras de tabela juntas"""
    out, tab = [], False
    for l in L:
        if not l.strip():
            tab = False
            continue
        n = Lv.nivel(l)
        if n:
            out.append(l.lstrip("#").strip() + ".")
            tab = False
            continue
        e_tab = " | " in l
        if e_tab and tab:
            out[-1] += "\n" + l
        else:
            out.append(l)
        tab = e_tab
    return "\n\n".join(out)


def _secoes(L):
    """as subseções imediatas de um trecho: [(título, linhas)], pelo nível do primeiro título abaixo do do trecho"""
    n0 = Lv.nivel(L[0])
    filhos = [i for i, l in enumerate(L) if i and Lv.nivel(l) == n0 + 1]
    return [(L[i].lstrip("#").strip(), L[i:(filhos[k + 1] if k + 1 < len(filhos) else len(L))]) for k, i in enumerate(filhos)]


def _corpo(L):
    """o texto de um trecho tirado o título de cima"""
    return _texto(L[1:]).strip()


def _antes_dos_filhos(L):
    n0 = Lv.nivel(L[0])
    fim = next((i for i, l in enumerate(L) if i and Lv.nivel(l) and Lv.nivel(l) <= n0 + 1), len(L))
    return L[1:fim]


FREQ = [
    r"(?:Uma|Duas) vez(?:es)? (?:por|entre|na) (?!tentativa|teste|aplicação)[^,.:;]+",
    r"Maestria vezes por [^,.:;]+",
    r"metade da Constituição, arredondada para baixo, \+1 vezes por cena",
]
# as duas frequências do livro que não cabem na linha do espelho, escritas mais curto
CURTO = {"Metade da Constituição, arredondada para baixo, +1 vezes por cena": "Constituição ÷ 2 + 1 vezes por cena",
         "Uma vez entre o começo de um turno seu e o começo do próximo": "Uma vez entre um turno seu e o próximo"}
# quando o texto não diz quantas vezes, mas diz o momento: o que o espelho da FICHA mostra no lugar da frequência
MOMENTO = [
    (r"\b(?:no|num|durante um|ao concluir um) descanso curto", "No descanso curto"),
    (r"\b(?:no|ao concluir um) descanso longo", "No descanso longo"),
    (r"\bao preparar uma missão", "No preparo da missão"),
    (r"um uso da sua Reserva de Experiência", "Gasta a Reserva de Experiência"),
]


def frequencia(texto):
    """as frequências que o texto diz, na ordem, sem repetir (até duas); sem nenhuma, o momento em que ela vale; sem
    momento, 'Passiva' (o efeito vale sempre)"""
    achadas = []
    for rx in FREQ:
        for m in re.finditer(rx, texto, re.I):
            achadas.append((m.start(), m.group(0)))
    out = []
    for _, f in sorted(achadas):
        f = f[:1].upper() + f[1:]
        if f.lower() not in [x.lower() for x in out]:
            out.append(f)
    if out:
        return " · ".join(CURTO.get(f, f) for f in out[:2])
    for rx, rot in MOMENTO:
        if re.search(rx, texto, re.I):
            return rot
    return "Passiva"


def _paragrafo(L, comeco):
    p = [x for x in Lv.paragrafos(L) if x.startswith(comeco)]
    if len(p) != 1:
        raise SystemExit(f"extrair_origens: devia haver um parágrafo começando por {comeco!r}, achei {len(p)}")
    return p[0]


def _pericias(L):
    p = _paragrafo(L, "Perícia da Origem: ")
    m = re.match(r"Perícia da Origem: escolha ([^.]+?) ou ([^.,]+)\.", p)
    if not m:
        raise SystemExit(f"extrair_origens: a frase da perícia mudou: {p[:120]!r}")
    lista = [x.strip() for x in m.group(1).split(",")] + [m.group(2).strip()]
    if len(lista) != 4:
        raise SystemExit(f"extrair_origens: a Origem devia dar quatro perícias, e dá {lista}")
    resto = p[m.end():].strip()
    rota = re.match(r"Criação: ([^.]+)\.", resto)
    return lista, (rota.group(1) if rota else None)


def _legados(L):
    p = [x for x in Lv.paragrafos(L) if x.startswith("Legados de história: ")]
    return p[0][len("Legados de história: "):] if p else None


def _menores(L, historia=None):
    out = []
    for nome, sub in _secoes(L):
        t = _corpo(sub)
        exige = None
        m = re.match(r"(Exclusiva|Requisito:) ([A-ZÀ-Ý][\wÀ-ÿ]+)\. ", t)
        if m:
            exige = m.group(2)
        out.append({"nome": nome, "texto": t, "freq": frequencia(t[m.end():] if m else t), "exige": exige,
                    "historia": historia})
    return out


def _marcante(nome, L, extra=""):
    t = _corpo(L) + (("\n\n" + extra) if extra else "")
    return {"nome": nome, "texto": t, "freq": frequencia(t)}


def extrai():
    cap = Lv.secao(CAPITULO)
    if not cap:
        raise SystemExit(f"extrair_origens: o manual.txt não tem o capítulo {CAPITULO!r}")
    fonte = json.load(open(os.path.join(os.path.dirname(AQUI), "manual-fonte.json"), encoding="utf-8"))
    sec = dict(_secoes(cap))
    _, tab = Lv.tabela(cap, "Origem")
    frase = {o: (p, c) for o, p, c in tab}
    origens = []

    def entrada(menu, livro, L, marcantes, menores, **k):
        per, rota = _pericias(L)
        return dict({"menu": menu, "livro": livro, "personagem": frase[livro][0], "criacao": frase[livro][1],
                     "pericias": per, "rota": rota, "legados": _legados(L), "marcantes": marcantes, "menores": menores,
                     "sem_tecnica": "Fundamento ou Sem Técnica" in frase[livro][1], "oficio": False, "ce4": False}, **k)

    # as cinco primeiras: uma marcante (ou as modalidades) e o catálogo "Menores do/da <Origem>"
    for o, modalidades in (("Latente", None), ("Receptáculo", ("Coexistência", "Conflito")),
                           ("Descendente", ("Zenin", "Kamo", "Gojo", "Inumaki")), ("Encarnado", None), ("Híbrido", None)):
        L = sec[o]
        filhos = dict(_secoes(L))
        menores_t = next(t for t in filhos if t.startswith("Menores d"))
        if modalidades:
            marc = [_marcante(m, filhos[m]) for m in modalidades]
        else:
            unica = [t for t in filhos if not t.startswith("Menores d")]
            marc = [_marcante(unica[0], filhos[unica[0]])]
        origens.append(entrada(o, o, L, marc, _menores(filhos[menores_t])))

    # o Corpo Amaldiçoado: a marcante comum, as oito gerais e as duas de Manutenção (uma história, não uma modalidade)
    L = sec["Corpo Amaldiçoado"]
    f = dict(_secoes(L))
    origens.append(entrada("Corpo Amaldiçoado", "Corpo Amaldiçoado", L,
                           [_marcante("Existência Artificial", f["Existência Artificial"])],
                           _menores(f["Menores do Corpo Amaldiçoado"]) + _menores(f["Menores de Manutenção"], "Manutenção"),
                           oficio=True, reparo=_corpo(f["Reparo do corpo"]), historias=_corpo(f["Histórias do corpo"])))

    # a Restrição Celestial, nos dois ramos: cada um com rota, marcante e catálogo
    L = sec["Restrição Celestial"]
    f = dict(_secoes(L))
    se = f["Sem Energia"]
    origens.append(entrada("Restrição Celestial · Sem Energia", "Restrição Celestial", se,
                           [_marcante("Ataque sem Prenúncio", f["Ataque sem Prenúncio"])],
                           _menores(f["Menores de Sem Energia"]), rota="Técnica Marcial, sem energia"))
    rc = f["Restrição corporal"]
    saida = _corpo(f["Saída Elevada"])
    corpos = [_marcante(c, f[c], "Saída Elevada.\n\n" + saida) for c in ("Corpo Debilitado", "Corpo Quebradiço", "Corpo Exaurido")]
    origens.append(entrada("Restrição Celestial · Restrição corporal", "Restrição Celestial", rc, corpos,
                           _menores(f["Menores da Restrição corporal"]), ce4=True, saida_elevada=saida,
                           ce4_texto=_corpo(f["Talento de Categoria de Efeito 4"])))

    n = sum(len(o["menores"]) for o in origens)
    if n != TOTAL_DE_MENORES:
        raise SystemExit(f"extrair_origens: o livro dá {TOTAL_DE_MENORES} menores, e achei {n}")
    st = sec["Sem Técnica"]
    pers = Lv.secao("Personalizar sua Origem", dentro=cap)
    return {
        "_meta": {"versao_do_livro": fonte["livro"], "sha256_do_livro": fonte["sha256"], "capitulo": CAPITULO,
                  "o_que_e": "as Origens do livro: a base, as marcantes e o catálogo de menores de cada uma, com o texto inteiro",
                  "extraido_por": "ficha-v01/extrair_origens.py"},
        "criada": CRIADA,
        "origens": origens,
        "sem_tecnica": _corpo(st),
        "personalizar": _corpo(pers),
        "legados_de_historia": _corpo(sec["Legados de história"]),
        "escolhas": _corpo(sec["Escolhas da Origem"]),
    }


if __name__ == "__main__":
    novo = extrai()
    if "--confere" in sys.argv:
        velho = json.load(open(SAIDA, encoding="utf-8"))
        igual = json.dumps(velho, ensure_ascii=False, sort_keys=True) == json.dumps(novo, ensure_ascii=False, sort_keys=True)
        print("o arquivo bate com o livro" if igual else "o arquivo NAO bate com o livro")
        sys.exit(0 if igual else 1)
    json.dump(novo, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{SAIDA}: {len(novo['origens'])} entradas de Origem, "
          f"{sum(len(o['marcantes']) for o in novo['origens'])} marcantes, {sum(len(o['menores']) for o in novo['origens'])} menores")
